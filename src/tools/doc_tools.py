import os
import json
import shutil
import sys
from typing import Union, List, Dict, Any, Optional
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path

import base64


from openai import OpenAI
from .mineru_vl_utils import MinerUClient

import json
from typing import Dict, List, Any, Union
from pathlib import Path


import os

DEFAULT_OUTPUT_ROOT = Path(
    os.environ.get('ocr-output-root') or
    os.environ.get('OCR_OUTPUT_ROOT') or
    "src/data/doc_demo/output"
)
DEFAULT_PDF_DIR = Path(
    os.environ.get('pdf-root') or
    os.environ.get('PDF_ROOT') or
    "src/data/doc_demo/PDF"
)
DEFAULT_TEMP_DIR = Path(
    os.environ.get('temp-output-root') or
    os.environ.get('TEMP_OUTPUT_ROOT') or
    "src/data/doc_demo/temp"
)

class DocCheckTool:
    """
    A tool to check the OCR parsing status of PDF files within a directory.
    It checks if the corresponding OCR JSON files exist in the output root directory.
    """
    name = "doc_check_tool"
    description = "Checks if a document (by base name, e.g., report_1) or all PDFs have been converted to structured JSON (OCR) format. THIS MUST BE THE FIRST TOOL CALLED FOR ANY NEW DOCUMENT QUERY."
    
    parameters = [
        {
            'name': 'file_name_or_all',
            'type': 'string',
            'description': 'The base name of a specific document (without .pdf) to check, or "all" to check all PDFs in the configured PDF directory.',
            'required': True
        }
    ]

    def _get_pdf_files_to_check(self, file_name_or_all: str, pdf_dir_path: Path) -> List[Path]:
        """Gets the list of PDF files based on input 'all' or specific file name."""
        if file_name_or_all.lower() == 'all':
            # Check all PDF files (case-insensitive glob)
            return list(pdf_dir_path.glob('*.pdf')) + list(pdf_dir_path.glob('*.PDF'))
        else:
            # Check a specific file (handle case-insensitivity)
            target_path_lower = pdf_dir_path / f"{file_name_or_all}.pdf"
            target_path_upper = pdf_dir_path / f"{file_name_or_all}.PDF"
            
            paths = []
            if target_path_lower.exists():
                paths.append(target_path_lower)
            if target_path_upper.exists() and target_path_lower != target_path_upper:
                paths.append(target_path_upper)
            
            return paths

    def call(self, params: Union[str, dict], **kwargs) -> Dict[str, Any]:
        """
        Executes the document check.
        """
        error_template = {"status": False, "files_to_process": [], "message": ""}
        
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return {**error_template, "message": "Error: Input parameters are not valid JSON."}

        file_name_or_all = params.get('file_name_or_all')
        
        if not file_name_or_all:
            return {**error_template, "message": "Error: 'file_name_or_all' is required."}
        
        pdf_dir_path = DEFAULT_PDF_DIR
        output_root_path = DEFAULT_OUTPUT_ROOT

        if not pdf_dir_path.is_dir():
            return {**error_template, "message": f"Error: PDF directory not found at {pdf_dir_path.resolve()}"}
        
        output_root_path.mkdir(parents=True, exist_ok=True) 

        pdf_files = self._get_pdf_files_to_check(file_name_or_all, pdf_dir_path)
        
        if not pdf_files:
            # Allow workflows that only rely on pre-generated OCR JSON (e.g., when PDFs live elsewhere).
            expected_json_path = output_root_path / f"{file_name_or_all}.json" if file_name_or_all.lower() == 'all' else output_root_path / f"{file_name_or_all}_ocr.json"
            if file_name_or_all.lower() != 'all' and expected_json_path.exists():
                return {
                    "status": True,
                    "files_to_process": [],
                    "message": f"PDF not found but OCR JSON exists at {expected_json_path.resolve()}. Skipping PDF check."
                }
            if file_name_or_all.lower() == 'all':
                msg = f"No PDF files found in directory {pdf_dir_path.resolve()}."
            else:
                msg = f"Specific PDF file '{file_name_or_all}.pdf' not found in {pdf_dir_path.resolve()}."
            return {"status": True, "files_to_process": [], "message": msg} # True status if nothing to process

        files_to_process = []
        
        for pdf_path in pdf_files:
            expected_json_name = f"{pdf_path.stem}_ocr.json"
            expected_json_path = output_root_path / expected_json_name
            
            if not expected_json_path.exists():
                files_to_process.append(pdf_path.stem)

        status = len(files_to_process) == 0
        message = f"Found {len(files_to_process)} files needing OCR processing."
        
        return {
            "status": status, # True if ALL checked files are processed
            "files_to_process": files_to_process, # List of base names that need to be processed
            "message": message
        }
        
class DocOCRTool:
    """
    A document OCR and content extraction tool using MinerUClient.
    Supports processing multi-page PDF documents and returns results in JSON format.
    """
    name = "doc_ocr_tool"
    # description = "Converts a raw PDF file into a structured JSON file containing all text, tables, and images with their coordinates. Must be run before searching or cropping a file for the first time."
    description = "Converts a raw PDF file into a structured JSON file. ONLY use this immediately AFTER doc_check_tool returns that a file is NOT processed."
    
    parameters = [
        {'name': 'file_name_or_all', 'type': 'string', 'description': 'The base name of a specific PDF document (without .pdf) to process, or "all" to process all PDFs in the configured PDF directory.', 'required': True},
        {'name': 'backend_type', 'type': 'string', 'description': 'The backend type: "transformers" or "vllm-engine".', 'required': False}
    ]

    def __init__(self, model_path: str, backend_type: str = 'transformers'):
        """
        Initializes DocOCRTool with specified backend type and model path, and sets default paths.

        Args:
            model_path (str): The path to the model.
            backend_type (str): The backend type to use for initialization. Can be 'transformers' or 'vllm-engine'. Default is 'transformers'.
        """
        
        self.model_path = model_path
        self.backend_type = backend_type
        
        self.client = self._initialize_mineru_client(model_path, backend_type)

    def _initialize_mineru_client(self, model_path: str, backend_type: str) -> MinerUClient:
        """
        Initializes the MinerUClient based on the specified backend type.
        """
        if backend_type == 'transformers':
            return self._initialize_transformers_client(model_path)
        elif backend_type == 'vllm-engine':
            return self._initialize_vllm_client(model_path)
        else:
            raise ValueError(f"Invalid backend_type: {backend_type}. Must be 'transformers' or 'vllm-engine'.")

    def _initialize_transformers_client(self, model_path: str) -> MinerUClient:
        """
        Initializes the MinerUClient using the transformers backend.
        """
        try:
            from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
            print("\n--- Initializing Transformers Backend ---")
            model = Qwen2VLForConditionalGeneration.from_pretrained(model_path, dtype="auto", device_map="auto")
            processor = AutoProcessor.from_pretrained(model_path, use_fast=True)

            client = MinerUClient(backend="transformers", model=model, processor=processor)
            print("✅ Successfully initialized MinerUClient with Transformers.")
            return client
        except Exception as e:
            print(f"❌ Transformers initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize Transformers backend: {e}")

    def _initialize_vllm_client(self, model_path: str) -> MinerUClient:
        """
        Initializes the MinerUClient using the vllm-engine backend.
        """
        try:
            print("\n--- Initializing VLLM-Engine Backend ---")
            from vllm import LLM
            from mineru_vl_utils import MinerULogitsProcessor

            llm_kwargs = {}
            if 'MinerULogitsProcessor' in globals():
                try:
                    llm_kwargs['logits_processors'] = [MinerULogitsProcessor]
                    print("  VLLM: Using MinerULogitsProcessor.")
                except Exception as e:
                    print(f"  VLLM: Failed to use MinerULogitsProcessor: {e}. Proceeding without it.")

            llm = LLM(model=model_path, **llm_kwargs)
            client = MinerUClient(backend="vllm-engine", vllm_llm=llm)
            print("✅ Successfully initialized MinerUClient with VLLM-Engine.")
            return client
        except ImportError:
            raise RuntimeError("VLLM library is not installed or required components are missing.")
        except Exception as e:
            print(f"❌ VLLM initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize VLLM-Engine: {e}")

    def _save_extracted_blocks_to_json(self, results: Union[list, dict], output_path: Path) -> Dict[str, Union[Any, bool]]:
        """
        Saves extracted OCR results (after pre-processing) to a JSON file.
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            return {
                "content_list": results, 
                "save_status": True, 
                "save_message": f"Results successfully saved to JSON: {output_path}"
            }
        except Exception as e:
            return {
                "content_list": results, 
                "save_status": False, 
                "save_message": f"Error saving results to JSON at {output_path}: {e}"
            }

    def _match_caption_and_cleanup(self, page_ocr_content: list) -> list:
        """
        Performs caption matching and cleanup:
        1. Identifies blocks with type containing 'caption'.
        2. Merges its 'content' into the 'caption' field of the adjacent main block (e.g., 'table', 'image').
        3. Removes the original caption block.
        """
        
        indices_to_remove = set()
        
        for i, block in enumerate(page_ocr_content):
            block_type = block.get('type', '')
            
            if "caption" in block_type:
                type_name = block_type.split('_')[0]
                caption_content = block.get('content', '')
                
                matched = False

                # 1. Check previous item 
                if i > 0 and page_ocr_content[i-1].get('type') == type_name:
                    page_ocr_content[i-1]['caption'] = caption_content
                    matched = True
                
                # 2. Check next item
                elif i < len(page_ocr_content) - 1 and page_ocr_content[i+1].get('type') == type_name:
                    page_ocr_content[i+1]['caption'] = caption_content
                    matched = True
                
                if matched:
                    indices_to_remove.add(i)
        
        new_page_ocr_content = [
            block for i, block in enumerate(page_ocr_content) if i not in indices_to_remove
        ]
        
        return new_page_ocr_content

    def _process_pdf_file(self, pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
        """
        Processes a single multi-page PDF file and extracts OCR content, 
        including pre-processing for captions.
        """
        results = []
        base_result = {
            "status": False,
            "doc_path": str(pdf_path),
            "json_path": "",
            "message": "",
        }
        
        try:
            pages = convert_from_path(pdf_path, dpi=300)
            base_name = pdf_path.stem
            json_output_file = output_dir / f"{base_name}_ocr.json"
            
            base_result['json_path'] = str(json_output_file)
            
            for i, page_image in enumerate(pages):
                # Placeholder for actual model call:
                page_results = self.client.two_step_extract(page_image)
                
                page_ocr_content = self._extract_ocr_content_from_page(page_image, page_results)
                
                # Core change: Pre-process content before saving
                processed_content = self._match_caption_and_cleanup(page_ocr_content)
                
                results.append({"page_id": i, "ocr_results": processed_content})

            # Save results to JSON
            json_save_res = self._save_extracted_blocks_to_json(results, json_output_file)
            base_result['status'] = json_save_res['save_status']
            base_result['message'] = json_save_res['save_message']
            return base_result
        except Exception as e:
            base_result['status'] = False
            base_result['message'] = f"Error processing PDF {pdf_path.name}: {e}"
            return base_result

    def _extract_ocr_content_from_page(self, page_image, page_results) -> list:
        """
        Extracts OCR content from a single page image, converting normalized
        coordinates to pixel-level bbox coordinates.
        """
        page_ocr_content = []
        image_width, image_height = page_image.size
        for block_index, block in enumerate(page_results):
            # Convert normalized bbox [x_min, y_min, x_max, y_max] to pixel values
            bbox = [
                int(block['bbox'][0] * image_width), 
                int(block['bbox'][1] * image_height), 
                int(block['bbox'][2] * image_width), 
                int(block['bbox'][3] * image_height)
            ]
            page_ocr_content.append({
                "block_id": block_index,
                "type": block['type'],
                "bbox": bbox,
                "angle": block.get('angle', 0), 
                "content": block.get('content', '')
            })
        return page_ocr_content

    def _get_pdf_files_to_process(self, file_name_or_all: str, pdf_dir_path: Path) -> List[Path]:
        """Get the list of PDF files to process (reusing DocCheckTool's logic)."""
        if file_name_or_all.lower() == 'all':
            return list(pdf_dir_path.glob('*.pdf')) + list(pdf_dir_path.glob('*.PDF'))
        else:
            target_path = pdf_dir_path / f"{file_name_or_all}.pdf"
            if target_path.exists():
                return [target_path]
            target_path_upper = pdf_dir_path / f"{file_name_or_all}.PDF"
            if target_path_upper.exists():
                 return [target_path_upper]
            return []
    def call(self, params: Union[str, dict], **kwargs) -> Dict[str, Any]:
        """
        Executes the OCR tool. Processes single PDF or all PDFs in the default directory.
        """
        error_template = {
            "status": False,
            "file_info": {},
            "message": ""
        }
        
        # --- 1. Parameter Parsing and Validation ---
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                error_template["message"] = "Error: Input parameters are not valid JSON."
                return error_template

        file_name_or_all = params.get('file_name_or_all')
        
        if not file_name_or_all:
            error_template["message"] = "Error: Missing required parameter 'file_name_or_all'."
            return error_template

        pdf_dir_path = DEFAULT_PDF_DIR
        output_dir_path = DEFAULT_OUTPUT_ROOT

        if not pdf_dir_path.exists() or not pdf_dir_path.is_dir():
            error_template["message"] = f"Error: PDF directory not found at {pdf_dir_path.resolve()}"
            return error_template

        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        files_to_process = self._get_pdf_files_to_process(file_name_or_all, pdf_dir_path)

        if not files_to_process:
            error_template["message"] = f"Error: No PDF files found for '{file_name_or_all}' in {pdf_dir_path.resolve()}"
            return error_template

        all_results = {}
        success_count = 0
        
        for pdf_path in files_to_process:
            print(f"Processing PDF: {pdf_path.name}...")
            file_result = self._process_pdf_file(pdf_path, output_dir_path) 
            
            all_results[pdf_path.stem] = {
                "json_path": file_result.get('json_path', ''),
                "pdf_path": str(pdf_path),
                "status": file_result.get('status', False),
                "message": file_result.get('message', '')
            }
            if file_result.get('status'):
                success_count += 1
                
        final_status = success_count == len(files_to_process)
        final_message = f"Successfully processed {success_count}/{len(files_to_process)} documents. All JSON results saved to {output_dir_path.resolve()}"
        
        return {
            "status": final_status,
            "file_info": all_results,
            "message": final_message
        }

class SearchKeywordTool:
    """
    A tool for searching keywords in a document.
    It searches pre-processed OCR JSON outputs, checking both 'content' and 'caption' fields.
    """
    name = "search_keyword_tool"
    description = "Searches for a keyword in the structured JSON content of processed documents. ONLY call this tool AFTER confirming the file is processed via doc_check_tool (and running doc_ocr_tool if necessary)."
    
    parameters = [
        {
            'name': 'keyword',
            'type': 'string',
            'description': 'The keyword to search for.',
            'required': True
        },
        {
            'name': 'file_list',
            'type': 'array',
            'array_type': 'object',
            'description': 'List of files to search. Each item: {"file_name": <base name without extension>, "page_id": <int or null>}',
            'required': False
        }
    ]

    def get_json_base(self, file_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resolves and loads the pre-processed OCR JSON for specified documents/pages.
        Uses internal DEFAULT_OUTPUT_ROOT.
        """
        json_base_list = []
        
        output_root_path = DEFAULT_OUTPUT_ROOT
        
        if not output_root_path.exists():
            return []

        files_to_process = []
        if not file_list:
            # Process all _ocr.json files if file_list is empty
            for json_path in output_root_path.glob('*_ocr.json'):
                files_to_process.append({"file_name": json_path.stem.split('_ocr')[0], "page_id": None})
        else:
            files_to_process = file_list

        for file_info in files_to_process:
            file_name = file_info.get('file_name')
            target_page_id = file_info.get('page_id')
            
            json_path = output_root_path / f"{file_name}_ocr.json"
            if not json_path.exists():
                continue

            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            except Exception:
                continue
            
            # content is a list of pages: [{"page_id": 0, "ocr_results": [...]}, ...]
            for page_item in content:
                current_page_id = page_item.get('page_id')
                
                # Check if the page should be processed
                if target_page_id is None or current_page_id == target_page_id:
                    page_content = page_item.get('ocr_results', [])
                    
                    json_base_list.append({
                        "file_name": file_name,
                        "json_path": str(json_path),
                        "page_id": current_page_id,
                        "ocr_results": page_content 
                    })
        return json_base_list

    def search_block_with_keyword(self, blocks: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """
        Searches within OCR blocks for the keyword (case-insensitive).
        Checks both 'content' and the pre-processed 'caption' field.
        """
        matches: List[Dict[str, Any]] = []
        if not keyword:
            return matches
        kw_lower = str(keyword).lower()
        
        # 'blocks' is a list of page objects
        for page_item in blocks:
            for block in page_item.get('ocr_results', []): 
                # Safely handle None values
                content = block.get('content') or ''
                caption = block.get('caption') or ''
                content_text = str(content).lower()
                caption_text = str(caption).lower() 

                # Search in content OR caption
                if kw_lower in content_text or kw_lower in caption_text:
                    match_result = {
                        "file_name": page_item.get('file_name'),
                        "page_id": page_item.get('page_id'),
                        "block_id": block.get('block_id'),
                        "type": block.get('type', ''),
                        "bbox": block.get('bbox', []),
                        "angle": block.get('angle', 0),
                        "content": content,  # Use the safe value
                        "caption": caption  # Use the safe value
                    }
                    matches.append(match_result)
        return matches

    def call(self, params: Union[str, dict], **kwargs) -> Dict[str, Any]:
        """
        Executes keyword search across specified files.
        """
        # Parameter parsing
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return {
                    "status": False, "keyword": "", "matches": [], 
                    "message": "Error: Input parameters are not valid JSON."
                }

        keyword = params.get('keyword')
        file_list = params.get('file_list', []) 

        if not keyword:
             return {
                "status": False, "keyword": "", "matches": [], 
                "message": "Error: 'keyword' is required."
            }
        
        if not DEFAULT_OUTPUT_ROOT.exists():
             return {
                "status": False, "keyword": keyword or "", "matches": [], 
                "message": f"Error: Output root directory not found at {DEFAULT_OUTPUT_ROOT.resolve()}."
            }


        # Core Logic Execution
        base_info = self.get_json_base(file_list=file_list)
        
        if not base_info:
            return {
                "status": False, 
                "keyword": keyword, 
                "matches": [], 
                "message": f"No document content found to search. Check if files in '{DEFAULT_OUTPUT_ROOT}' have been processed."
            }

        aggregate_matches = self.search_block_with_keyword(blocks=base_info, keyword=keyword)
        
        status = len(aggregate_matches) > 0
        message = f"Found {len(aggregate_matches)} matches for keyword '{keyword}'." if status else f"No matches found for keyword '{keyword}'."
            
        return {
            "status": status,
            "keyword": keyword,
            "matches": aggregate_matches,
            "message": message
        }

class GetPageOCRTool:
    """
    A tool for retrieving the full, concatenated OCR content of a specific page.
    Formats formula blocks using $$ delimiters.
    """
    name = "get_page_ocr_tool"
    description = "Based on a document block (e.g., from search_keyword_tool), it identifies the page and returns the full, concatenated OCR text content of that entire page."
    
    parameters = [
        {
            'name': 'file_name',
            'type': 'string',
            'description': 'The base name of the document file (without extension).',
            'required': True
        },
        {
            'name': 'page_id',
            'type': 'integer',
            'description': 'The 0-indexed ID of the page whose OCR content should be retrieved.',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> Dict[str, Any]:
        """
        Executes the OCR retrieval and concatenation.
        """
        error_template = {"status": False, "ocr_content": "", "message": ""}
        
        # --- 1. Parameter Parsing and Validation ---
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return {**error_template, "message": "Error: Input parameters are not valid JSON."}

        file_name = params.get('file_name')
        page_id = params.get('page_id')
        

        if not all([file_name, page_id is not None]):
            return {**error_template, "message": "Error: 'file_name' and 'page_id' are required."}
  
        json_path = DEFAULT_OUTPUT_ROOT / f"{file_name}_ocr.json"

        if not json_path.exists():
            return {**error_template, "message": f"Error: OCR JSON file not found at {json_path.resolve()}. Has the file been processed by DocOCRTool?"}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                doc_content = json.load(f)
        except Exception as e:
            return {**error_template, "message": f"Error loading JSON from {json_path.resolve()}: {e}"}

        page_content = None
        for page_item in doc_content:
            if page_item.get('page_id') == page_id:
                page_content = page_item.get('ocr_results', [])
                break
        
        if page_content is None:
            return {**error_template, "message": f"Error: Page ID {page_id} not found in the OCR JSON for file '{file_name}'."}

        concatenated_content = []
        for block in page_content:
            # Ensure block_content and caption are strings, not None
            block_content = block.get('content') or ''
            if block_content is None:
                block_content = ''
            else:
                block_content = str(block_content)
            
            block_type = block.get('type', '')
            
            caption = block.get('caption') or ''
            if caption:
                caption = str(caption)
                concatenated_content.append(f"Caption: {caption}")

            if block_type == 'formula':
                # Formulas wrapped in $$ (Display Math)
                formatted_content = f"$$\n{block_content}\n$$"
            elif block_type in ['table', 'image', 'chart']:
                # For non-text blocks, often only the content is the extracted text representation (if available)
                formatted_content = f"[{block_type.upper()} Content]\n{block_content}"
            else:
                # Standard text blocks
                formatted_content = block_content
            
            # Only add non-empty content
            if formatted_content and formatted_content.strip():
                concatenated_content.append(formatted_content.strip())
        
        final_text = '\n\n'.join(concatenated_content)

        return {
            "status": True,
            "file_name": file_name,
            "page_id": page_id,
            "ocr_content": final_text,
            "message": f"Successfully retrieved OCR content for page {page_id} of file '{file_name}'."
        }
        
class CropImageTool:
    name = "crop_image_tool"
    description = "Crops a specific figure, table, or chart from the PDF using the location data (bbox and angle) obtained from the search_keyword_tool. Returns the local file path to the high-resolution, upright PNG image, saved in the temp directory."
    
    parameters = [
        {
            'name': 'match_block', 
            'type': 'object',
            'description': 'The single match block to be cropped. Keys must include: "file_name" (base name), "page_id" (int), "block_id" (int), "type" (str), "bbox" (list), and "angle" (int).',
            'required': True
        }
    ]
    
    def call(self, params: Union[str, dict], **kwargs) -> Dict[str, Any]:
        """
        Executes the crop image tool, saves the cropped and rotated image, and returns its path.
        """
        error_template = {"status": False, "cropped_image_path": "", "message": ""}
        
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return {**error_template, "message": "Error: Input parameters are not valid JSON."}

        match_block = params.get('match_block')
        
        pdf_dir_path = DEFAULT_PDF_DIR
        output_crop_path = DEFAULT_TEMP_DIR
        
        if not match_block:
            return {**error_template, "message": "Error: 'match_block' is required."}
        if not pdf_dir_path.exists():
            return {**error_template, "message": f"Error: PDF directory not found at {pdf_dir_path.resolve()}."}

        block = match_block
        file_name = block.get('file_name')
        page_id = block.get('page_id')
        bbox = block.get('bbox')
        block_type = block.get('type')
        block_id = block.get('block_id')
        angle = block.get('angle', 0)

        if not all([file_name, page_id is not None, bbox, block_type, block_id is not None]):
            return {**error_template, "message": "Error: 'match_block' is missing required keys (file_name, page_id, bbox, type, block_id)."}

        if block_type not in ['image', 'table', 'chart']:
            return {**error_template, "message": f"Error: Block type '{block_type}' is not supported. Only 'image', 'table', and 'chart' blocks can be cropped."}
        
        output_crop_path.mkdir(parents=True, exist_ok=True)
        
        pdf_path_lower = pdf_dir_path / f"{file_name}.pdf"
        pdf_path_upper = pdf_dir_path / f"{file_name}.PDF"
        pdf_path = None
        
        if pdf_path_lower.exists():
            pdf_path = pdf_path_lower
        elif pdf_path_upper.exists():
            pdf_path = pdf_path_upper
        else:
            return {**error_template, "message": f"Error: PDF file not found for {file_name} in {pdf_dir_path.resolve()}."}
        
        try:
            pdf_page_index = int(page_id) + 1
            
            page_images = convert_from_path(str(pdf_path), first_page=pdf_page_index, last_page=pdf_page_index, dpi=300)
            
            if not page_images:
                raise Exception(f"PDF does not contain page {page_id}")
                
            page_image = page_images[0]
            image_crop = page_image.crop(bbox)
            
            if angle != 0:
                image_crop = image_crop.rotate(-angle, expand=True, fillcolor=(255, 255, 255))
            
            crop_filename = f"{file_name}_page{page_id}_block{block_id}_rotated_crop.png"
            crop_filepath = output_crop_path / crop_filename
            
            image_crop.save(crop_filepath)
            
            return {
                "status": True,
                "file_name": file_name,
                "page_id": page_id,
                "block_id": block_id,
                "type": block_type,
                "bbox": bbox,
                "angle": angle,
                "cropped_image_path": str(crop_filepath),
                "message": f"Successfully cropped and rotated '{block_type}' from page {page_id} by {angle} degrees, saved to {crop_filepath.resolve()}"
            }
            
        except Exception as e:
            return {
                "status": False, 
                "cropped_image_path": "",
                "message": f"Error processing block (ID {block_id}) from page {page_id}: {str(e)}",
                "block_details": block
            }

class GetPageImageTool:
    """
    A tool for extracting and saving a specific page image from a PDF document.
    """
    name = "get_page_image_tool"
    description = "Based on a document block (e.g., from search_keyword_tool), it identifies the page and extracts the full image of that entire page, saving it as a PNG file in the temp directory. Returns the path to the saved image."
    
    parameters = [
        {
            'name': 'file_name',
            'type': 'string',
            'description': 'The base name of the document file (without extension).',
            'required': True
        },
        {
            'name': 'page_id',
            'type': 'integer',
            'description': 'The 0-indexed ID of the page to extract.',
            'required': True
        }
    ]

    def call(self, params: Union[str, dict], **kwargs) -> Dict[str, Any]:
        """
        Executes the page image extraction, saves the image, and returns its path.
        """
        error_template = {"status": False, "image_path": "", "message": ""}
        
        # --- 1. Parameter Parsing and Validation ---
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                return {**error_template, "message": "Error: Input parameters are not valid JSON."}

        file_name = params.get('file_name')
        page_id = params.get('page_id')
        
        pdf_dir_path = DEFAULT_PDF_DIR
        output_dir = DEFAULT_TEMP_DIR

        if not all([file_name, page_id is not None]):
            return {**error_template, "message": "Error: 'file_name' and 'page_id' are required."}
        
        if not pdf_dir_path.exists():
            return {**error_template, "message": f"Error: PDF directory not found at {pdf_dir_path.resolve()}"}
        
        # Find PDF Path (Handles .pdf and .PDF)
        pdf_path_lower = pdf_dir_path / f"{file_name}.pdf"
        pdf_path_upper = pdf_dir_path / f"{file_name}.PDF"
        pdf_path = None
        
        if pdf_path_lower.exists():
            pdf_path = pdf_path_lower
        elif pdf_path_upper.exists():
            pdf_path = pdf_path_upper
        else:
            return {**error_template, "message": f"Error: PDF file not found for {file_name} in {pdf_dir_path.resolve()}."}

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            pdf_page_index = int(page_id) + 1
            
            page_images = convert_from_path(str(pdf_path), 
                                            first_page=pdf_page_index, 
                                            last_page=pdf_page_index, 
                                            dpi=300)
            
            if not page_images:
                raise Exception(f"Page {page_id} (index {pdf_page_index}) not found in PDF.")
                
            page_image = page_images[0]
            
            image_filename = f"{file_name}_page{page_id}_full.png"
            image_filepath = output_dir / image_filename
            
            page_image.save(image_filepath)
            
            return {
                "status": True,
                "file_name": file_name,
                "page_id": page_id,
                "image_path": str(image_filepath),
                "message": f"Successfully extracted page {page_id} and saved to {image_filepath.resolve()}"
            }
            
        except Exception as e:
            return {**error_template, "message": f"Error extracting page {page_id} from PDF {file_name}: {str(e)}"}             

class ImageDescriptionTool:
    """
    A tool that uses a multimodal LLM (e.g., OpenAI's GPT-4V) to generate a
    detailed description for an image or chart provided as a local file path.
    Requires OPENAI_API_KEY and OPENAI_API_BASE / OPENAI_BASE_URL environment variables to be set.
    """
    name = "image_description_tool"
    description = "Uses a multimodal model (VLM) to analyze a local image file (PNG/JPG) and generate a detailed text description. Use after crop_image_tool or get_page_image_tool to interpret visual content."
    
    # ... (parameters 保持不变) ...
    parameters = [
        {
            'name': 'image_path',
            'type': 'string',
            'description': 'The file path to the image (PNG or JPG) that needs analysis. This path is typically obtained from the crop_image_tool or get_page_image_tool, located in the temp directory.',
            'required': True
        }
    ]

    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        Initializes the tool and checks for necessary API credentials.
        """
        self.api_key = api_key if api_key and api_key.strip() else os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.api_key = self.api_key.strip()
        else:
            self.api_key = None
        
        self.api_base = api_base if api_base and api_base.strip() else (
            os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_API_URL") or os.getenv("OPENAI_BASE_URL")
        )
        if self.api_base:
            self.api_base = self.api_base.strip()
        else:
            self.api_base = None
        
        self.model_name = model_name
        self.client = None
        self.is_ready = False

        if not self.api_key or not self.api_base:
            print("Warning: OPENAI_API_KEY or OPENAI_API_BASE/OPENAI_BASE_URL/OPENAI_API_URL environment variables are not set. The tool will not be usable.")
        else:
            try:
                client_kwargs = {}
                if self.api_key:
                    client_kwargs["api_key"] = self.api_key
                if self.api_base:
                    client_kwargs["base_url"] = self.api_base
                # --- 修改点 1: 实例化 OpenAI 客户端 ---
                self.client = OpenAI(**client_kwargs) 
                self.is_ready = True
                print("✅ Successfully initialized OpenAI client.")
            except Exception as e:
                print(f"❌ Error initializing OpenAI client: {e}")
                self.is_ready = False

    def _encode_image_to_base64(self, image_path: Path) -> str:
        """
        Converts a local image file to a base64 encoded string.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def call(self, params: Union[str, dict], **kwargs) -> Dict[str, Any]:
        """
        Executes the image description generation via API call using the OpenAI client.
        The output format will inherit the input parameters and add a 'description' field.
        """
        base_error_template = {"status": False, "description": "", "message": ""}
        
        # --- 1. Parameter Parsing and Validation ---
        if isinstance(params, str):
            try:
                input_params = json.loads(params)
            except json.JSONDecodeError:
                return {**base_error_template, "message": "Error: Input parameters are not valid JSON."}
        else:
            input_params = params.copy()

        image_path_str = input_params.get('cropped_image_path') or input_params.get('image_path')
        
        if 'image_path' not in input_params and image_path_str:
            input_params['image_path'] = image_path_str 

        if not image_path_str:
            return {**base_error_template, "message": "Error: Required parameter 'image_path' or 'cropped_image_path' is missing."}

        # --- 2. Tool Readiness Check ---
        if not self.is_ready or not self.client:
            return {
                **input_params,
                **base_error_template,
                "message": "Error: OpenAI client is not initialized. Please set OPENAI_API_KEY and OPENAI_API_BASE / OPENAI_BASE_URL environment variables."
            }

        image_path = Path(image_path_str)
        if not image_path.exists():
            return {**input_params, **base_error_template, "message": f"Error: Image file not found at {image_path_str}"}

        # --- 3. Encode Image ---
        try:
            base64_image = self._encode_image_to_base64(image_path)
            # 确保使用正确的 MIME type (PNG, JPG/JPEG)
            mime_type = f"image/{image_path.suffix.lstrip('.')}"
            image_url = f"data:{mime_type};base64,{base64_image}"
        except Exception as e:
            return {**input_params, **base_error_template, "message": f"Error encoding image to base64: {e}"}

        # --- 4. Construct and Execute API Call ---
        default_prompt = (
            "Generate a comprehensive analysis of the image. The description must first identify the **Type** "
            "(e.g., bar chart, line graph, table, photograph, technical diagram, flow chart). "
            "Ensure the description is detailed and structured based on the type: \n\n"
            "**If it is a Chart, Table, or Data Visualization**:\n"
            "Focus on: **Key Data/Trends** (specify numbers, peaks, troughs, percentage changes), **Axis/Labels**, and summarize the main conclusions or relationships shown.\n\n"
            "**If it is a Photograph, Drawing, or General Illustration**:\n"
            "Focus on: **Subject Matter** (what is the main object/scene?), **Content Detail** (describe important visible features/labels), and its **Context/Relevance** to a technical or procedural document.\n\n"
            "Provide a final concise summary of the visual content."
            )
        question = default_prompt
        
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ]

            # --- 修改点 2: 完整的 API 调用逻辑 ---
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=2048
            )
            description = response.choices[0].message.content.strip()
            
            # --- 5. Return Result (继承输入格式) ---
            return {
                **input_params,
                "status": True,
                "description": description,
                "message": "Image description successfully generated."
            }

        except Exception as e:
            # 捕获 API 错误，返回包含输入参数的错误信息
            return {
                **input_params, 
                **base_error_template, 
                "message": f"API call failed: {e}. Check API key, base URL, and model name."
            }
                  
# # if __name__ == '__main__':
#     # ------------------- MinerU Test --------------------------------
#     # 1. Configuration (can be modified as needed)
#     model_path = "/mnt/dhwfile/doc_parse/wufan/cache/mineru2.5/mineru2.5_0916_e3"
#     backend_type = 'transformers'  # 'transformers' or 'vllm-engine'
#     test_root = "/mnt/petrelfs/zhangjunyuan/zqt/Agent_Flow/AgentFlow-main/src/data/doc_demo/"
#     test_pdf = "PDF/test_pdf.pdf"
#     output_dir = "/mnt/petrelfs/zhangjunyuan/zqt/Agent_Flow/AgentFlow-main/src/data/doc_demo/output"

#     # 2. Initialize DocOCRTool
#     try:
#         # Directly pass model path and backend type to DocOCRTool's __init__ method
#         doc_ocr_tool = DocOCRTool(model_path=model_path, backend_type=backend_type)
#         print(f"Successfully initialized {doc_ocr_tool.name} with {doc_ocr_tool.client.backend} backend.")
#     except (RuntimeError, ValueError) as e:
#         print(f"\n--- FATAL ERROR: Client Initialization Failed ---")
#         print(str(e))
#         sys.exit(1)

#     # 3. Test file setup
#     test_pdf_path = os.path.join(test_root, test_pdf)
#     output_dir = Path(output_dir)

#     # 4. Process PDF file
#     print(f"\n--- Processing File: {test_pdf_path} ---")
#     params = {
#         'input_path': test_pdf_path,
#         'output_dir': str(output_dir)
#     }
#     result = doc_ocr_tool.call(params)
#     print(f"Tool Call Result (Status: {result}):")

#     # 5. Optional cleanup
#     print("\n--- Test Cleanup ---")