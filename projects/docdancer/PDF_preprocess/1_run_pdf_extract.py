import os
import json
import argparse
import traceback 
from pathlib import Path
from typing import List, Dict, Any

try:
    from vllm import LLM
    from PIL import Image
    from pdf2image import convert_from_path 
    from mineru_vl_utils import MinerUClient
    from mineru_vl_utils import MinerULogitsProcessor 
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please ensure you have installed them: pip install 'mineru-vl-utils[vllm]' pdf2image Pillow")
    exit(1)


class MinerUPDFProcessor:
    """
    Batch process PDF files using the MinerU model and vLLM engine for two-step extraction and post-processing.
    """
    def __init__(self, model_name: str = "opendatalab/MinerU2.5-2509-1.2B"):
        print("🚀 Initializing vLLM Engine and MinerU Client...")
        
        self.llm = LLM(
            model=model_name,
            logits_processors=[MinerULogitsProcessor] 
        )
        
        self.client = MinerUClient(
            backend="vllm-engine",
            vllm_llm=self.llm
        )
        print("✅ Initialization complete.")


    def _extract_ocr_content_from_page(self, page_image: Image.Image, page_results: List[Dict]) -> List[Dict]:
        page_ocr_content = []
        image_width, image_height = page_image.size
        
        for block_index, block in enumerate(page_results):
            bbox = [
                    int(block['bbox'][0] * image_width), 
                    int(block['bbox'][1] * image_height), 
                    int(block['bbox'][2] * image_width), 
                    int(block['bbox'][3] * image_height)
                ]

            page_ocr_content.append({
                "block_id": block_index,
                "type": block.get('type', ''),
                "bbox": bbox,
                "angle": block.get('angle', 0), 
                "content": block.get('content', ''),
                "origin_block":block
            })
        return page_ocr_content


    def _match_caption_and_cleanup(self, page_ocr_content: List[Dict]) -> List[Dict]:
        indices_to_remove = set()
        
        for i, block in enumerate(page_ocr_content):
            block_type = block.get('type', '')
            
            if "caption" in block_type.lower(): 
                type_parts = block_type.split('_')
                type_name = type_parts[0] if type_parts and type_parts[-1] == 'caption' else None
                
                caption_content = block.get('content', '')
                
                if not type_name:
                    type_name = None 
                
                matched = False

                # 1. Check the previous item
                if i > 0:
                    prev_block = page_ocr_content[i-1]
                    if type_name is None or prev_block.get('type') == type_name:
                        prev_block['caption'] = caption_content
                        matched = True
                        
                # 2. If previous item did not match, check the next item
                if not matched and i < len(page_ocr_content) - 1:
                    next_block = page_ocr_content[i+1]
                    if type_name is None or next_block.get('type') == type_name:
                        next_block['caption'] = caption_content
                        matched = True
                
                if matched:
                    indices_to_remove.add(i)
        
        new_page_ocr_content = [
            block for i, block in enumerate(page_ocr_content) if i not in indices_to_remove
        ]
        
        return new_page_ocr_content

    def process_pdf(self, pdf_path: Path, output_dir: Path):
        base_name = pdf_path.stem
        print(f"\n📄 Starting processing for: {pdf_path.name}")
        
        pages = convert_from_path(str(pdf_path), dpi=300)

        print(f"   -> Found {len(pages)} pages. Running vLLM inference in batch mode...")
        all_page_results = self.client.batch_two_step_extract(pages)
        print("   -> Inference complete. Starting post-processing.")
        
        pdf_results = []
        for i, (page_image, page_results) in enumerate(zip(pages, all_page_results)):
            
            page_ocr_content = self._extract_ocr_content_from_page(page_image, page_results)
            
            processed_content = self._match_caption_and_cleanup(page_ocr_content)
            
            pdf_results.append({"page_id": i, "ocr_results": processed_content})

        json_output_file = output_dir / f"{base_name}_ocr.json"
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(pdf_results, f, ensure_ascii=False, indent=4)
            
        print(f"   -> Successfully processed and saved to: {json_output_file}")


    def run_batch_processing(self, input_dir: Path, output_dir: Path) -> List[str]:
        """
        Traverse the input directory and process all PDF files.
        If an error occurs or the file has already been processed, skip and record it.

        Returns:
            List[str]: A list of PDF file names that failed to be processed.
        """
        if not input_dir.is_dir():
            print(f"Error: Input directory not found at {input_dir}")
            return []
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {input_dir}")
            return []
        
        print(f"\n✨ Found {len(pdf_files)} PDF files to process in {input_dir}")
        
        failed_pdfs: List[str] = [] 

        for pdf_path in pdf_files:
            pdf_name = pdf_path.name
            base_name = pdf_path.stem
            json_output_file = output_dir / f"{base_name}_ocr.json"

            if json_output_file.exists():
                print(f"   -> Skipping {pdf_name}: Output file already exists at {json_output_file}")
                continue 

            try:
                self.process_pdf(pdf_path, output_dir)
            except Exception as e:
                print(f"\n❌ Error processing {pdf_name}. Skipping to next file.")
                print(f"   Error details: {e}")
                traceback.print_exc() 
                
                failed_pdfs.append(pdf_name)
                continue 
            
        print("\n🎉 All PDF files processed (or skipped).")
        
        return failed_pdfs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch process PDF files using MinerU VLM with vLLM engine."
    )
    parser.add_argument(
        "--input_dir", 
        type=str, 
        required=True, 
        help="Path to the directory containing PDF files."
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        required=True, 
        help="Path to the directory where output JSON files will be saved."
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="opendatalab/MinerU2.5-2509-1.2B",
        help="Path or repo id to the model checkpoint (default: opendatalab/MinerU2.5-2509-1.2B)."
    )
    
    args = parser.parse_args()
    
    processor = MinerUPDFProcessor(model_name=args.model_path)
    
    failed_files = processor.run_batch_processing(Path(args.input_dir), Path(args.output_dir))

    if failed_files:
        print("\n--- ⚠️ Processing Summary ---")
        print(f"Total files failed: {len(failed_files)}")
        print("Failed PDF files:")
        for name in failed_files:
            print(f"- {name}")
        print("----------------------------")
    else:
        print("\n✅ All specified PDF files were processed successfully or skipped (already existing).")