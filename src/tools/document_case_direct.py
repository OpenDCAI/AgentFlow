import os
import copy
import xml.etree.ElementTree as ET
from .document_tools import format_xml_element, get_case_document_adapter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def _safe_float(value):
    try:
        return float(value)
    except Exception:
        return None

def _find_outline_path():
    xml_dir = os.path.join(REPO_ROOT, "case", "test_xml")
    if not os.path.isdir(xml_dir):
        return None
    files = [os.path.join(xml_dir, n) for n in os.listdir(xml_dir) if n.lower().endswith(".xml")]
    return files[0] if files else None

def get_outline_xml(outline_path=None, skip_para_after_page=100, disable_caption_after_page=False):
    path = outline_path or _find_outline_path()
    if not path or not os.path.exists(path):
        return ""
    tree = ET.parse(path)
    root = tree.getroot()
    root_copy = copy.deepcopy(root)
    for parent in root_copy.iter():
        for child in list(parent):
            if child.tag == "Paragraph":
                pv = _safe_float(child.get("page_num"))
                if pv is not None and pv > skip_para_after_page:
                    parent.remove(child)
            elif child.tag == "Image" and disable_caption_after_page:
                pv = _safe_float(child.get("page_num"))
                if pv is not None and pv > disable_caption_after_page:
                    for sub in child:
                        if sub.tag == "Caption" and sub.text:
                            sub.text = sub.text[:20]
    root_copy.tag = "Outline"
    return format_xml_element(root_copy)

def collect_outline_candidates(outline_path=None):
    path = outline_path or _find_outline_path()
    if not path or not os.path.exists(path):
        return []
    tree = ET.parse(path)
    root = tree.getroot()
    cands = []
    current_section = ""
    current_page = ""
    table_counter = 0
    for node in root.iter():
        if node.tag == "Section":
            current_section = node.get("section_id", current_section)
            current_page = node.get("start_page_num", node.get("page_num", current_page))
            heading = None
            for child in node:
                if child.tag == "Heading":
                    heading = child.text or ""
                    break
            if heading:
                cands.append({"tag":"Section","text":heading,"section_id":current_section,"page_num":current_page,"image_id":"","table_id":""})
            continue
        if node.tag == "Title" and (node.text or "").strip():
            cands.append({"tag":"Title","text":node.text or "","section_id":current_section,"page_num":current_page,"image_id":"","table_id":""})
        elif node.tag == "Paragraph":
            txt = node.get("first_sentence") or node.text or ""
            if txt:
                cands.append({"tag":"Paragraph","text":txt,"section_id":current_section,"page_num":node.get("page_num",""),"image_id":"","table_id":""})
        elif node.tag == "CSV_Table":
            txt = node.text or ""
            if txt:
                cands.append({
                    "tag":"CSV_Table",
                    "text":txt,
                    "section_id":current_section,
                    "page_num":node.get("page_num",""),
                    "image_id":"",
                    "table_id":str(table_counter),
                })
                table_counter += 1
        elif node.tag == "Image":
            image_id = node.get("image_id", "")
            texts = []
            for child in node:
                if child.text:
                    texts.append(child.text)
            caption = " ".join(texts).strip()
            if caption:
                cands.append({"tag":"Image","text":caption,"section_id":current_section,"page_num":node.get("page_num",""),"image_id":image_id,"table_id":""})
    return cands

def resolve_asset_paths(image_id=None, table_id=None):
    adapter = get_case_document_adapter()
    image_path = None
    table_path = None
    if adapter:
        if image_id:
            fn = adapter.image_path_dict.get(str(image_id))
            if fn and adapter.figures_dir:
                image_path = os.path.join(adapter.figures_dir, fn)
        if table_id is not None:
            fn = adapter.table_image_path_dict.get(str(table_id))
            if fn and adapter.tables_dir:
                table_path = os.path.join(adapter.tables_dir, fn)
    return image_path, table_path
