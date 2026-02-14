import json
import os
import argparse
import pickle
import numpy as np
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path  # For better path manipulation
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm
import openai
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing  # For getting CPU core count
import time


# --- VLM Prompt (unchanged) ---
PROMPT = """
    **ROLE:** You are an expert and highly detailed Visual Language Model (VLM) image describer. Your sole task is to analyze the input image meticulously and generate a comprehensive, objective, and purely descriptive text.

    **INSTRUCTION:**
    1.  **Analyze the Image Type:** Determine the primary content category (e.g., Chart/Graph, Flowchart/Diagram, Academic Paper Figure, Poster/Infographic, Natural Photograph, Text/Document, etc.).
    2.  **Describe the Overall Scene/Layout:** State the main subject, setting, or purpose of the image. For structured images (charts, diagrams), describe the layout (e.g., "A bar chart comparing...", "A three-step process flowchart...", "A vertically oriented film poster...").
    3.  **Detail Key Components:**
        * **For Charts/Graphs/Diagrams:** Describe the type (bar, line, pie, scatter), axes, labels, and the main trend or conclusion. Include specific data points or relationships if legible.
        * **For Flowcharts/Diagrams:** Trace the sequence of steps, nodes, and connections. Identify the start and end points and the purpose of the process.
        * **For Posters/Infographics:** Describe the prominent visuals, main title/text, and overall color scheme/mood.
        * **For Natural Images:** Describe the subjects, setting, actions, mood, time of day, and primary visual elements (colors, composition, texture).
    4.  **Incorporate Text (if present):** Transcribe and mention any significant, legible text within the image (titles, labels, captions) and state its location/context.
    5.  **Maintain Objectivity:** Do not offer interpretations, opinions, emotional reactions, or subjective analysis. Stick strictly to what is visually observable.

    **OUTPUT FORMAT REQUIREMENT:**
    * **Generate ONLY the descriptive text.**
    * **Do NOT include any prefixes** like "Image description:", "The image shows:", or "Based on the image...".
    * **The output must be a continuous block of text.**

"""

def get_response(
    image_path, 
    prompt, 
    api_key=None, 
    base_url=None, 
    model_name=None,
    **kwargs,
):
    """
    Sends a request to OpenAI's API for image understanding with prompt and image.
    Args:
        image_path (str): Path to the image file.
        prompt (str): Prompt string for the model.
        api_key (str): OpenAI API key. (If None, default openai package behavior applies.)
        base_url (str): Custom API base url (for Azure, etc). Optional.
        model_name (str): Model name (e.g., "gpt-4-vision-preview")
        kwargs: Extra openai.Image.create parameters

    Returns:
        str: The model-generated image description response.
    """
    client = openai.OpenAI(api_key=api_key, base_url=base_url) if base_url or api_key else openai.OpenAI()
    if not model_name:
        model_name = "gpt-4o"  

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    msg_content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_bytes.encode("base64").decode()}},
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": msg_content}],
        max_tokens=1024,
        temperature=0.2,
        **kwargs,
    )
    return response.choices[0].message.content

def simple_gap_clustering(height_list, min_gap_ratio=1.15):
    """
    Simple gap-based sort and split algorithm for clustering title heights.
    """
    if not height_list:
        return []

    unique_heights = np.array(sorted(list(set(height_list))))
    if len(unique_heights) <= 1:
        return [(unique_heights[0], unique_heights[0])]

    clusters = []
    current_cluster_start_h = unique_heights[0]

    for i in range(1, len(unique_heights)):
        h_prev = unique_heights[i-1]
        h_curr = unique_heights[i]
        
        if h_curr / h_prev > min_gap_ratio:
            clusters.append((current_cluster_start_h, h_prev))
            current_cluster_start_h = h_curr
    
    clusters.append((current_cluster_start_h, unique_heights[-1]))
    
    return clusters

def split_and_load_pdf_images(pdf_path: Path, page_image_output_dir: Path) -> list[Image.Image] | None:
    """
    Split a PDF into images per page, save them, and return the list of images.
    """
    pdf_base_name = pdf_path.stem
    print(f"[{pdf_base_name}] Loading and saving PDF page images (DPI=300)...")

    try:
        page_image_output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[{pdf_base_name}] ❌ Error: Could not create directory {page_image_output_dir}: {e}")
        return None

    try:
        pages: list[Image.Image] = convert_from_path(str(pdf_path), dpi=300, fmt='png')
        print(f"[{pdf_base_name}] Loaded {len(pages)} pages successfully.")
    except Exception as e:
        print(f"[{pdf_base_name}] ❌ Error: Failed to read PDF with pdf2image. Error: {e}. Skipping.")
        return None

    for i, page_image in enumerate(pages):
        file_name = f"page_{i:04d}.png"
        output_path = page_image_output_dir / file_name
        try:
            page_image.save(output_path)
        except Exception as e:
            print(f"[{pdf_base_name}] ❌ Error: Failed to save page image {file_name}: {e}")
            continue

    return pages

def split_and_load_pdf_images_fitz(
    pdf_path: Path,
    page_image_output_dir: Path,
    dpi: int = 300
) -> list[Image.Image] | None:
    """
    Use PyMuPDF (fitz) to render PDF pages as images, save them and return the list of PIL Images.
    """
    pdf_base_name = pdf_path.stem
    print(f"[{pdf_base_name}] Loading PDF pages with PyMuPDF (DPI={dpi})...")

    try:
        page_image_output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[{pdf_base_name}] ❌ Failed to create directory: {e}")
        return None

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"[{pdf_base_name}] ❌ Failed to open PDF: {e}")
        return None

    zoom = dpi / 72  # DPI conversion for PyMuPDF
    mat = fitz.Matrix(zoom, zoom)

    page_images = []

    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        file_name = f"page_{page_index:04d}.png"
        output_path = page_image_output_dir / file_name
        img.save(output_path)

        page_images.append(img)

    doc.close()
    print(f"[{pdf_base_name}] Loaded {len(page_images)} pages successfully.")
    return page_images

def get_preprocess_json(data, PDF_name, page_image_list, save_root):
    """
    Process structured PDF data and generate final JSON and PKL output files.
    The first 'title' element on the first page is treated as Title and does not participate in heading clustering.
    Accepts preloaded page_image_list.
    """
    FILE_SAVE = os.path.join(save_root, PDF_name)
    FILE_FIGURE_SAVE = os.path.join(FILE_SAVE, "figures")
    FILE_TABLE_SAVE = os.path.join(FILE_SAVE, "tables")
    os.makedirs(FILE_FIGURE_SAVE, exist_ok=True)
    os.makedirs(FILE_TABLE_SAVE, exist_ok=True)

    if not page_image_list:
        print(f"[{PDF_name}] ❌ Error: Page image list is empty. Cannot crop figures/tables.")
        return None

    height_list = []
    total_elements = 0
    document_title_found = False
    document_title_index = None

    for page_idx, page_item in enumerate(data):
        if isinstance(page_item, dict) and "ocr_results" in page_item:
            elements = page_item["ocr_results"]
        elif isinstance(page_item, list):
            elements = page_item
        else:
            elements = []
        
        total_elements += len(elements)
        
        for item_idx, item in enumerate(elements):
            if not isinstance(item, dict):
                continue
            
            if item.get("type") == "title" and item.get("bbox") is not None:
                # Skip the first 'title' on the first page
                if page_idx == 0 and not document_title_found:
                    document_title_found = True
                    document_title_index = (page_idx, item_idx)
                    continue

                # Other 'title' elements participate in heading clustering
                height = item["bbox"][3] - item["bbox"][1]
                height_list.append(height)

    height_clusters = simple_gap_clustering(height_list)
    cluster_map = {}
    sorted_clusters = sorted(height_clusters, key=lambda x: x[0], reverse=True)

    for i, (min_h, max_h) in enumerate(sorted_clusters):
        style_name = f"Heading {i+1}"
        for h in sorted(list(set(h for h in height_list if min_h <= h <= max_h))):
            cluster_map[h] = style_name

    all_data = []
    page_id = 0
    table_id = 0
    image_id = 0
    title_applied = False

    with tqdm(total=total_elements, desc=f"[{PDF_name}] Processing elements", unit="item") as pbar:
        for page_idx, page_item in enumerate(data):
            all_data.append({
                "para_text": None,
                "table_id": page_id,
                "style": "Page_Start"
            })
            page_id += 1

            if isinstance(page_item, dict) and "ocr_results" in page_item:
                elements = page_item["ocr_results"]
            elif isinstance(page_item, list):
                elements = page_item
            else:
                elements = []

            if page_idx >= len(page_image_list):
                pbar.update(len(elements))
                continue

            page_image = page_image_list[page_idx]

            for item_idx, item in enumerate(elements):
                if not isinstance(item, dict):
                    pbar.update(1)
                    continue

                item_type = item.get("type")
                bbox = item.get("bbox")
                pbar.set_postfix_str(f"Page {page_idx+1} ({item_type})")

                if item_type not in ["image", "table"]:
                    style = item_type.capitalize()

                    if item_type == "title" and bbox is not None:
                        if (page_idx, item_idx) == document_title_index and not title_applied:
                            style = "Title"
                            title_applied = True
                            content_preview = item.get('content', '...').replace('\n', ' ')
                            print(f"\n[{PDF_name}] 📝 Document Title Identified: '{content_preview[:50]}...'")
                        else:
                            current_height = bbox[3] - bbox[1]
                            style = cluster_map.get(current_height, "Title_Other")

                    if item.get("content") is None:
                        continue

                    all_data.append({
                        "para_text": item.get("content"),
                        "table_id": None,
                        "style": style
                    })
                else:
                    if bbox is None:
                        pbar.update(1)
                        continue

                    try:
                        crop_area = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
                        crop_image = page_image.crop(crop_area)
                    except Exception as e:
                        print(f"\n[{PDF_name}] ⚠️ Warning: Page {page_idx} {item_type} crop failed. Error: {e}. Skipping.")
                        pbar.update(1)
                        continue

                    if item_type == "image":
                        image_save_path_full = os.path.join(FILE_FIGURE_SAVE, f"image_{str(image_id)}.png")
                        image_save_path_relative = f"figures/image_{str(image_id)}.png"
                        crop_image.save(image_save_path_full)

                        pbar.set_postfix_str(f"Page {page_idx+1} (Image {image_id}) VLM...")
                        alt_text = get_response(PROMPT, crop_image)

                        all_data.append({
                            "para_text": {"path": image_save_path_relative, "alt_text": alt_text},
                            "table_id": image_id,
                            "style": "Image"
                        })
                        image_id += 1

                        if "caption" in item:
                            all_data.append({"para_text": item["caption"], "table_id": None, "style": "Caption"})
                    if item_type == "table":
                        table_save_path_full = os.path.join(FILE_TABLE_SAVE, f"table_{str(table_id)}.png")
                        table_save_path_relative = f"tables/table_{str(table_id)}.png"
                        crop_image.save(table_save_path_full)
                        all_data.append({
                            "para_text": {"image_path": table_save_path_relative, "content": item.get("content")},
                            "table_id": table_id,
                            "style": "Table"
                        })
                        table_id += 1

                        if "caption" in item:
                            all_data.append({"para_text": item["caption"], "table_id": None, "style": "Caption"})

                pbar.update(1)

    json_path = os.path.join(FILE_SAVE, f"{PDF_name}.json")
    pickle_path = os.path.join(FILE_SAVE, "data.pkl")

    print(f"\n[{PDF_name}] Saving data to {FILE_SAVE}/...")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    df_data = pd.DataFrame(all_data)

    with open(pickle_path, 'wb') as f:
        pickle.dump(df_data, f)

    print(f"[{PDF_name}] ✅ Success. Data saved to {FILE_SAVE}/")
    return {"pdf_name": PDF_name, "data_head": df_data.head().to_dict()}


def process_single_file(filename, input_root, pdf_root, output_root):
    """
    Wrapper to call PDF loading/saving and data processing in a process pool.
    """
    pdf_base_name = filename.replace("_ocr.json", "").replace(".json", "")
    json_path = os.path.join(input_root, filename)
    pdf_path = Path(os.path.join(pdf_root, pdf_base_name + ".pdf"))

    FILE_SAVE = os.path.join(output_root, pdf_base_name)
    PAGE_IMAGE_OUTPUT_DIR = Path(FILE_SAVE) / "page_images"

    if not os.path.exists(pdf_path):
        print(f"\n[{pdf_base_name}] ❌ Error: PDF not found at {pdf_path}. Skipping.")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        page_image_list = split_and_load_pdf_images_fitz(pdf_path, PAGE_IMAGE_OUTPUT_DIR)

        if page_image_list is None:
            return None

        result = get_preprocess_json(data, pdf_base_name, page_image_list, output_root)

        return result

    except json.JSONDecodeError:
        print(f"\n[{pdf_base_name}] ❌ Error: Failed to parse JSON {json_path}. Skipping.")
        return None
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n[{pdf_base_name}] ❌ Unexpected Error: {e}. Skipping. Details:\n{error_detail}")
        return None

def main():
    """
    Main function: parses command line and uses ProcessPoolExecutor to process files in parallel.
    """
    parser = argparse.ArgumentParser(description="Process structured JSON data to extract images, generate descriptions, and output unified data formats (JSON/PKL) using parallel processing.")
    parser.add_argument('--input_root', type=str, required=True, 
                        help="Root directory containing the input JSON files.")
    parser.add_argument('--output_root', type=str, required=True, 
                        help="Root directory where the processed output (JSON, PKL, figures, tables) will be stored.")
    parser.add_argument('--pdf_root', type=str, required=True,
                        help="Root directory containing the source PDF files (name should match JSON base name).")
    parser.add_argument('--max_workers', type=int, default=4,
                        help="Maximum number of worker processes (default: 4).")

    args = parser.parse_args()

    input_root = args.input_root
    output_root = args.output_root
    pdf_root = args.pdf_root
    max_workers = args.max_workers

    os.makedirs(output_root, exist_ok=True)

    print(f"--- Starting Parallel Processing ---")
    print(f"Input JSON Directory: {input_root}")
    print(f"Source PDF Directory: {pdf_root}")
    print(f"Output Directory: {output_root}")
    print(f"Maximum Worker Processes: {max_workers}")
    print("------------------------------------")

    all_json_files = [f for f in os.listdir(input_root) if f.endswith(".json")]

    files_to_process = []
    skipped_count = 0

    print("--- Checking for existing output files (data.pkl) and page image folders (page_images) ---")
    for filename in all_json_files:
        pdf_base_name = filename.replace("_ocr.json", "").replace(".json", "")

        target_pkl_path = Path(output_root) / pdf_base_name / "data.pkl"
        target_page_images_dir = Path(output_root) / pdf_base_name / "page_images"

        if target_pkl_path.is_file() and target_page_images_dir.is_dir():
            print(f"[{pdf_base_name}] ⏩ data.pkl and page_images dir exist, skipping.")
            skipped_count += 1
        else:
            files_to_process.append(filename)

    total_files = len(all_json_files)
    process_count = len(files_to_process)

    print(f"Found {total_files} JSON files in total.")
    print(f"{skipped_count} files already processed and skipped (both data.pkl and page_images exist).")
    print(f"{process_count} files remaining to process.")
    print("------------------------------------")

    if process_count == 0:
        print("All files have been processed. Exiting.")
        return

    with ProcessPoolExecutor(max_workers=max_workers) as executor:

        future_to_file = {
            executor.submit(process_single_file, filename, input_root, pdf_root, output_root): filename
            for filename in files_to_process
        }

        first_result_shown = False

        for future in tqdm(as_completed(future_to_file), total=process_count, desc="Pending files progress"):
            filename = future_to_file[future]

            try:
                result = future.result()
                if result is not None and not first_result_shown:
                    pdf_base_name = result['pdf_name']
                    data_head = result['data_head']
                    print(f"\n--- Temporary DataFrame structured data (from {pdf_base_name} - Example) ---")
                    df_temp = pd.DataFrame(data_head)
                    print(df_temp)
                    first_result_shown = True

            except Exception as exc:
                print(f'\nException occurred while processing file {filename}: {exc}')

    print("\n--- All pending files processed. ---")

if __name__ == "__main__":
    main()