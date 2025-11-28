"""
Document tools for AgentFlow - Multi-modal document understanding tools based on DocAgent.

These tools provide capabilities for:
- Searching documents by keywords
- Retrieving document sections
- Getting document outlines
- Accessing page images, figures, and table images
"""

import sys
import os
import json
import copy
import base64
import mimetypes
import re
from typing import Union, Dict, Any, Optional, Tuple
import xml.etree.ElementTree as ET
import xml.dom.minidom
import openai

# Add DocAgent to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'DocAgent'))

try:
    from doc_reader import DocReader
except ImportError:
    DocReader = None


# ============================================================================
# Case Data Adapter (XML/Case assets fallback)
# ============================================================================

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CASE_DIR = os.path.join(REPO_ROOT, "case")
CASE_XML_DIR = os.path.join(CASE_DIR, "test_xml")
CASE_OUTPUT_DIR = os.path.join(CASE_DIR, "test_output")
CASE_PDF_DIR = os.path.join(CASE_DIR, "test_PDF")


def _encode_file_to_base64(file_path: str) -> Tuple[str, str, Optional[str]]:
    """Read a file and return (media_type, base64_string, error)."""
    if not os.path.exists(file_path):
        return "", "", f"File not found: {file_path}"
    
    media_type, _ = mimetypes.guess_type(file_path)
    if media_type is None:
        return "", "", f"Unsupported file type for: {file_path}"
    
    try:
        with open(file_path, "rb") as file_obj:
            encoded = base64.b64encode(file_obj.read()).decode("utf-8")
        return media_type, encoded, None
    except Exception as exc:
        return "", "", f"Failed to read file {file_path}: {exc}"


def _safe_float(value: Optional[str]) -> Optional[float]:
    """Convert a string to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class CaseDocumentAdapter:
    """
    Lightweight adapter that mimics DocReader APIs using pre-generated XML and assets
    placed under the repository's `case/` directory.
    """
    
    def __init__(self):
        self.outline_path = os.environ.get(
            "AGENTFLOW_OUTLINE_PATH",
            self._detect_outline_path()
        )
        self.document_root = os.environ.get(
            "AGENTFLOW_DOCUMENT_ROOT",
            self._detect_document_root()
        )
        self.case_doc_id = os.environ.get(
            "AGENTFLOW_CASE_DOC_ID",
            os.path.basename(self.document_root) if self.document_root else None
        )
        
        self.figures_dir = (
            os.path.join(self.document_root, "figures")
            if self.document_root else None
        )
        self.tables_dir = (
            os.path.join(self.document_root, "tables")
            if self.document_root else None
        )
        self.page_images_dir = (
            os.path.join(self.document_root, "page_images")
            if self.document_root else None
        )
        self.docagent_root = None
        if self.case_doc_id:
            da = os.path.join(REPO_ROOT, "DocAgent", "preprocess", "processed_output", self.case_doc_id)
            if os.path.isdir(da):
                self.docagent_root = da
                if not self.page_images_dir:
                    cand = os.path.join(da, "page_images")
                    if os.path.isdir(cand):
                        self.page_images_dir = cand
        self.pdf_path = None
        if self.case_doc_id:
            candidate_pdf = os.path.join(CASE_PDF_DIR, f"{self.case_doc_id}.pdf")
            if os.path.exists(candidate_pdf):
                self.pdf_path = candidate_pdf
        
        self.root: Optional[ET.Element] = None
        self.section_dict: Dict[str, ET.Element] = {}
        self.image_path_dict: Dict[str, str] = {}
        self.table_image_path_dict: Dict[str, str] = {}
        self.num_page: int = 0
        self.json_page_map: Dict[int, list] = {}
        self.json_path: Optional[str] = None
        
        self._load_outline()
        self._index_assets()
        self._load_json()
    
    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------
    
    @staticmethod
    def _detect_outline_path() -> Optional[str]:
        if os.path.isdir(CASE_XML_DIR):
            xml_files = [
                os.path.join(CASE_XML_DIR, name)
                for name in os.listdir(CASE_XML_DIR)
                if name.lower().endswith(".xml")
            ]
            if xml_files:
                return xml_files[0]
        # fallback: search outline_result.xml under test_output/*/
        if os.path.isdir(CASE_OUTPUT_DIR):
            for name in sorted(os.listdir(CASE_OUTPUT_DIR)):
                candidate = os.path.join(CASE_OUTPUT_DIR, name, "outline_result.xml")
                if os.path.isfile(candidate):
                    return candidate
        return None
    
    @staticmethod
    def _detect_document_root() -> Optional[str]:
        if not os.path.isdir(CASE_OUTPUT_DIR):
            return None
        for candidate in sorted(os.listdir(CASE_OUTPUT_DIR)):
            candidate_path = os.path.join(CASE_OUTPUT_DIR, candidate)
            if os.path.isdir(candidate_path) and os.path.exists(
                os.path.join(candidate_path, "data.pkl")
            ):
                return candidate_path
        return None
    
    # ------------------------------------------------------------------
    # Loading & indexing
    # ------------------------------------------------------------------
    
    def _load_outline(self):
        if not self.outline_path or not os.path.exists(self.outline_path):
            return
        tree = ET.parse(self.outline_path)
        self.root = tree.getroot()
        
        for section in self.root.iter("Section"):
            section_id = section.get("section_id")
            if section_id:
                self.section_dict[section_id] = section
                start_page = _safe_float(section.get("start_page_num"))
                end_page = _safe_float(section.get("end_page_num"))
                page_candidates = [
                    value for value in [start_page, end_page] if value is not None
                ]
                if page_candidates:
                    self.num_page = max(
                        self.num_page,
                        int(max(page_candidates))
                    )
        
        # Ensure num_page is at least 1 if outline exists
        if self.root is not None and self.num_page == 0:
            self.num_page = 1
    
    def _index_assets(self):
        if self.figures_dir and os.path.isdir(self.figures_dir):
            for name in os.listdir(self.figures_dir):
                match = re.match(r"image_(\d+)\.", name)
                if match:
                    self.image_path_dict[match.group(1)] = name
        
        if self.tables_dir and os.path.isdir(self.tables_dir):
            for name in os.listdir(self.tables_dir):
                match = re.match(r"table_(\d+)\.", name)
                if match:
                    self.table_image_path_dict[match.group(1)] = name
    
    def _load_json(self):
        if not self.case_doc_id or not self.document_root:
            return
        cand = os.path.join(self.document_root, f"{self.case_doc_id}.json")
        if not os.path.isfile(cand):
            return
        self.json_path = cand
        try:
            with open(cand, "r", encoding="utf-8") as f:
                data = json.load(f)
            cur = None
            for entry in data:
                style = entry.get("style")
                para = entry.get("para_text")
                if style == "Page_number":
                    try:
                        cur = int(str(para).strip())
                    except Exception:
                        cur = cur
                    continue
                if cur is None:
                    continue
                text = ""
                if isinstance(para, dict):
                    text = para.get("alt_text") or para.get("content") or ""
                else:
                    text = para or ""
                if text:
                    self.json_page_map.setdefault(cur, []).append(text)
        except Exception:
            self.json_page_map = {}
    
    # ------------------------------------------------------------------
    # DocReader-compatible APIs
    # ------------------------------------------------------------------
    
    @property
    def is_available(self) -> bool:
        return self.root is not None
    
    def get_outline_root(
        self,
        skip_para_after_page: int = 100,
        disable_caption_after_page: bool = False
    ) -> ET.Element:
        if not self.root:
            raise RuntimeError("Outline XML not loaded")
        
        root_copy = copy.deepcopy(self.root)
        for parent in root_copy.iter():
            for child in list(parent):
                if child.tag == "Paragraph":
                    page_value = _safe_float(child.get("page_num"))
                    if (
                        page_value is not None
                        and page_value > skip_para_after_page
                    ):
                        parent.remove(child)
                elif child.tag == "Image" and disable_caption_after_page:
                    page_value = _safe_float(child.get("page_num"))
                    if (
                        page_value is not None
                        and page_value > disable_caption_after_page
                    ):
                        for sub_child in child:
                            if sub_child.tag == "Caption" and sub_child.text:
                                sub_child.text = sub_child.text[:20]
        root_copy.tag = "Outline"
        return root_copy
    
    def get_section_content(self, section_id: str) -> ET.Element:
        if section_id not in self.section_dict:
            raise KeyError(section_id)
        return copy.deepcopy(self.section_dict[section_id])
    
    def search(self, keyword: str) -> ET.Element:
        if not self.root:
            raise RuntimeError("Outline XML not loaded")
        
        keyword = keyword.lower()
        result_root = ET.Element("Search_Result")
        
        def traverse(node: ET.Element, current_section_id: str = ""):
            next_section_id = current_section_id
            if node.tag == "Section":
                next_section_id = node.get("section_id", current_section_id)
                heading_text = ""
                for child in node:
                    if child.tag == "Heading":
                        heading_text = child.text or ""
                        break
                if heading_text and keyword in heading_text.lower():
                    item = ET.SubElement(
                        result_root,
                        "Item",
                        type="Section",
                        section_id=next_section_id,
                        page_num=node.get("start_page_num", "")
                    )
                    item.text = heading_text
                for child in node:
                    traverse(child, next_section_id)
                return
            
            if node.tag in ("Paragraph", "CSV_Table"):
                text_value = node.get("first_sentence") or node.text or ""
                if text_value and keyword in text_value.lower():
                    item = ET.SubElement(
                        result_root,
                        "Item",
                        type=node.tag,
                        section_id=current_section_id,
                        page_num=node.get("page_num", "")
                    )
                    item.text = text_value
            elif node.tag == "Image":
                image_id = node.get("image_id", "")
                texts = [child.text or "" for child in node]
                if any(keyword in text.lower() for text in texts if text):
                    item = ET.SubElement(
                        result_root,
                        "Image",
                        type="Image",
                        image_id=image_id,
                        section_id=current_section_id,
                        page_num=node.get("page_num", "")
                    )
                    for child in node:
                        sub_item = ET.SubElement(item, child.tag)
                        sub_item.text = child.text
            else:
                for child in node:
                    traverse(child, current_section_id)
        
        traverse(self.root)
        if self.json_page_map:
            allowed_pages = sorted(self.json_page_map.keys())
            for p in allowed_pages:
                texts = self.json_page_map.get(p, [])
                for t in texts:
                    if isinstance(t, str) and keyword in t.lower():
                        item = ET.SubElement(
                            result_root,
                            "Item",
                            type="JSON",
                            section_id="",
                            page_num=str(float(p))
                        )
                        item.text = t
        return result_root
    
    def get_image(self, image_id: str) -> Tuple[str, str, Optional[str]]:
        if not self.figures_dir:
            return "", "", "Figures directory not configured."
        
        file_name = self.image_path_dict.get(image_id)
        if not file_name:
            # fall back to default naming convention
            file_name = f"image_{image_id}.png"
        image_path = os.path.join(self.figures_dir, file_name)
        return _encode_file_to_base64(image_path)
    
    def get_table_image(self, table_id: str) -> Tuple[str, str, Optional[str]]:
        if not self.tables_dir:
            return "", "", "Tables directory not configured."
        
        file_name = self.table_image_path_dict.get(table_id)
        if not file_name:
            file_name = f"table_{table_id}.png"
        table_path = os.path.join(self.tables_dir, file_name)
        return _encode_file_to_base64(table_path)
    
    def get_page_image(self, page_num: int) -> Tuple[str, str, Optional[str]]:
        if self.page_images_dir:
            index_string = f"page_{page_num - 1:04d}.png"
            candidate = os.path.join(self.page_images_dir, index_string)
            if os.path.exists(candidate):
                return _encode_file_to_base64(candidate)
        
        if self.pdf_path:
            return (
                "",
                "",
                f"Page images are unavailable. Refer to PDF at {self.pdf_path} "
                "or generate page images under the document root."
            )
        
        return (
            "",
            "",
            "Page images are unavailable for the fallback case document."
        )


_CASE_ADAPTER: Optional[CaseDocumentAdapter] = None
_CASE_ADAPTER_INITIALIZED = False


def get_case_document_adapter() -> Optional[CaseDocumentAdapter]:
    """Lazily initialize and cache the case document adapter."""
    global _CASE_ADAPTER, _CASE_ADAPTER_INITIALIZED
    if _CASE_ADAPTER_INITIALIZED:
        return _CASE_ADAPTER
    
    _CASE_ADAPTER_INITIALIZED = True
    try:
        adapter = CaseDocumentAdapter()
        if adapter.is_available:
            _CASE_ADAPTER = adapter
    except Exception as exc:
        print(f"[DocumentTools] Warning: failed to initialize case adapter: {exc}")
        _CASE_ADAPTER = None
    return _CASE_ADAPTER


# ============================================================================
# Utility Functions
# ============================================================================

def clean_xml_string(xml_str: str) -> str:
    """Clean XML string for better formatting."""
    cleaned = "".join(char for char in xml_str if char.isprintable() or char.isspace())
    return cleaned


def format_xml_element(element: ET.Element) -> str:
    """
    Convert XML element to formatted string.
    
    Args:
        element: XML element to format
        
    Returns:
        Formatted XML string
    """
    xml_string = ET.tostring(element, encoding="unicode", method="xml")
    xml_string = clean_xml_string(xml_string)
    dom = xml.dom.minidom.parseString(xml_string)
    xml_string = dom.toprettyxml(indent="  ", newl="\n").split("\n", 1)[1]
    return xml_string


def parse_params(params: Union[str, dict]) -> dict:
    """
    Parse parameters from string or dict.
    
    Args:
        params: Parameters as string (JSON) or dict
        
    Returns:
        Parsed parameters as dict
    """
    if isinstance(params, str):
        return json.loads(params)
    return params


def _call_openai_summary(prompt: str) -> Optional[str]:
    try:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", ""))
        if not api_key or not base_url:
            return None
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":prompt}],
            temperature=0.0,
            max_tokens=200
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


# ============================================================================
# Base Document Tool Class
# ============================================================================

class BaseDocumentTool:
    """
    Base class for all document tools.
    
    Provides common functionality:
    - DocReader initialization and validation
    - Parameter parsing
    - Error handling
    """
    
    def __init__(self, doc_reader: Optional[DocReader] = None):
        """
        Initialize the document tool.
        
        Args:
            doc_reader: DocReader instance. If None, must be set via set_doc_reader().
        """
        self.doc_reader = doc_reader
    
    def _get_data_provider(self):
        """
        Return the active data provider (DocReader or fallback adapter).
        """
        if self.doc_reader is not None:
            return self.doc_reader
        return get_case_document_adapter()
    
    def set_doc_reader(self, doc_reader: DocReader):
        """Set the DocReader instance."""
        self.doc_reader = doc_reader
    
    def _check_doc_reader(self) -> Optional[str]:
        """
        Check if DocReader is available and initialized.
        
        Returns:
            Error message if check fails, None otherwise
        """
        provider = self._get_data_provider()
        if provider is not None:
            return None
        
        if DocReader is None:
            return (
                f"[{self.__class__.__name__}] Error: No document provider available. "
                "Ensure DocAgent is installed or place fallback assets under the case/ directory."
            )
        
        if self.doc_reader is None:
            return (
                f"[{self.__class__.__name__}] Error: DocReader not initialized. "
                "Set doc_reader or configure the case/ fallback assets."
            )
        
        return None
    
    def _parse_and_validate_params(self, params: Union[str, dict], required_params: list) -> Tuple[Optional[dict], Optional[str]]:
        """
        Parse and validate parameters.
        
        Args:
            params: Parameters as string or dict
            required_params: List of required parameter names
            
        Returns:
            Tuple of (parsed_params, error_message). If error, params is None.
        """
        try:
            parsed_params = parse_params(params)
            
            # Check required parameters
            for param_name in required_params:
                if param_name not in parsed_params or not parsed_params[param_name]:
                    return None, f"[{self.__class__.__name__}] Error: '{param_name}' parameter is required."
            
            return parsed_params, None
            
        except json.JSONDecodeError as e:
            return None, f"[{self.__class__.__name__}] Error: Invalid JSON parameters: {str(e)}"
        except Exception as e:
            return None, f"[{self.__class__.__name__}] Error: Failed to parse parameters: {str(e)}"


# ============================================================================
# Document Tools
# ============================================================================

class DocumentSearchTool(BaseDocumentTool):
    """
    Tool for searching keywords in documents.
    
    This tool searches for keywords across the entire document including:
    - Section headings
    - Paragraphs
    - Tables
    - Image captions and alt text
    """
    
    name = "document_search"
    description = (
        "Search for keywords in the document. Returns matching sections, paragraphs, "
        "tables, and images with their locations (section_id, page_num). "
        "Use this tool to quickly locate relevant content before reading detailed sections."
    )
    parameters = [
        {
            'name': 'keyword',
            'type': 'string',
            'description': 'The keyword or phrase to search for in the document',
            'required': True
        },
        {
            'name': 'max_results',
            'type': 'integer',
            'description': 'Maximum number of results to return (default: 24)',
            'required': False
        },
        {
            'name': 'use_api',
            'type': 'boolean',
            'description': 'Optionally summarize matches via API (default: False)',
            'required': False
        }
    ]
    
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the search tool."""
        # Check DocReader availability
        error = self._check_doc_reader()
        if error:
            return error
        
        provider = self._get_data_provider()
        if provider is None:
            return f"[{self.__class__.__name__}] Error: No document provider available."
        
        # Parse and validate parameters
        parsed_params, error = self._parse_and_validate_params(params, ["keyword"])
        if error:
            return error
        
        try:
            keyword = parsed_params["keyword"]
            max_results = parsed_params.get("max_results", 24)
            use_api = parsed_params.get("use_api", False)
            
            # Perform search
            search_root = provider.search(keyword)
            total_results = len(search_root)
            
            # Limit results
            if total_results > max_results:
                for subelement in list(search_root)[max_results:]:
                    search_root.remove(subelement)
                result_text = (
                    f"Found {total_results} results for keyword '{keyword}'. "
                    f"Showing first {max_results} results:\n\n"
                )
            else:
                result_text = f"Found {total_results} results for keyword '{keyword}':\n\n"
            
            # Format XML
            xml_string = format_xml_element(search_root)
            summary = None
            if use_api:
                snippets = []
                for it in list(search_root)[:min(max_results, 8)]:
                    txt = (it.text or "").strip()
                    if txt:
                        snippets.append(txt)
                if snippets:
                    prompt = "Summarize key points concisely from these document snippets:\n\n" + "\n".join(f"- {s}" for s in snippets)
                    summary = _call_openai_summary(prompt)
            return result_text + xml_string + ("\n\nAPI Summary:\n" + summary if summary else "")
            
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"


class DocumentGetSectionTool(BaseDocumentTool):
    """
    Tool for retrieving full content of a document section.
    
    This tool returns the complete text content of a specified section including:
    - Section heading
    - All paragraphs
    - Tables (CSV format)
    - Image references
    """
    
    name = "document_get_section"
    description = (
        "Get the full text content of a specific section by section_id. "
        "Use section_id from the document outline or search results. "
        "Returns XML format with all paragraphs, tables, and images in that section."
    )
    parameters = [
        {
            'name': 'section_id',
            'type': 'string',
            'description': 'The section ID (e.g., "1", "1.1", "2.3.1") to retrieve',
            'required': True
        }
    ]
    
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the get section tool."""
        # Check DocReader availability
        error = self._check_doc_reader()
        if error:
            return error
        
        provider = self._get_data_provider()
        if provider is None:
            return f"[{self.__class__.__name__}] Error: No document provider available."
        
        # Parse and validate parameters
        parsed_params, error = self._parse_and_validate_params(params, ["section_id"])
        if error:
            return error
        
        try:
            section_id = str(parsed_params["section_id"])
            
            # Check if section exists
            section_dict = getattr(provider, "section_dict", {})
            if section_id not in section_dict:
                available_ids = list(section_dict.keys())[:10]
                return (
                    f"[{self.__class__.__name__}] Error: Section ID '{section_id}' not found. "
                    f"Available section IDs (showing first 10): {available_ids}. "
                    "Use document_get_outline to see all sections."
                )
            
            # Get section content
            section_root = provider.get_section_content(section_id)
            
            # Format XML
            xml_string = format_xml_element(section_root)
            
            # Truncate if too long
            MAX_LENGTH = 30000
            if len(xml_string) > MAX_LENGTH:
                xml_string = (
                    xml_string[:MAX_LENGTH] + 
                    "\n... [Content truncated. The section is too long. Try to get content from sub-sections.]"
                )
                result_text = f"Section {section_id} content (truncated):\n\n"
            else:
                result_text = f"Full content of Section {section_id}:\n\n"
            
            return result_text + xml_string
            
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"


class DocumentGetOutlineTool(BaseDocumentTool):
    """
    Tool for retrieving document outline/structure.
    
    This tool returns the hierarchical structure of the document including:
    - All section headings with their IDs
    - First sentence of each paragraph
    - Table and image references
    """
    
    name = "document_get_outline"
    description = (
        "Get the document outline showing the hierarchical structure with all sections, "
        "headings, and a brief preview of content. Use this to understand the document "
        "structure and find relevant section_ids before reading detailed content."
    )
    parameters = [
        {
            'name': 'skip_para_after_page',
            'type': 'integer',
            'description': 'Skip paragraphs after this page number to shorten outline (default: 100)',
            'required': False
        }
    ]
    
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the get outline tool."""
        # Check DocReader availability
        error = self._check_doc_reader()
        if error:
            return error
        
        try:
            parsed_params = parse_params(params)
            skip_para_after_page = parsed_params.get("skip_para_after_page", 100)
            
            # Get outline
            provider = self._get_data_provider()
            if provider is None:
                return f"[{self.__class__.__name__}] Error: No document provider available."
            
            outline_root = provider.get_outline_root(
                skip_para_after_page=skip_para_after_page
            )
            
            # Format and return XML
            xml_string = format_xml_element(outline_root)
            return f"Document Outline:\n\n{xml_string}"
            
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"


class DocumentGetPageImageTool(BaseDocumentTool):
    """
    Tool for retrieving page images from the document.
    
    This tool returns page images as base64-encoded strings that can be used
    for visual understanding of the document layout and content.
    """
    
    name = "document_get_page_image"
    description = (
        "Get page images from the document for visual understanding. "
        "Returns base64-encoded images. Use this to see the visual layout, "
        "charts, diagrams, or any visual content on specific pages."
    )
    parameters = [
        {
            'name': 'page_num',
            'type': 'integer',
            'description': 'The page number to retrieve (1-indexed)',
            'required': True
        }
    ]
    
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the get page image tool."""
        # Check DocReader availability
        error = self._check_doc_reader()
        if error:
            return error
        
        provider = self._get_data_provider()
        if provider is None:
            return f"[{self.__class__.__name__}] Error: No document provider available."
        
        # Parse and validate parameters
        parsed_params, error = self._parse_and_validate_params(params, ["page_num"])
        if error:
            return error
        
        try:
            page_num = int(parsed_params["page_num"])
            
            # Validate page number
            if page_num < 1:
                return f"[{self.__class__.__name__}] Error: page_num must be >= 1."
            
            max_page = getattr(provider, "num_page", 0)
            if page_num > max_page and max_page > 0:
                return (
                    f"[{self.__class__.__name__}] Error: page_num ({page_num}) exceeds "
                    f"maximum page number ({max_page})."
                )
            
            # Get page image
            media_type, base64_image, error = provider.get_page_image(page_num)
            
            if error is not None:
                return f"[{self.__class__.__name__}] Error: {error}"
            
            # Return base64 image (note: AgentFlow tools return strings, so we return the base64 data)
            # The caller can use this base64 data to display images
            return (
                f"[{self.__class__.__name__}] Successfully retrieved page {page_num} image.\n"
                f"Media type: {media_type}\n"
                f"Base64 data length: {len(base64_image)} characters\n"
                f"Base64 data: {base64_image[:100]}...\n\n"
                "Note: Full base64 image data is available. Use this for visual understanding."
            )
            
        except ValueError as e:
            return f"[{self.__class__.__name__}] Error: Invalid page_num format: {str(e)}"
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"


class DocumentGetImageTool(BaseDocumentTool):
    """
    Tool for retrieving specific images from the document.
    
    This tool returns images (figures, charts, diagrams) embedded in the document
    as base64-encoded strings.
    """
    
    name = "document_get_image"
    description = (
        "Get a specific image from the document by image_id. "
        "Use image_id from search results or section content. "
        "Returns base64-encoded image for visual understanding."
    )
    parameters = [
        {
            'name': 'image_id',
            'type': 'string',
            'description': 'The image ID to retrieve (e.g., "0", "1", "2")',
            'required': True
        }
    ]
    
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the get image tool."""
        # Check DocReader availability
        error = self._check_doc_reader()
        if error:
            return error
        
        provider = self._get_data_provider()
        if provider is None:
            return f"[{self.__class__.__name__}] Error: No document provider available."
        
        # Parse and validate parameters
        parsed_params, error = self._parse_and_validate_params(params, ["image_id"])
        if error:
            return error
        
        try:
            image_id = str(parsed_params["image_id"])
            
            # Check if image exists
            image_dict = getattr(provider, "image_path_dict", {})
            if image_id not in image_dict:
                available_ids = list(image_dict.keys())[:10]
                return (
                    f"[{self.__class__.__name__}] Error: Image ID '{image_id}' not found. "
                    f"Available image IDs (showing first 10): {available_ids}."
                )
            
            # Get image
            media_type, base64_image, error = provider.get_image(image_id)
            
            if error is not None:
                return f"[{self.__class__.__name__}] Error: {error}"
            
            return (
                f"[{self.__class__.__name__}] Successfully retrieved image {image_id}.\n"
                f"Media type: {media_type}\n"
                f"Base64 data length: {len(base64_image)} characters\n"
                f"Base64 data: {base64_image[:100]}...\n\n"
                "Note: Full base64 image data is available. Use this for visual understanding."
            )
            
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"


class DocumentGetTableImageTool(BaseDocumentTool):
    """
    Tool for retrieving table images from the document.
    
    This tool returns table screenshots as base64-encoded strings,
    useful for verifying table content or understanding table layout.
    """
    
    name = "document_get_table_image"
    description = (
        "Get a table image (screenshot) from the document by table_id. "
        "Use table_id from search results or section content. "
        "Returns base64-encoded table image for visual verification."
    )
    parameters = [
        {
            'name': 'table_id',
            'type': 'string',
            'description': 'The table ID to retrieve (e.g., "0", "1", "2")',
            'required': True
        }
    ]
    
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the get table image tool."""
        # Check DocReader availability
        error = self._check_doc_reader()
        if error:
            return error
        
        provider = self._get_data_provider()
        if provider is None:
            return f"[{self.__class__.__name__}] Error: No document provider available."
        
        # Parse and validate parameters
        parsed_params, error = self._parse_and_validate_params(params, ["table_id"])
        if error:
            return error
        
        try:
            table_id = str(parsed_params["table_id"])
            
            # Check if table image exists
            table_dict = getattr(provider, "table_image_path_dict", {})
            if table_id not in table_dict:
                available_ids = list(table_dict.keys())[:10]
                return (
                    f"[{self.__class__.__name__}] Error: Table ID '{table_id}' doesn't have an image. "
                    f"Available table IDs with images (showing first 10): {available_ids}."
                )
            
            # Get table image
            media_type, base64_image, error = provider.get_table_image(table_id)
            
            if error is not None:
                return f"[{self.__class__.__name__}] Error: {error}"
            
            return (
                f"[{self.__class__.__name__}] Successfully retrieved table {table_id} image.\n"
                f"Media type: {media_type}\n"
                f"Base64 data length: {len(base64_image)} characters\n"
                f"Base64 data: {base64_image[:100]}...\n\n"
                "Note: Full base64 image data is available. Use this for visual verification."
            )
            
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"
