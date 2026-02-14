import base64
import copy
import glob
import os
import xml.etree.ElementTree as ET
from typing import Optional, Tuple
import sys  # import sys module

import pandas as pd
from PIL import Image

# Try to import tqdm for progress bar
try:
    from tqdm import tqdm
except ImportError:
    # If tqdm is not installed, provide a dummy tqdm to avoid errors
    def tqdm(iterable, *args, **kwargs):
        return iterable
    print("Warning: tqdm not installed. Install it with 'pip install tqdm' for progress bar.")

class DocReader:
    def __init__(self, data_path, max_section_depth=10):
        self.data_path = data_path
        self.data = pd.read_pickle(self.data_path + "/data.pkl")

        prev_heading_num = 0
        self.root = ET.Element("Document")
        prev_node = self.root
        stack = [(prev_node, prev_heading_num)]
        self.image_count, self.table_count, self.para_count = 0, 0, 0

        self.section_dict = dict()
        self.image_path_dict = dict()
        self.table_image_path_dict = dict()
        prev_section_id = ""  # Root section id
        self.num_page = len(glob.glob(self.data_path + "/page_images/*.png"))
        self.max_section_depth = max_section_depth

        index = 0
        curr_page_num = 1
        # If the first element is not a heading, create a default Section node as root's first child
        if not self.data.iloc[0]["style"].startswith("Heading"):
            curr_section_id = "1"
            curr_node = ET.SubElement(
                prev_node,
                "Section",
                section_id=curr_section_id,
                start_page_num=str(curr_page_num),
            )

            self.section_dict[curr_section_id] = curr_node
            stack.append([curr_node, 1])

            prev_section_id = curr_section_id
            prev_node = curr_node

        while index < len(self.data):
            row = self.data.iloc[index]

            if row["style"].startswith("Heading"):
                curr_heading_num = int(row["style"].split()[1])

                # If the current heading has higher level (smaller number), pop the stack until matching hierarchy
                while curr_heading_num < stack[-1][1]:
                    stack[-1][0].set("end_page_num", str(curr_page_num))
                    stack.pop()
                    prev_section_id_list = prev_section_id.split(".")
                    prev_section_id = ".".join(prev_section_id_list[:-1])

                # If the current heading has the same level as previous, create a sibling section
                if curr_heading_num == stack[-1][1]:
                    stack[-1][0].set("end_page_num", str(curr_page_num))
                    curr_section_id_list = prev_section_id.split(".")
                    curr_section_id_list[-1] = str(int(curr_section_id_list[-1]) + 1)
                    curr_section_id = ".".join(curr_section_id_list)
                    prev_node = stack[-2][0]

                    curr_node = ET.SubElement(
                        prev_node,
                        "Section",
                        section_id=curr_section_id,
                        start_page_num=str(curr_page_num),
                    )
                    self.section_dict[curr_section_id] = curr_node
                    heading = ET.SubElement(curr_node, "Heading")
                    heading.text = row["para_text"].strip()

                    stack[-1][0] = curr_node

                else:
                    # If the current heading is lower (deeper nesting), create a sub-section unless max depth exceeded
                    if len(stack) <= self.max_section_depth:
                        prev_node = stack[-1][0]
                        curr_section_id = prev_section_id + ".1"
                        curr_node = ET.SubElement(
                            prev_node,
                            "Section",
                            section_id=curr_section_id,
                            start_page_num=str(curr_page_num),
                        )
                        self.section_dict[curr_section_id] = curr_node
                        heading = ET.SubElement(curr_node, "Heading")
                        heading.text = row["para_text"].strip()

                        stack.append([curr_node, curr_heading_num])
                    else:
                        # If section nesting is too deep, treat as paragraph to avoid excessive depth
                        content = row["para_text"]
                        while (
                            index + 1 < len(self.data)
                            and self.data.iloc[index + 1]["style"]
                               in ["Text", "Phonetic", "Image_caption", "Image_footnote", "Table_caption", "Table_footnote", "Code", "Code_caption", "Algorithm", "Reference", "List", "Equation", "Equation_block", "Aside_text", "Page_number", "Page_footnote", "Ref_text"]
                        ):
                            index += 1
                            content = content + " " + self.data.iloc[index]["para_text"]

                        para = ET.SubElement(
                            prev_node, "Paragraph", page_num=str(curr_page_num)
                        )
                        para.text = content

                        self.para_count += 1
                        index += 1
                        continue  # Skip updating prev_node and prev_section_id

                prev_section_id = curr_section_id
                prev_node = curr_node

            elif row["style"] in ["Text", "Phonetic", "Image_caption", "Image_footnote", "Table_caption", "Table_footnote", "Code", "Code_caption", "Algorithm", "Reference", "List", "Equation", "Equation_block", "Aside_text", "Page_number", "Page_footnote", "Ref_text"]:
                curr_style = row["style"]
                content = row["para_text"]
                while (
                    index + 1 < len(self.data)
                    and self.data.iloc[index + 1]["style"] == curr_style
                ):
                    index += 1
                    content = content + " " + self.data.iloc[index]["para_text"]

                para = ET.SubElement(
                    prev_node, "Paragraph", page_num=str(curr_page_num)
                )
                para.text = content

                self.para_count += 1

            elif row["style"] == "Image":
                item = row["para_text"]
                image = ET.SubElement(
                    prev_node,
                    "Image",
                    image_id=str(self.image_count),
                    page_num=str(curr_page_num),
                )
                self.image_path_dict[str(self.image_count)] = os.path.basename(
                    item["path"]
                )

                if item["alt_text"] is not None:
                    alt_text = ET.SubElement(image, "Alt_Text")
                    alt_text.text = str(item["alt_text"])

                self.image_count += 1

            elif row["style"] == "Table":
                if len(row["para_text"]) == 0 or "content" not in row["para_text"]:
                    index += 1
                    continue
                table = ET.SubElement(
                    prev_node,
                    "HTML_Table",
                    table_id=str(self.table_count),
                    page_num=str(curr_page_num),
                )

                table.text = row["para_text"]["content"]
                if "image_path" in row["para_text"]:
                    self.table_image_path_dict[str(self.table_count)] = row["para_text"]["image_path"]
                self.table_count += 1

            elif row["style"] in ["Caption", "Image_caption", "Table_caption", "Code_caption"]:
                prev_row = self.data.iloc[index - 1]
                if prev_row["style"] == "Image":
                    caption = ET.SubElement(image, "Caption")
                # If you want to add caption for table, uncomment below code
                # if prev_row["style"] == "Table":
                #     caption = ET.SubElement(table, "Caption")
                else:
                    caption = ET.SubElement(prev_node, "Caption")

                caption.text = str(row["para_text"])

            elif row["style"] == "Page_Start":
                curr_page_num = row["table_id"] + 1

            elif row["style"] == "Title":
                content = row["para_text"]
                para = ET.SubElement(prev_node, "Title", page_num=str(curr_page_num))
                para.text = content

            elif row["style"] in ["Header", "Footer"]:
                pass

            else:
                print("Uncovered style:", row["style"])
                raise Exception
            index += 1
        for i in range(len(stack)):
            if stack[i][0].tag == "Section":
                stack[i][0].set("end_page_num", str(curr_page_num))

    def get_outline_root(
        self, skip_para_after_page=100, disable_caption_after_page=False
    ):
        def iterator(parent):
            for child in reversed(parent):
                if len(child) >= 1 and child.tag == "Section":
                    iterator(child)
                if child.tag == "Paragraph":
                    # Remove paragraphs whose page number is greater than skip_para_after_page to avoid an excessively long outline
                    if int(float(child.get("page_num"))) > skip_para_after_page:
                        parent.remove(child)
                    else:
                        # For paragraphs: extract first sentence as an attribute
                        if child.text:
                            child.set("first_sentence", child.text.split(". ", 1)[0])
                        child.text = None

                if child.tag == "HTML_Table":
                    # Clear table content for tables after skip_para_after_page to save outline length
                    if int(float(child.get("page_num"))) > skip_para_after_page:
                        child.text = None

                if child.tag == "Image":
                    # For image nodes, extract first sentence of Alt_Text as an attribute
                    alt_text_node = child.find("Alt_Text")

                    if alt_text_node is not None and alt_text_node.text is not None:
                        original_alt_text = alt_text_node.text.strip()
                        first_sentence = original_alt_text.split(". ", 1)[0].strip()
                        # If the original alt_text has a period, make sure punctuation is at the end of attribute
                        if ". " in original_alt_text and not first_sentence.endswith(('.', '?', '!')):
                            first_sentence += '.'
                        child.set("first_sentence_of_image_description", first_sentence)
                        # Remove Alt_Text node to keep outline short
                        child.remove(alt_text_node)

                    if disable_caption_after_page:
                        if int(float(child.get("page_num"))) > disable_caption_after_page:
                            for sub_child in child:
                                if sub_child.tag == "Caption" and sub_child.text is not None:
                                    # Truncate caption text to 20 characters to limit context length
                                    sub_child.text = sub_child.text[:20]

        root = copy.deepcopy(self.root)
        root.tag = "Outline"
        iterator(root)

        return root


if __name__ == "__main__":

    # Get prepress_root from command line arguments
    if len(sys.argv) < 2:
        print("Error: Missing argument. Please provide the path to prepress_root.")
        print(f"Usage: python {sys.argv[0]} <prepress_root_path>")
        sys.exit(1)

    prepress_root = sys.argv[1]

    if not os.path.isdir(prepress_root):
        print(f"Error: prepress_root path not found or is not a directory: {prepress_root}")
        sys.exit(1)

    # Iterate over all subfolders in prepress_root
    subdirs = [d for d in os.listdir(prepress_root) if os.path.isdir(os.path.join(prepress_root, d))]

    for subdir in tqdm(subdirs, desc="Processing Documents"):
        subdir_path = os.path.join(prepress_root, subdir)

        data_pkl_path = os.path.join(subdir_path, "data.pkl")
        if not os.path.exists(data_pkl_path):
            tqdm.write(f"Warning: data.pkl not found in {subdir_path}. Skipping.")
            continue

        try:
            document = DocReader(data_path=subdir_path)

            outline_root = document.get_outline_root(skip_para_after_page=100, disable_caption_after_page=False)
            output_path_outline = os.path.join(subdir_path, "outline.xml")

            outline_tree = ET.ElementTree(outline_root)
            outline_tree.write(output_path_outline, encoding="utf-8", xml_declaration=True)

            output_path_all = os.path.join(subdir_path, "all_content.xml")
            full_tree = ET.ElementTree(document.root)
            full_tree.write(output_path_all, encoding="utf-8", xml_declaration=True)

            tqdm.write(f"Successfully processed {subdir}: Saved outline.xml and all_content.xml")

        except Exception as e:
            tqdm.write(f"Error processing {subdir_path}: {e}")
            continue