# sandbox/server/backends/tools/doc_tool.py
"""
Document QA API 工具

提供 search 和 read 两个工具，用于文档问答
"""

import base64
import json
import logging
import os
import time
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple, Union
from xml.dom import minidom

# PIL 是可选依赖
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

# OpenAI 客户端
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from . import register_api_tool
from ..error_codes import ErrorCode
from .base_tool import BaseApiTool, ToolBusinessError

logger = logging.getLogger("DocTool")


def process_image(image_path: str) -> Tuple[str, str, Optional[str]]:
    """处理图片，返回 media_type, base64_image, error_msg"""
    try:
        if not os.path.exists(image_path):
            return "", "", f"File not found: {image_path}"

        _, extension = os.path.splitext(image_path)
        extension = extension.lower()

        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
        }

        media_type = media_types.get(extension)
        if not media_type:
            return "", "", f"Unsupported image format: {extension}"

        image_size = os.path.getsize(image_path) / 1024.0 / 1024.0  # size in MB
        if image_size > 1 and extension != ".jpg" and PIL_AVAILABLE:
            compress_image_path = image_path[:-4] + "_compressed.jpg"
            if not os.path.exists(compress_image_path) and Image:
                img = Image.open(image_path)
                img.save(compress_image_path)
            image_path = compress_image_path
            media_type = "image/jpeg"

        with open(image_path, "rb") as image_file:
            binary_data = image_file.read()
            base64_image = base64.b64encode(binary_data).decode("utf-8")

        return media_type, base64_image, None

    except Exception as e:
        return "", "", f"Error processing image: {str(e)}"


def make_snippet(text: str, keyword: str, max_snippet_length: int = 512) -> str:
    """生成包含关键词的文本片段"""
    if not text or not keyword:
        return ""

    text_lower = text.lower()
    keyword_lower = keyword.lower()
    klen = len(keyword)

    positions = []
    start_pos = 0

    while True:
        idx = text_lower.find(keyword_lower, start_pos)
        if idx == -1:
            break
        positions.append(idx)
        start_pos = idx + klen

    if not positions:
        return ""

    half = max_snippet_length // 2
    windows = []
    for idx in positions:
        start = max(0, idx - half)
        end = min(len(text), idx + klen + half)
        windows.append([start, end])

    windows.sort()
    merged = [windows[0]]

    for s, e in windows[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1][1] = max(last_e, e)
        else:
            merged.append([s, e])

    snippets = []
    for start, end in merged:
        while start > 0 and not text[start - 1].isspace():
            start -= 1
        while end < len(text) and not text[end:end+1].isspace():
            end += 1

        snippet = text[start:end]

        if start > 0:
            snippet = " ... " + snippet
        if end < len(text):
            snippet = snippet + " ... "

        snippets.append(snippet.strip())

    return "\n".join(snippets)


def extract_image_and_table_items(root: ET.Element) -> List[Dict[str, Any]]:
    """从 XML 元素中提取图片和表格信息"""
    items = []
    for child in root.iter():
        if child.tag == "Image":
            caption = child.findtext("Caption")
            alt_text = child.findtext("Alt_Text")

            items.append({
                "type": "Image",
                "page_num": child.get("page_num"),
                "image_id": child.get("image_id"),
                "caption": (caption or "").strip(),
                "alt_text": (alt_text or "").strip()
            })

        elif child.tag == "HTML_Table":
            items.append({
                "type": "HTML_Table",
                "page_num": child.get("page_num"),
                "table_id": child.get("table_id"),
                "text": (child.text or "").strip()
            })

    return items


def get_page_numbers_from_section(section: ET.Element) -> List[int]:
    """从 section 中提取所有页码"""
    pages = set()
    for node in section.iter():
        page_num = node.get("page_num")
        if page_num is not None:
            pages.add(int(float(page_num)))
    return sorted(pages)


GET_USEFUL_INFO_PROMPT = """Now you need to process the following document content (text) together with all previously provided visual inputs, including images, tables and pages, and extract relevant information based on the user goal.

## Document Content
{document_content}

## User Goal
{goal}

Before producing the final output, you must perform a careful and thorough analysis to complete the following tasks:

## Task Guidelines

1. Content Scanning for Rationale  
   Locate the specific text snippets and/or visual data (from images and tables) that are directly related to the user's goal within the document content and the previously provided visual inputs.

2. Key Extraction for Evidence  
   Identify and extract the most relevant information from both the textual content and the visual content.  
   You must not miss any important information.  
   Output the full original context of the evidence as completely as possible.  
   The evidence may contain more than three fragments.

3. Summary Output  
   Organize the extracted information into a concise, logically structured summary.  
   Prioritize clarity and explicitly judge how each piece of information contributes to achieving the user's goal.

## Final Output Format

You must return the result in JSON format with the following fields:
- "rational"
- "evidence"
- "summary"
In the final JSON output, the values should not use any special formatting structure. Simply concatenate the content in plain Markdown format.

The final JSON must be wrapped inside the following tags:

<json>
[YOUR_JSON_OUTPUT]
</json>
""".strip()


class VLMClient:
    """负责调用视觉语言模型 API，处理文档内容并返回有用信息"""
    
    def __init__(
        self, 
        model: str, 
        api_key: Optional[str], 
        api_url: Optional[str], 
        max_tokens: int = 16 * 1024,
        timeout: int = 300,
        retry_max_attempts: int = 10
    ):
        self.model = model
        self.api_key = api_key
        self.api_url = api_url
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_max_attempts = retry_max_attempts
    
    def call_llm(self, messages: List[Dict[str, Any]]) -> str:
        """
        调用 OpenAI API 处理消息
        
        Args:
            messages: 包含文本和图片的消息列表
            
        Returns:
            LLM 返回的文本内容
        """
        if not OPENAI_AVAILABLE or openai is None:
            raise ToolBusinessError("openai package is not available", ErrorCode.EXECUTION_ERROR)
        
        if not self.model:
            raise ToolBusinessError("VLM model not configured", ErrorCode.EXECUTION_ERROR)
        
        if not self.api_key:
            raise ToolBusinessError("VLM API key not configured", ErrorCode.EXECUTION_ERROR)
        
        client = openai.OpenAI(api_key=self.api_key, base_url=self.api_url)
        
        last_error = None
        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                )
                response_content = response.choices[0].message.content
                if response_content:
                    logger.debug(f"[VLM Response] Attempt {attempt} succeeded")
                    # 参考原始实现，打印响应内容用于调试
                    logger.debug(f"[LLM RESPONSE]: {response_content}")
                    return response_content.strip()
                else:
                    raise ToolBusinessError("Empty response from VLM API", ErrorCode.EXECUTION_ERROR)
            except Exception as e:
                last_error = str(e)
                logger.warning(f"[LLM CLIENT ERROR]: {e}, retrying {attempt}/{self.retry_max_attempts} ...")
                if attempt < self.retry_max_attempts:
                    time.sleep(1)
        
        raise ToolBusinessError(
            f"Failed to call VLM API after {self.retry_max_attempts} attempts. Last error: {last_error}",
            ErrorCode.EXECUTION_ERROR
        )
    
    def get_useful_info(self, section_id: str, goal: str, messages: List[Dict[str, Any]]) -> str:
        """
        调用 VLM 处理文档内容并解析返回的有用信息
        
        Args:
            section_id: 文档 section ID
            goal: 用户目标/问题
            messages: 包含文档内容和图片的消息列表
            
        Returns:
            格式化的有用信息字符串，包含 evidence 和 summary
        """
        for retry in range(self.retry_max_attempts):
            try:
                # 调用 LLM API
                response = self.call_llm(messages)
                
                # 解析 JSON 响应（从 <json>...</json> 标签中提取）
                if "<json>" in response and "</json>" in response:
                    json_str = response.split("<json>")[-1].split("</json>")[0].strip()
                else:
                    # 如果没有标签，尝试直接解析整个响应
                    json_str = response.strip()
                
                response_json = json.loads(json_str)
                
                # 格式化返回结果
                useful_info = f"The useful information from the document section (section_id={section_id}) for user goal `{goal}` is as follows: \n\n"
                useful_info += f"Evidence in document: \n{str(response_json.get('evidence', ''))}\n\n"
                useful_info += f"Summary: \n{str(response_json.get('summary', ''))}"
                
                return useful_info
                
            except json.JSONDecodeError as e:
                logger.warning(f"[GET USEFUL INFO ERROR]: {e}, retrying {retry+1}/{self.retry_max_attempts} ...")
                if retry < self.retry_max_attempts - 1:
                    time.sleep(1)
            except ToolBusinessError:
                # 如果是业务错误（如 API 调用失败），直接抛出
                raise
            except Exception as e:
                logger.warning(f"[GET USEFUL INFO ERROR]: {e}, retrying {retry+1}/{self.retry_max_attempts} ...")
                if retry < self.retry_max_attempts - 1:
                    time.sleep(1)
        
        # 如果所有重试都失败，返回错误信息
        useful_info = f"The useful information from the document section (section_id={section_id}) for user goal `{goal}` is as follows: \n\n"
        useful_info += "Evidence in document: \nThe provided document section could not be processed by the VLM. Please check the section ID and try again.\n\n"
        useful_info += "Summary: \nThe document section could not be processed, and therefore, no information is available."
        
        return useful_info


class DocTool:
    """文档工具类，用于加载和处理文档 XML"""
    
    def __init__(self, seed_path: str):
        self.seed_path = seed_path
        self.outline_root: Optional[ET.Element] = None
        self.content_root: Optional[ET.Element] = None
        self.section_dict: Dict[str, ET.Element] = {}
        self.image_path_dict: Dict[str, str] = {}
        self.table_image_path_dict: Dict[str, str] = {}
        
        self._load_documents()
    
    def _load_documents(self):
        """加载 outline.xml 和 all_content.xml"""
        outline_path = os.path.join(self.seed_path, "outline.xml")
        content_path = os.path.join(self.seed_path, "all_content.xml")
        
        if not os.path.exists(outline_path):
            raise ToolBusinessError(f"outline.xml not found at {outline_path}", ErrorCode.EXECUTION_ERROR)
        if not os.path.exists(content_path):
            raise ToolBusinessError(f"all_content.xml not found at {content_path}", ErrorCode.EXECUTION_ERROR)
        
        try:
            self.outline_root = ET.parse(outline_path).getroot()
            self.content_root = ET.parse(content_path).getroot()
            
            # 构建 section_dict
            for section in self.content_root.iter("Section"):
                section_id = section.get("section_id")
                if section_id:
                    self.section_dict[section_id] = section
            
            # 构建 image_path_dict 和 table_image_path_dict
            # 从 data.pkl 中读取（如果需要），或者从 XML 中提取
            # 这里简化处理，假设图片路径可以从 image_id 推断
            
        except Exception as e:
            raise ToolBusinessError(f"Failed to load documents: {str(e)}", ErrorCode.EXECUTION_ERROR)
    
    def get_section_content(self, section_id: str) -> Optional[ET.Element]:
        """获取指定 section 的内容"""
        return self.section_dict.get(section_id)
    
    def get_image(self, image_id: str) -> Tuple[str, str, Optional[str]]:
        """获取图片的 base64 编码"""
        # 尝试从 figures 文件夹中查找图片
        figures_dir = os.path.join(self.seed_path, "figures")
        if os.path.exists(figures_dir):
            # 优先查找压缩版本（更小）
            possible_names = [
                f"image_{image_id}_compressed.jpg",
                f"image_{image_id}.jpg",
                f"image_{image_id}.png",
            ]
            
            for name in possible_names:
                image_path = os.path.join(figures_dir, name)
                if os.path.exists(image_path):
                    return process_image(image_path)
        
        return "", "", f"Image {image_id} not found"
    
    def get_page_image(self, page_num: int) -> Tuple[str, str, Optional[str]]:
        """获取页面图片的 base64 编码"""
        page_images_dir = os.path.join(self.seed_path, "page_images")
        if not os.path.exists(page_images_dir):
            return "", "", f"page_images directory not found"
        
        # 尝试多种可能的文件名格式，优先使用压缩版本
        index_string = "%04d" % (int(page_num) - 1)
        possible_names = [
            f"page_{index_string}_compressed.jpg",
            f"page_{index_string}.jpg",
            f"page_{index_string}.png",
        ]
        
        for name in possible_names:
            image_path = os.path.join(page_images_dir, name)
            if os.path.exists(image_path):
                return process_image(image_path)
        
        return "", "", f"Page {page_num} image not found"
    
    def get_table_image(self, table_id: str) -> Tuple[str, str, Optional[str]]:
        """获取表格图片的 base64 编码"""
        tables_dir = os.path.join(self.seed_path, "tables")
        if not os.path.exists(tables_dir):
            return "", "", f"tables directory not found"
        
        # 尝试查找表格图片
        for ext in [".png", ".jpg"]:
            table_path = os.path.join(tables_dir, f"table_{table_id}{ext}")
            if os.path.exists(table_path):
                return process_image(table_path)
        
        return "", "", f"Table {table_id} image not found"
    
    def single_search(self, key_word: str) -> ET.Element:
        """在文档中搜索关键词"""
        key_word = key_word.lower()
        result_root = ET.Element("Search_Result")
        curr_section_id = ""

        for curr in self.content_root.iter():
            if curr.tag == "Section":
                curr_section_id = curr.get("section_id", "")

                # 检查 heading
                if len(curr) > 0 and curr[0].text is not None:
                    if key_word in curr[0].text.lower():
                        item = ET.SubElement(
                            result_root,
                            "Item",
                            type="Section",
                            section_id=curr_section_id,
                            page_num=curr.get("start_page_num", ""),
                        )
                        item.text = curr[0].text

            elif curr.tag == "Paragraph" and curr.text:
                if key_word in curr.text.lower():
                    item = ET.SubElement(
                        result_root,
                        "Item",
                        type=curr.tag,
                        section_id=curr_section_id,
                        page_num=curr.get("page_num", ""),
                    )
                    item.text = make_snippet(curr.text, key_word)

            elif curr.tag == "HTML_Table" and curr.text:
                if key_word in curr.text.lower():
                    item = ET.SubElement(
                        result_root,
                        "Item",
                        type=curr.tag,
                        table_id=curr.get("table_id", ""),
                        section_id=curr_section_id,
                        page_num=curr.get("page_num", ""),
                    )
                    item.text = curr.text

            elif curr.tag == "Image":
                keyword_found = False
                for child in curr:
                    if child.text and key_word in child.text.lower():
                        keyword_found = True
                        break
                
                if keyword_found:
                    item = ET.SubElement(
                        result_root,
                        "Image",
                        type=curr.tag,
                        image_id=curr.get("image_id", ""),
                        section_id=curr_section_id,
                        page_num=curr.get("page_num", ""),
                    )
                    for child in curr:
                        sub_item = ET.SubElement(item, child.tag)
                        sub_item.text = child.text

        return result_root


class SearchTool(BaseApiTool):
    """文档搜索工具"""
    
    def __init__(self):
        super().__init__(tool_name="doc:search", resource_type="doc")
    
    async def execute(
        self,
        key_words: Union[str, List[str]],
        max_search_results: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        在文档中搜索关键词
        
        Args:
            key_words: 关键词（字符串或列表）
            max_search_results: 最大搜索结果数
            **kwargs: 包含 seed_path（从 seed.jsonl 的 kwargs 中传递）等参数
        """
        # 从 kwargs 中获取 seed_path（优先），否则使用配置中的默认值
        seed_path = kwargs.get("seed_path") or self.get_config("seed_path")
        
        if not seed_path:
            raise ToolBusinessError("seed_path must be provided in kwargs (from seed.jsonl)", ErrorCode.EXECUTION_ERROR)
        
        if not os.path.exists(seed_path):
            raise ToolBusinessError(f"Seed path not found: {seed_path}", ErrorCode.EXECUTION_ERROR)
        
        if max_search_results is None:
            max_search_results = self.get_config('max_search_results')
        if max_search_results is None:
            max_search_results = 10
        max_search_results = int(max_search_results)

        if isinstance(key_words, str):
            key_words = [key_words]
        
        doc_tool = DocTool(seed_path)
        search_result = ""

        for key_word in key_words:
            single_search_result = doc_tool.single_search(key_word)
            result_num = len(single_search_result)
            
            if result_num == 0:
                single_search_result = f"We didn't find any section or paragraph that contains the keyword `{key_word}`"
            else:
                if result_num > max_search_results:
                    for subelement in single_search_result[max_search_results:]:
                        single_search_result.remove(subelement)

                single_search_result = ET.tostring(single_search_result, encoding="unicode")
                single_search_result = minidom.parseString(single_search_result).toprettyxml(indent="  ").replace('<?xml version="1.0" ?>\n', '').strip()

            if result_num > max_search_results:
                search_result += f"A Document search for `{key_word}` found {result_num} results. To shorten response, the first {max_search_results} results are listed below:\n\n{single_search_result}"
            else:
                search_result += f"A Document search for `{key_word}` found {result_num} results:\n\n{single_search_result}"
            search_result += "\n\n=============================\n\n"

        search_result = search_result.strip("\n\n=============================\n\n")
        return {"result": search_result}


class ReadTool(BaseApiTool):
    """文档读取工具"""
    
    def __init__(self):
        super().__init__(tool_name="doc:read", resource_type="doc")
    
    def _single_read(
        self,
        doc_tool: DocTool,
        section_id: str,
        goal: str,
        vlm_client: VLMClient,
        max_image_num: int = 10,
        max_text_token: int = 20000
    ) -> str:
        """读取单个 section 并调用 VLM 获取有用信息"""
        visual_num_exceeded = False
        text_token_exceeded = False
        
        if section_id not in doc_tool.section_dict:
            return f"The section_id {section_id} is not presented in the document, here is the full list of available section_id: {list(doc_tool.section_dict.keys())}. Please try again."
        
        # 构建 messages
        messages = [
            {'role': 'system', 'content': [{"type": "text", "text": "You are a helpful assistant."}]},
        ]
        
        xml_section_obj = doc_tool.get_section_content(section_id)
        visual_items = extract_image_and_table_items(xml_section_obj)
        section_text = ET.tostring(xml_section_obj, encoding="unicode")
        section_text = minidom.parseString(section_text).toprettyxml(indent="  ").replace('<?xml version="1.0" ?>\n', '').strip()

        # 检查文本长度
        if len(section_text) > max_text_token:
            text_token_exceeded = True
            section_text = section_text[:max_text_token] + "\n\n... [Document content truncated to comply with maximum text length limit] ..."
        
        page_numbers = get_page_numbers_from_section(xml_section_obj)

        visual_object_infos = []
        # 添加页面图片
        for page_num in page_numbers:
            media_type, base64_image, error_msg = doc_tool.get_page_image(page_num)
            if not error_msg:
                visual_object_infos.append({
                    "type": "Page",
                    "page_num": page_num,
                    "media_type": media_type,
                    "base64_image": base64_image,
                    "error_msg": error_msg
                })

        # 添加图片和表格
        for visual_item in visual_items:
            if visual_item['type'] == 'Image':
                media_type, base64_image, error_msg = doc_tool.get_image(visual_item['image_id'])
                if not error_msg:
                    visual_item.update({
                        'media_type': media_type, 
                        'base64_image': base64_image, 
                        "error_msg": error_msg
                    })
                    visual_object_infos.append(visual_item)
            elif visual_item['type'] == 'HTML_Table':
                media_type, base64_image, error_msg = doc_tool.get_table_image(visual_item['table_id'])
                if not error_msg:
                    visual_item.update({
                        'media_type': media_type, 
                        'base64_image': base64_image, 
                        "error_msg": error_msg
                    })
                    visual_object_infos.append(visual_item)

        # 限制图片数量
        if len(visual_object_infos) > max_image_num:
            visual_object_infos = [item for item in visual_object_infos if item['type'] != 'Page']
            if len(visual_object_infos) > max_image_num:
                visual_object_infos = [item for item in visual_object_infos if item['type'] != 'HTML_Table']
                if len(visual_object_infos) > max_image_num:
                    visual_object_infos = visual_object_infos[:max_image_num]
                    visual_num_exceeded = True

        # 构建 messages：先添加视觉对象，再添加文本
        # global visual first, then local visual, then text with instruction
        for visual_object_info in visual_object_infos:
            if visual_object_info['type'] == 'Page':
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"I have uploaded the full page images for the selected section, corresponding to the following page numbers: {visual_object_info['page_num']}."
                        },
                        {
                            "type": "image_url",
                            "min_pixels": 4*32*32,
                            "max_pixels": 2048*32*32,
                            "image_url": {
                                "url": f"data:{visual_object_info['media_type']};base64,{visual_object_info['base64_image']}"
                            }
                        }
                    ]
                })
            elif visual_object_info['type'] == 'Image':
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"I have uploaded the image with image ID {visual_object_info['image_id']} from the selected section."
                        },
                        {
                            "type": "image_url",
                            "min_pixels": 4*32*32,
                            "max_pixels": 2048*32*32,
                            "image_url": {
                                "url": f"data:{visual_object_info['media_type']};base64,{visual_object_info['base64_image']}"
                            }
                        }
                    ]
                })
            elif visual_object_info['type'] == 'HTML_Table':
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"I have uploaded the table with table ID {visual_object_info['table_id']} from the selected section."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{visual_object_info['media_type']};base64,{visual_object_info['base64_image']}"
                            }
                        }
                    ]
                })

        if visual_num_exceeded:
            messages.append({
                'role': 'user', 
                'content': [{"type": "text", "text": "Note that due to the large number of visual inputs in this section, some visual inputs have been omitted."}]
            })

        if text_token_exceeded:
            messages.append({
                'role': 'user', 
                'content': [{"type": "text", "text": f"Note that the document content has been truncated due to its large size exceeding the {max_text_token} character limit."}]
            })

        # 添加最终的 prompt
        messages.append({
            'role': 'user', 
            'content': [{"type": "text", "text": GET_USEFUL_INFO_PROMPT.format(document_content=section_text, goal=goal)}]
        })

        # 调用 VLM 获取有用信息
        useful_info = vlm_client.get_useful_info(section_id, goal, messages)

        return useful_info
    
    async def execute(
        self,
        section_ids: Union[str, List[str]],
        goal: str,
        max_image_num: Optional[int] = None,
        max_text_token: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        读取文档指定 section 的内容，调用 VLM 获取有用信息
        
        Args:
            section_ids: section ID（字符串或列表）
            goal: 用户目标/问题
            max_image_num: 最大图片数量
            max_text_token: 最大文本长度
            **kwargs: 包含 seed_path（从 seed.jsonl 的 kwargs 中传递）等参数
        """
        # 从 kwargs 中获取 seed_path（优先），否则使用配置中的默认值
        seed_path = kwargs.get("seed_path") or self.get_config("seed_path")
        
        if not seed_path:
            raise ToolBusinessError("seed_path must be provided in kwargs (from seed.jsonl)", ErrorCode.EXECUTION_ERROR)
        
        if not os.path.exists(seed_path):
            raise ToolBusinessError(f"Seed path not found: {seed_path}", ErrorCode.EXECUTION_ERROR)
        
        if max_image_num is None:
            max_image_num = self.get_config('max_image_num')
        if max_image_num is None:
            max_image_num = 10
        max_image_num = int(max_image_num)

        if max_text_token is None:
            max_text_token = self.get_config('max_text_token')
        if max_text_token is None:
            max_text_token = 20000
        max_text_token = int(max_text_token)

        if isinstance(section_ids, str):
            section_ids = [section_ids]
        
        # 从配置中获取 VLM 参数
        vlm_model = self.get_config('vlm_model') or os.getenv('VLM_MODEL')
        vlm_api_key = self.get_config('vlm_api_key') or os.getenv('VLM_API_KEY') or os.getenv('OPENAI_API_KEY')
        vlm_api_url = self.get_config('vlm_api_url') or os.getenv('VLM_API_URL') or os.getenv('OPENAI_API_URL')
        vlm_max_tokens = self.get_config('vlm_max_tokens', 16 * 1024)
        vlm_timeout = self.get_config('vlm_timeout', 300)
        vlm_retry_max_attempts = self.get_config('vlm_retry_max_attempts', 10)
        
        if not vlm_model:
            raise ToolBusinessError("VLM model not configured. Please set 'vlm_model' in config or VLM_MODEL environment variable", ErrorCode.EXECUTION_ERROR)
        
        if not vlm_api_key:
            raise ToolBusinessError("VLM API key not configured. Please set 'vlm_api_key' in config or VLM_API_KEY/OPENAI_API_KEY environment variable", ErrorCode.EXECUTION_ERROR)
        
        # 创建 VLM 客户端
        vlm_client = VLMClient(
            model=vlm_model,
            api_key=vlm_api_key,
            api_url=vlm_api_url,
            max_tokens=vlm_max_tokens,
            timeout=vlm_timeout,
            retry_max_attempts=vlm_retry_max_attempts
        )
        
        doc_tool = DocTool(seed_path)
        read_result = ""

        for section_id in section_ids:
            try:
                single_read_result = self._single_read(
                    doc_tool=doc_tool,
                    section_id=section_id,
                    goal=goal,
                    vlm_client=vlm_client,
                    max_image_num=max_image_num,
                    max_text_token=max_text_token
                )
                read_result += single_read_result.strip()
                read_result += "\n\n=============================\n\n"
            except Exception as e:
                read_result += f"[ERROR] Section {section_id} read failed: {str(e)}\n\n=============================\n\n"

        read_result = read_result.strip("\n\n=============================\n\n")
        return {"result": read_result}


# 注册工具
search = register_api_tool(
    name="doc:search",
    config_key="doc",
    description="在文档中搜索关键词"
)(SearchTool())

read = register_api_tool(
    name="doc:read",
    config_key="doc",
    description="读取文档指定 section 的内容，调用 VLM 获取有用信息并返回给 agent"
)(ReadTool())
