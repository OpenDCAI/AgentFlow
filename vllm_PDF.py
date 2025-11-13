import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# 依赖库导入
try:
    from vllm import LLM
    from PIL import Image
    from pdf2image import convert_from_path # 用于将 PDF 转换为图片
    from mineru_vl_utils import MinerUClient
    from mineru_vl_utils import MinerULogitsProcessor # vllm>=0.10.1 推荐
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please ensure you have installed them: pip install 'mineru-vl-utils[vllm]' pdf2image Pillow")
    exit(1)


class MinerUPDFProcessor:
    """
    使用 MinerU 模型和 vLLM 引擎批量处理 PDF 文件，进行两步提取和后处理。
    """
    def __init__(self, model_name: str = "/mnt/shared-storage-user/mineru2-shared/zhengyuanhong/MinerU2.5-2509-1.2B/"):
        print("🚀 Initializing vLLM Engine and MinerU Client...")
        
        # 1. 初始化 vLLM 引擎
        # 注意：此处假设您的环境可以支持此模型（显存、硬件）
        self.llm = LLM(
            model=model_name,
            # 添加 LogitsProcessor 以优化 MinerU 的采样，要求 vllm>=0.10.1
            logits_processors=[MinerULogitsProcessor] 
        )
        
        # 2. 初始化 MinerU 客户端
        self.client = MinerUClient(
            backend="vllm-engine",
            vllm_llm=self.llm
        )
        print("✅ Initialization complete.")

    def _extract_ocr_content_from_page(self, page_image: Image.Image, page_results: List[Dict]) -> List[Dict]:
        """
        处理 1: 提取 OCR 内容，并将归一化坐标转换为像素坐标。
        """
        page_ocr_content = []
        image_width, image_height = page_image.size
        
        for block_index, block in enumerate(page_results):
            # 将归一化 bbox [x_min, y_min, x_max, y_max] 转换为像素值
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
                "content": block.get('content', '')
            })
        return page_ocr_content

    def _match_caption_and_cleanup(self, page_ocr_content: List[Dict]) -> List[Dict]:
        """
        处理 2: 匹配图表标题（caption）并清理：
        1. 识别类型中包含 'caption' 的块。
        2. 将其内容合并到相邻的 'table' 或 'image' 等主块的 'caption' 字段中。
        3. 移除原始的 caption 块。
        """
        
        indices_to_remove = set()
        
        for i, block in enumerate(page_ocr_content):
            block_type = block.get('type', '')
            
            if "caption" in block_type.lower(): # 使用 .lower() 确保匹配
                # 尝试获取主类型名 (e.g., 'table_caption' -> 'table')
                type_parts = block_type.split('_')
                type_name = type_parts[0] if type_parts and type_parts[-1] == 'caption' else None
                
                caption_content = block.get('content', '')
                
                if not type_name:
                    # 如果不是标准的 'type_caption' 格式，尝试通用匹配
                    type_name = None 
                
                matched = False

                # 1. 检查前一个项目
                if i > 0:
                    prev_block = page_ocr_content[i-1]
                    # 匹配逻辑：如果当前块是 caption，前一块是其对应的主体块
                    if type_name is None or prev_block.get('type') == type_name:
                        prev_block['caption'] = caption_content
                        matched = True
                        
                # 2. 如果前一个没有匹配上，检查下一个项目
                if not matched and i < len(page_ocr_content) - 1:
                    next_block = page_ocr_content[i+1]
                    # 匹配逻辑：如果当前块是 caption，后一块是其对应的主体块
                    if type_name is None or next_block.get('type') == type_name:
                        next_block['caption'] = caption_content
                        matched = True
                
                # 如果匹配成功，则将当前 caption 块标记为移除
                if matched:
                    indices_to_remove.add(i)
        
        # 移除已合并的 caption 块
        new_page_ocr_content = [
            block for i, block in enumerate(page_ocr_content) if i not in indices_to_remove
        ]
        
        return new_page_ocr_content

    def process_pdf(self, pdf_path: Path, output_dir: Path):
        """
        处理单个 PDF 文件：拆分页面，批量推理，并进行后处理。
        """
        base_name = pdf_path.stem
        print(f"\n📄 Starting processing for: {pdf_path.name}")
        
        # 1. PDF 转换为图片（pages是一个PIL.Image列表）
        pages = convert_from_path(str(pdf_path), dpi=300)

        # 2. **关键优化：将所有页面作为一个批次进行 vLLM 推理**
        print(f"   -> Found {len(pages)} pages. Running vLLM inference in batch mode...")
        
        # all_page_results = self.client.two_step_extract(pages)
        all_page_results = self.client.batch_two_step_extract(pages)


        print("   -> Inference complete. Starting post-processing.")
        
        # 3. 后处理和格式化
        pdf_results = []
        for i, (page_image, page_results) in enumerate(zip(pages, all_page_results)):
            
            # 处理 1: 格式化和坐标转换
            page_ocr_content = self._extract_ocr_content_from_page(page_image, page_results)
            
            # 处理 2: 匹配 caption 和清理
            processed_content = self._match_caption_and_cleanup(page_ocr_content)
            
            pdf_results.append({"page_id": i, "ocr_results": processed_content})

        # 4. 存储结果
        json_output_file = output_dir / f"{base_name}_ocr.json"
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(pdf_results, f, ensure_ascii=False, indent=4)
            
        print(f"   -> Successfully processed and saved to: {json_output_file}")


    def run_batch_processing(self, input_dir: Path, output_dir: Path):
        """
        遍历输入目录，处理所有 PDF 文件。
        """
        if not input_dir.is_dir():
            print(f"Error: Input directory not found at {input_dir}")
            return
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {input_dir}")
            return
        
        print(f"\n✨ Found {len(pdf_files)} PDF files to process in {input_dir}")

        for pdf_path in pdf_files:
            self.process_pdf(pdf_path, output_dir)
            
        print("\n🎉 All PDF files processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch process PDF files using MinerU VLM with vLLM engine."
    )
    # 示例用法：python process_pdfs.py --input_dir /path/to/pdfs --output_dir /path/to/output
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
    
    args = parser.parse_args()
    
    # 实例化并运行
    processor = MinerUPDFProcessor()
    processor.run_batch_processing(Path(args.input_dir), Path(args.output_dir))