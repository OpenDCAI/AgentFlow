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

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'DocAgent'))
try:
    from doc_reader import DocReader
except ImportError:
    DocReader = None

class BaseDocAgentTool:
    def __init__(self, doc_reader: Optional[DocReader] = None):
        self.doc_reader = doc_reader

    def set_doc_reader(self, doc_reader: DocReader):
        self.doc_reader = doc_reader

    def _check(self) -> Optional[str]:
        if DocReader is None:
            return f"[{self.__class__.__name__}] Error: DocAgent DocReader unavailable."
        if self.doc_reader is None:
            return f"[{self.__class__.__name__}] Error: DocReader not initialized."
        return None

def _clean_xml_string(xml_str: str) -> str:
    return "".join(c for c in xml_str if c.isprintable() or c.isspace())

def _format_xml_element(element: ET.Element) -> str:
    xml_string = ET.tostring(element, encoding="unicode", method="xml")
    xml_string = _clean_xml_string(xml_string)
    dom = xml.dom.minidom.parseString(xml_string)
    return dom.toprettyxml(indent="  ", newl="\n").split("\n", 1)[1]

def _parse_params(params: Union[str, dict]) -> dict:
    if isinstance(params, str):
        return json.loads(params)
    return params

class DocumentSearchTool(BaseDocAgentTool):
    name = "document_search"
    description = (
        "Search for keywords in the document. Returns matching sections, paragraphs, "
        "tables, and images with their locations (section_id, page_num)."
    )
    parameters = [
        {'name':'keyword','type':'string','description':'Keyword or phrase','required':True},
        {'name':'max_results','type':'integer','description':'Maximum results (default: 24)','required':False},
        {'name':'use_api','type':'boolean','description':'Optional summarize via API','required':False},
    ]
    def call(self, params: Union[str, dict], **kwargs) -> str:
        err = self._check()
        if err:
            return err
        try:
            parsed = _parse_params(params)
            if 'keyword' not in parsed or not parsed['keyword']:
                return f"[{self.__class__.__name__}] Error: 'keyword' parameter is required."
            keyword = parsed['keyword']
            max_results = parsed.get('max_results', 24)
            search_root = self.doc_reader.search(keyword)
            total = len(search_root)
            if total > max_results:
                for sub in list(search_root)[max_results:]:
                    search_root.remove(sub)
                header = f"Found {total} results for keyword '{keyword}'. Showing first {max_results} results:\n\n"
            else:
                header = f"Found {total} results for keyword '{keyword}':\n\n"
            xml_string = _format_xml_element(search_root)
            return header + xml_string
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"

class DocumentGetSectionTool(BaseDocAgentTool):
    name = "document_get_section"
    description = "Get the full text content of a specific section by section_id."
    parameters = [
        {'name':'section_id','type':'string','description':'Section ID','required':True},
    ]
    def call(self, params: Union[str, dict], **kwargs) -> str:
        err = self._check()
        if err:
            return err
        try:
            parsed = _parse_params(params)
            if 'section_id' not in parsed or not parsed['section_id']:
                return f"[{self.__class__.__name__}] Error: 'section_id' parameter is required."
            section_id = str(parsed['section_id'])
            if section_id not in self.doc_reader.section_dict:
                ids = list(self.doc_reader.section_dict.keys())[:10]
                return (
                    f"[{self.__class__.__name__}] Error: Section ID '{section_id}' not found. "
                    f"Available section IDs (showing first 10): {ids}."
                )
            section_root = self.doc_reader.get_section_content(section_id)
            xml_string = _format_xml_element(section_root)
            if len(xml_string) > 30000:
                xml_string = xml_string[:30000] + "\n... [Content truncated.]"
                header = f"Section {section_id} content (truncated):\n\n"
            else:
                header = f"Full content of Section {section_id}:\n\n"
            return header + xml_string
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"

class DocumentGetOutlineTool(BaseDocAgentTool):
    name = "document_get_outline"
    description = "Get the document outline showing hierarchical structure."
    parameters = [
        {'name':'skip_para_after_page','type':'integer','description':'Skip paragraphs after this page','required':False},
    ]
    def call(self, params: Union[str, dict], **kwargs) -> str:
        err = self._check()
        if err:
            return err
        try:
            parsed = _parse_params(params)
            skip_para_after_page = parsed.get('skip_para_after_page', 100)
            outline_root = self.doc_reader.get_outline_root(skip_para_after_page=skip_para_after_page)
            xml_string = _format_xml_element(outline_root)
            return f"Document Outline:\n\n{xml_string}"
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"

def _encode_file_to_base64(file_path: str) -> Tuple[str, str, Optional[str]]:
    if not os.path.exists(file_path):
        return "", "", f"File not found: {file_path}"
    media_type, _ = mimetypes.guess_type(file_path)
    if media_type is None:
        return "", "", f"Unsupported file type for: {file_path}"
    try:
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return media_type, encoded, None
    except Exception as exc:
        return "", "", f"Failed to read file {file_path}: {exc}"

class DocumentGetPageImageTool(BaseDocAgentTool):
    name = "document_get_page_image"
    description = "Get page images as base64-encoded strings."
    parameters = [
        {'name':'page_num','type':'integer','description':'1-indexed page number','required':True},
    ]
    def call(self, params: Union[str, dict], **kwargs) -> str:
        err = self._check()
        if err:
            return err
        try:
            parsed = _parse_params(params)
            if 'page_num' not in parsed:
                return f"[{self.__class__.__name__}] Error: 'page_num' parameter is required."
            page_num = int(parsed['page_num'])
            if page_num < 1:
                return f"[{self.__class__.__name__}] Error: page_num must be >= 1."
            idx = f"page_{page_num - 1:04d}.png"
            root = getattr(self.doc_reader, 'page_images_dir', None)
            if not root:
                return f"[{self.__class__.__name__}] Error: Page images directory not configured."
            candidate = os.path.join(root, idx)
            media_type, base64_image, error = _encode_file_to_base64(candidate)
            if error:
                return f"[{self.__class__.__name__}] Error: {error}"
            return (
                f"[{self.__class__.__name__}] Successfully retrieved page {page_num} image.\n"
                f"Media type: {media_type}\n"
                f"Base64 data length: {len(base64_image)} characters\n"
                f"Base64 data: {base64_image[:100]}...\n\n"
                "Note: Full base64 image data is available."
            )
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"

class DocumentGetImageTool(BaseDocAgentTool):
    name = "document_get_image"
    description = "Get a specific image by image_id."
    parameters = [
        {'name':'image_id','type':'string','description':'Image ID','required':True},
    ]
    def call(self, params: Union[str, dict], **kwargs) -> str:
        err = self._check()
        if err:
            return err
        try:
            parsed = _parse_params(params)
            if 'image_id' not in parsed or not parsed['image_id']:
                return f"[{self.__class__.__name__}] Error: 'image_id' parameter is required."
            image_id = str(parsed['image_id'])
            figures_dir = getattr(self.doc_reader, 'figures_dir', None)
            image_map = getattr(self.doc_reader, 'image_path_dict', {})
            if image_id not in image_map:
                ids = list(image_map.keys())[:10]
                return f"[{self.__class__.__name__}] Error: Image ID '{image_id}' not found. Available: {ids}."
            file_name = image_map.get(image_id)
            image_path = os.path.join(figures_dir, file_name)
            media_type, base64_image, error = _encode_file_to_base64(image_path)
            if error:
                return f"[{self.__class__.__name__}] Error: {error}"
            return (
                f"[{self.__class__.__name__}] Successfully retrieved image {image_id}.\n"
                f"Media type: {media_type}\n"
                f"Base64 data length: {len(base64_image)} characters\n"
                f"Base64 data: {base64_image[:100]}...\n\n"
                "Note: Full base64 image data is available."
            )
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"

class DocumentGetTableImageTool(BaseDocAgentTool):
    name = "document_get_table_image"
    description = "Get a table image by table_id."
    parameters = [
        {'name':'table_id','type':'string','description':'Table ID','required':True},
    ]
    def call(self, params: Union[str, dict], **kwargs) -> str:
        err = self._check()
        if err:
            return err
        try:
            parsed = _parse_params(params)
            if 'table_id' not in parsed or not parsed['table_id']:
                return f"[{self.__class__.__name__}] Error: 'table_id' parameter is required."
            table_id = str(parsed['table_id'])
            tables_dir = getattr(self.doc_reader, 'tables_dir', None)
            table_map = getattr(self.doc_reader, 'table_image_path_dict', {})
            if table_id not in table_map:
                ids = list(table_map.keys())[:10]
                return f"[{self.__class__.__name__}] Error: Table ID '{table_id}' doesn't have an image. Available: {ids}."
            file_name = table_map.get(table_id)
            table_path = os.path.join(tables_dir, file_name)
            media_type, base64_image, error = _encode_file_to_base64(table_path)
            if error:
                return f"[{self.__class__.__name__}] Error: {error}"
            return (
                f"[{self.__class__.__name__}] Successfully retrieved table {table_id} image.\n"
                f"Media type: {media_type}\n"
                f"Base64 data length: {len(base64_image)} characters\n"
                f"Base64 data: {base64_image[:100]}...\n\n"
                "Note: Full base64 image data is available."
            )
        except Exception as e:
            return f"[{self.__class__.__name__}] Error: {str(e)}"

