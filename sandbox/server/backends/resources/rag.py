# sandbox/server/backends/resources/rag.py
"""
RAG 后端 - 文档检索服务

提供高性能文档检索功能：
- QueryBatcher: 批量请求收集器，自动聚合多个查询请求
- DenseE5RAGIndex: Faiss + E5 密集检索
- 异步非阻塞接口

配置参数:
- model_name: E5 模型路径或名称
- index_path: Faiss 索引文件路径
- corpus_path: 语料库 JSONL 文件路径
- device: 设备配置（如 "cuda:0" 或 "cuda:0/cuda:1"）
- batcher_trigger_batch_size: 触发批处理的最小请求数（默认 16）
- batcher_max_batch_size: 单批次最大请求数（默认 32）
- batcher_max_wait_time: 最大等待时间（秒，默认 0.05）

使用示例:
```python
from sandbox.server import HTTPServiceServer
from sandbox.server.backends.resources import RAGBackend

server = HTTPServiceServer()
server.load_backend(RAGBackend())
server.run()
```

客户端调用:
```python
async with Sandbox() as sandbox:
    # 显式预热（可选，减少首次调用延迟）
    await sandbox.warmup(["rag"])
    
    # 单条查询
    result = await sandbox.execute("rag:search", {"query": "Python tutorial", "top_k": 10})
    
    # 批量查询
    result = await sandbox.execute("rag:batch_search", {
        "queries": ["Python", "Java", "Go"],
        "top_k": 5
    })
```
"""

import logging
import asyncio
import time
import os
import json
import struct
from typing import Dict, Any, List, Optional, Union, cast, Tuple
from dataclasses import dataclass, field
from collections import deque

import numpy as np
import torch
from tqdm import tqdm

from sandbox.server.backends.base import Backend, BackendConfig
from sandbox.server.core import tool
from sandbox.server.backends.error_codes import ErrorCode, get_error_message
from sandbox.server.backends.response_builder import (
    build_success_response,
    build_error_response,
    ResponseTimer,
)

logger = logging.getLogger("RAGBackend")
index_logger = logging.getLogger("RAGIndex")

# ============================================================================
# RAG Index Core
# ============================================================================

_FAISS_AVAILABLE = True
try:
    import faiss
except ImportError:
    faiss = None  # type: ignore
    _FAISS_AVAILABLE = False


def is_faiss_available() -> bool:
    """检查 Faiss 是否可用"""
    return _FAISS_AVAILABLE


class DiskBasedChunks:
    """
    Lazy loading list-like object for large JSONL files.
    Uses an offset file to jump to specific lines without reading the whole file.
    """
    def __init__(self, jsonl_path: str, offset_path: Optional[str] = None):
        self.jsonl_path = jsonl_path
        if offset_path is None:
            # 尝试多种可能的 offset 文件命名方式
            candidates = []
            if jsonl_path.endswith(".jsonl"):
                # 方式1: wiki_dump.offsets (去掉 .jsonl 后加 .offsets)
                candidates.append(jsonl_path[:-6] + ".offsets")
                # 方式2: wiki_dump.jsonl.offset (在 .jsonl 后加 .offset)
                candidates.append(jsonl_path + ".offset")
                # 方式3: wiki_dump.jsonl.offsets (在 .jsonl 后加 .offsets)
                candidates.append(jsonl_path + ".offsets")
            else:
                candidates.append(jsonl_path + ".offsets")
                candidates.append(jsonl_path + ".offset")

            # 查找第一个存在的 offset 文件
            offset_path = None
            for candidate in candidates:
                if os.path.exists(candidate):
                    offset_path = candidate
                    break

            if offset_path is None:
                raise FileNotFoundError(
                    f"Offset file not found. Tried: {', '.join(candidates)}. "
                    "Please run convert_index.py first."
                )
        self.offset_path = offset_path

        if not os.path.exists(self.jsonl_path):
            raise FileNotFoundError(f"JSONL file not found: {self.jsonl_path}")

        if not os.path.exists(self.offset_path):
            raise FileNotFoundError(
                f"Offset file not found: {self.offset_path}. "
                "Please run convert_index.py first."
            )

        self._offsets = self._load_offsets()
        self._file = open(self.jsonl_path, "rb")

    def _load_offsets(self) -> List[int]:
        """
        加载 offset 文件，支持两种格式：
        1. 二进制格式：每个 offset 是 8 字节的 uint64_t (小端序)
        2. 文本格式：每行是 "offset:length" 格式，只取 offset 部分
        """
        with open(self.offset_path, "rb") as f:
            data = f.read()

        # 检测文件格式：如果前 100 字节都是可打印的 ASCII 字符，则认为是文本格式
        sample = data[:min(100, len(data))]
        is_text = all(32 <= b <= 126 or b in (9, 10, 13) for b in sample)

        if is_text:
            # 文本格式：每行是 "offset:length" 或只有 "offset"
            offsets = []
            for line in data.decode("utf-8").strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                # 支持两种格式： "offset:length" 或 "offset"
                if ":" in line:
                    offset_str = line.split(":", 1)[0]
                else:
                    offset_str = line
                try:
                    offsets.append(int(offset_str))
                except ValueError:
                    index_logger.warning(f"跳过无效的 offset 行: {line}")
                    continue
            index_logger.info(f"从文本格式 offset 文件加载了 {len(offsets):,} 个偏移量")
            return offsets
        else:
            # 二进制格式：每个 offset 是 8 字节的 uint64_t
            count = len(data) // 8
            if len(data) % 8 != 0:
                raise ValueError(
                    f"二进制 offset 文件大小 ({len(data)} 字节) 不是 8 的倍数，"
                    f"可能文件格式不正确或已损坏"
                )
            offsets = list(struct.unpack(f"<{count}Q", data))
            index_logger.info(f"从二进制格式 offset 文件加载了 {len(offsets):,} 个偏移量")
            return offsets

    def __len__(self):
        return len(self._offsets)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start, stop, step = idx.indices(len(self))
            return [self[i] for i in range(start, stop, step)]

        if idx < 0:
            idx += len(self)

        if idx < 0 or idx >= len(self._offsets):
            raise IndexError("DiskBasedChunks index out of range")

        offset = self._offsets[idx]
        self._file.seek(offset)
        line = self._file.readline()
        return json.loads(line.decode("utf-8"))

    def __del__(self):
        if hasattr(self, "_file") and self._file:
            self._file.close()


class DecExEncoder:
    """
    E5/BGE 编码器，支持 Mean Pooling + L2 归一化
    """
    def __init__(self, model_name: str, model_path: str, device: str = "cuda"):
        self.model_name = model_name
        self.device = device

        try:
            from transformers import AutoTokenizer, AutoModel
        except ImportError:
            raise ImportError("DecExEncoder 需要 transformers: pip install transformers")

        index_logger.info(f"正在加载模型: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        self.model.eval()
        self.model.to(self.device)
        index_logger.info(f"模型加载完成，设备: {self.device}")

    def encode(self, query_list: List[str], max_length: int = 512) -> np.ndarray:
        """
        编码文本列表为向量
        """
        if isinstance(query_list, str):
            query_list = [query_list]

        # E5 特有的 query prefix
        if "e5" in self.model_name.lower():
            query_list = [f"query: {q}" for q in query_list]

        inputs = self.tokenizer(
            query_list,
            max_length=max_length,
            padding=True,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            output = self.model(**inputs)
            attention_mask = inputs["attention_mask"]
            last_hidden = output.last_hidden_state.masked_fill(
                ~attention_mask[..., None].bool(), 0.0
            )
            embeddings = last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
            embeddings = torch.nn.functional.normalize(embeddings, dim=-1)

        return embeddings.cpu().numpy().astype(np.float32)


def parse_device_config(device: str) -> Tuple[str, str]:
    """
    解析设备配置字符串
    """
    device = device.strip()

    if "/" in device:
        # 格式: "encoder_device/index_device"
        parts = device.split("/", 1)
        encoder_dev = _normalize_device(parts[0].strip())
        index_dev = _normalize_device(parts[1].strip())
    else:
        # 单设备格式: encoder 使用该设备，index 默认 cpu
        encoder_dev = _normalize_device(device)
        index_dev = "cpu"

    return encoder_dev, index_dev


def _normalize_device(device: str) -> str:
    """
    标准化设备字符串
    """
    if device == "cuda":
        return "cuda:0"
    return device


class DenseE5RAGIndex:
    """
    密集检索索引：Faiss + E5 Encoder
    """
    corpus: Union[List[Dict[str, Any]], DiskBasedChunks]

    def __init__(
        self,
        index_path: str,
        model_name: str,
        corpus_path: str,
        device: str = "cuda:0",
        **kwargs
    ):
        # 解析设备配置
        self.encoder_device, self.index_device = parse_device_config(device)
        self.device_config = device  # 保存原始配置

        self.model_name = model_name
        self.corpus_path = corpus_path
        self.index_path = index_path

        if not _FAISS_AVAILABLE:
            raise ImportError("需要 faiss: pip install faiss-gpu 或 faiss-cpu")

        # 判断是否需要 GPU 索引
        use_gpu_index = "cuda" in self.index_device

        # 1. 加载 Faiss 索引
        self.index = self._load_faiss_index(index_path, self.index_device, use_gpu_index)

        # 2. 加载 Encoder
        self.encoder = DecExEncoder(model_name, model_path=model_name, device=self.encoder_device)

        # 3. 加载语料库
        self.corpus = self._load_corpus(corpus_path)

        index_logger.info(f"初始化完成，索引向量数: {self.index.ntotal:,}")
        index_logger.info(f"Encoder 设备: {self.encoder_device}, Index 设备: {self.index_device}")

    def _load_faiss_index(self, index_path: str, index_device: str, use_gpu_index: bool):
        """加载 Faiss 索引"""
        index_logger.info(f"加载 Faiss 索引: {index_path}")

        # 尝试 mmap 加载
        try:
            io_flags = faiss.IO_FLAG_MMAP | faiss.IO_FLAG_READ_ONLY  # type: ignore
            index = faiss.read_index(index_path, io_flags)  # type: ignore
            index_logger.info("成功启用 Memory Mapping (mmap)")
        except Exception as e:
            index_logger.warning(f"mmap 加载失败，回退到普通加载: {e}")
            index = faiss.read_index(index_path)  # type: ignore

        # GPU 加载（可选）
        if use_gpu_index and "cuda" in index_device:
            # 从设备字符串提取 GPU ID（如 "cuda:1" -> 1）
            gpu_id = self._parse_gpu_id(index_device)
            index_size_gb = os.path.getsize(index_path) / (1024**3)

            # 检测 GPU 显存并决定是否加载
            can_load, reason = self._check_gpu_memory(gpu_id, index_size_gb)

            if can_load and hasattr(faiss, "StandardGpuResources"):
                try:
                    res = faiss.StandardGpuResources()  # type: ignore
                    index = faiss.index_cpu_to_gpu(res, gpu_id, index)  # type: ignore
                    index_logger.info(f"Faiss 索引已迁移到 GPU:{gpu_id}")
                except Exception as e:
                    index_logger.warning(f"GPU 迁移失败，继续使用 CPU: {e}")
            else:
                index_logger.info(reason)

        return index

    @staticmethod
    def _check_gpu_memory(gpu_id: int, index_size_gb: float, max_ratio: float = 0.8) -> Tuple[bool, str]:
        """
        检查 GPU 显存是否足够加载索引
        """
        try:
            if not torch.cuda.is_available():
                return False, "CUDA 不可用，使用 CPU"

            if gpu_id >= torch.cuda.device_count():
                return False, f"GPU:{gpu_id} 不存在，使用 CPU"

            # 获取 GPU 显存信息
            props = torch.cuda.get_device_properties(gpu_id)
            total_memory_gb = props.total_memory / (1024**3)

            # 获取当前可用显存
            torch.cuda.set_device(gpu_id)
            free_memory = torch.cuda.memory_reserved(gpu_id) - torch.cuda.memory_allocated(gpu_id)
            # 更准确的方式：使用 nvidia-smi 获取的空闲显存
            try:
                free_memory_gb = (torch.cuda.get_device_properties(gpu_id).total_memory -
                                  torch.cuda.memory_allocated(gpu_id)) / (1024**3)
            except Exception:
                free_memory_gb = total_memory_gb * 0.9  # 假设 90% 可用

            # 计算是否可以加载
            max_allowed_gb = total_memory_gb * max_ratio

            if index_size_gb <= max_allowed_gb:
                index_logger.info(
                    f"GPU:{gpu_id} 显存: {total_memory_gb:.1f}GB, "
                    f"索引: {index_size_gb:.1f}GB ({index_size_gb/total_memory_gb*100:.0f}%)"
                )
                return True, ""
            else:
                return False, (
                    f"索引 ({index_size_gb:.1f}GB) 超过 GPU:{gpu_id} 显存限制 "
                    f"({max_allowed_gb:.1f}GB = {total_memory_gb:.1f}GB × {max_ratio:.0%})，使用 CPU"
                )

        except Exception as e:
            return False, f"GPU 检测失败: {e}，使用 CPU"

    @staticmethod
    def _parse_gpu_id(device: str) -> int:
        """
        从设备字符串解析 GPU ID
        """
        if ":" in device:
            try:
                return int(device.split(":")[1])
            except (ValueError, IndexError):
                return 0
        return 0

    def _load_corpus(self, corpus_path: str) -> Union[List[Dict[str, Any]], DiskBasedChunks]:
        """加载语料库"""
        index_logger.info(f"加载语料库: {corpus_path}")

        # 尝试多种可能的 offset 文件命名方式
        offset_candidates = []
        if corpus_path.endswith(".jsonl"):
            # 方式1: wiki_dump.offsets (去掉 .jsonl 后加 .offsets)
            offset_candidates.append(corpus_path[:-6] + ".offsets")
            # 方式2: wiki_dump.jsonl.offset (在 .jsonl 后加 .offset)
            offset_candidates.append(corpus_path + ".offset")
            # 方式3: wiki_dump.jsonl.offsets (在 .jsonl 后加 .offsets)
            offset_candidates.append(corpus_path + ".offsets")
        else:
            offset_candidates.append(corpus_path + ".offsets")
            offset_candidates.append(corpus_path + ".offset")

        # 查找第一个存在的 offset 文件
        offset_path = None
        for candidate in offset_candidates:
            if os.path.exists(candidate):
                offset_path = candidate
                break

        if offset_path:
            index_logger.info(f"找到 offset 文件: {offset_path}")
            index_logger.info("使用磁盘懒加载模式")
            corpus = DiskBasedChunks(corpus_path, offset_path)
            index_logger.info(f"语料库: {len(corpus):,} 条 (懒加载)")
            return corpus
        else:
            index_logger.info(f"未找到 offset 文件（尝试了: {', '.join(offset_candidates)}）")
            index_logger.info("全量加载到内存")
            corpus: List[Dict[str, Any]] = []
            with open(corpus_path, "r", encoding="utf-8") as f:
                for line in tqdm(f, desc="加载语料"):
                    if line.strip():
                        corpus.append(json.loads(line))
            index_logger.info(f"语料库: {len(corpus):,} 条")
            return corpus

    def _format_doc(self, doc: Dict[str, Any]) -> str:
        """格式化单个文档"""
        text = doc.get("contents") or doc.get("text", "")
        title = doc.get("title", "")
        return f"[{title}]\n{text}" if title else text

    def search(self, query_embs: np.ndarray, top_k: int = 5) -> tuple:
        """
        原始向量检索（供 Batcher 调用）
        """
        return self.index.search(query_embs, k=top_k)

    def encode(self, queries: List[str]) -> np.ndarray:
        """
        编码查询文本（供 Batcher 调用）
        """
        return self.encoder.encode(queries)

    def format_results(self, indices: np.ndarray) -> List[str]:
        """
        格式化检索结果（供 Batcher 调用）
        """
        all_results = []
        for query_indices in indices:
            query_results = []
            for idx in query_indices:
                if idx == -1 or idx >= len(self.corpus):
                    continue
                doc = cast(Dict[str, Any], self.corpus[idx])
                query_results.append(self._format_doc(doc))

            if not query_results:
                all_results.append("[查询结果] 未找到相关文档")
            else:
                all_results.append("\n---\n".join(query_results))

        return all_results

    def query(self, query: str, top_k: int = 5) -> str:
        """单条查询"""
        try:
            query_emb = self.encoder.encode([query])
            _, idxs = self.index.search(query_emb, k=top_k)
            return self.format_results(idxs)[0]
        except Exception as e:
            return f"[Error] {str(e)}"

    def batch_query(self, queries: List[str], top_k: int = 5) -> List[str]:
        """批量查询"""
        if not queries:
            return []

        try:
            query_embs = self.encoder.encode(queries)
            _, idxs = self.index.search(query_embs, k=top_k)
            return self.format_results(idxs)
        except Exception as e:
            return [f"[Error] {str(e)}" for _ in queries]

    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        return {
            "index_path": self.index_path,
            "model_name": self.model_name,
            "corpus_path": self.corpus_path,
            "corpus_size": len(self.corpus),
            "index_size": self.index.ntotal,
            "device_config": self.device_config,
            "encoder_device": self.encoder_device,
            "index_device": self.index_device
        }

    def release(self):
        """
        释放 GPU 资源
        """
        import gc

        index_logger.info("开始清理 GPU 资源...")

        # 1. 释放 Encoder 模型
        if hasattr(self, "encoder") and self.encoder is not None:
            if hasattr(self.encoder, "model") and self.encoder.model is not None:
                # 将模型移到 CPU 并删除
                try:
                    self.encoder.model.cpu()
                    del self.encoder.model
                    self.encoder.model = None  # type: ignore
                except Exception as e:
                    index_logger.warning(f"释放 encoder.model 失败: {e}")
            try:
                del self.encoder
            except Exception:
                pass
            self.encoder = None  # type: ignore

        # 2. 释放 Faiss GPU 索引
        if hasattr(self, "index") and self.index is not None:
            try:
                del self.index
            except Exception as e:
                index_logger.warning(f"释放 index 失败: {e}")
            self.index = None  # type: ignore

        # 3. 释放语料库
        if hasattr(self, "corpus") and self.corpus is not None:
            try:
                del self.corpus
            except Exception:
                pass
            self.corpus = []  # type: ignore

        # 4. 强制垃圾回收
        gc.collect()

        # 5. 清理 CUDA 缓存
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                # 同步所有 CUDA 流
                for i in range(torch.cuda.device_count()):
                    try:
                        with torch.cuda.device(i):
                            torch.cuda.synchronize()
                    except Exception:
                        pass
        except Exception as e:
            index_logger.warning(f"清理 CUDA 缓存失败: {e}")

        index_logger.info("GPU 资源清理完成")


# ============================================================================
# Query Batcher - 批量请求收集器
# ============================================================================

@dataclass
class PendingQuery:
    """待处理的查询请求"""
    query: str
    top_k: int
    future: asyncio.Future
    timestamp: float = field(default_factory=time.time)


class QueryBatcher:
    """
    查询批处理器
    
    收集一段时间窗口内的查询请求，然后批量执行 Faiss 检索。
    
    工作原理:
    1. 请求到达时加入队列，返回 Future
    2. 后台任务定期检查队列
    3. 达到触发大小或超时时，批量执行检索
    4. 将结果分发到各个 Future
    
    Args:
        rag_index: RAG 索引实例
        trigger_batch_size: 触发批处理的阈值（队列达到此大小时触发）
        max_batch_size: 单次批处理的最大数量
        max_wait_time: 最大等待时间（秒）
        check_interval: 检查间隔（秒）
    """
    
    def __init__(
        self,
        rag_index: "DenseE5RAGIndex",
        trigger_batch_size: int = 16,
        max_batch_size: int = 32,
        max_wait_time: float = 0.05,  # 50ms
        check_interval: float = 0.01   # 10ms
    ):
        self.rag_index = rag_index
        self.trigger_batch_size = trigger_batch_size
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.check_interval = check_interval

        self._queue: deque[PendingQuery] = deque()
        # 不在 __init__ 中创建 Lock，因为它会绑定到当前事件循环
        # 在 start() 中创建，确保使用正确的事件循环
        self._lock: Optional[asyncio.Lock] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False

        # 统计信息
        self._total_queries = 0
        self._total_batches = 0
        self._total_batch_size = 0
    
    async def start(self):
        """启动后台批处理任务"""
        if self._running:
            logger.warning("[Batcher] Already running, skipping start")
            return

        # 强制重新创建 Lock，确保使用当前事件循环
        # 即使之前有残留的 Lock，也会被覆盖
        self._lock = asyncio.Lock()
        logger.info(f"[Batcher] Created lock in event loop: {id(asyncio.get_event_loop())}")

        logger.info(f"[Batcher] Starting... _running before={self._running}")
        self._running = True
        logger.info(f"[Batcher] _running set to True")

        self._task = asyncio.create_task(self._batch_worker())
        logger.info(
            f"[Batcher] 启动，trigger={self.trigger_batch_size}, "
            f"max={self.max_batch_size}, wait={self.max_wait_time}s"
        )
        logger.info(f"[Batcher] Background task created: {self._task}")
        logger.info(f"[Batcher] Event loop: {id(asyncio.get_event_loop())}")

        # 等待一小段时间，确保任务开始执行
        await asyncio.sleep(0.001)
        logger.info(f"[Batcher] After sleep, task status: done={self._task.done()}, cancelled={self._task.cancelled()}")

        # 如果任务立即完成，说明有问题
        if self._task.done():
            logger.error("[Batcher] Worker task completed immediately! This indicates a problem.")
            try:
                # 尝试获取异常
                exc = self._task.exception()
                logger.error(f"[Batcher] Worker task exception: {exc}")
            except Exception as e:
                logger.error(f"[Batcher] Could not get task exception: {e}")
    
    async def stop(self):
        """停止后台任务"""
        logger.info(f"[Batcher] Stopping... _running={self._running}, task={self._task}")
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.info("[Batcher] Task cancelled successfully")
            except Exception as e:
                logger.error(f"[Batcher] Error during task cancellation: {e}")
            self._task = None

        # 清理队列中剩余的请求
        if self._lock:
            async with self._lock:
                for pending in self._queue:
                    if not pending.future.done():
                        pending.future.set_exception(
                            RuntimeError("Batcher stopped")
                        )
                self._queue.clear()
        else:
            # 如果没有 Lock，直接清理队列
            for pending in self._queue:
                if not pending.future.done():
                    pending.future.set_exception(
                        RuntimeError("Batcher stopped")
                    )
            self._queue.clear()

        # 清理 Lock 引用，下次 start 时会重新创建
        self._lock = None

        logger.info("[Batcher] 已停止")
    
    async def submit(self, query: str, top_k: int = 5) -> str:
        """
        提交查询请求

        Args:
            query: 查询文本
            top_k: 返回结果数

        Returns:
            检索结果文本
        """
        logger.info(f"[Batcher] Submit query: '{query[:30]}...', top_k={top_k}")
        logger.info(f"[Batcher] Worker status: running={self._running}, task={self._task}, task_done={self._task.done() if self._task else 'N/A'}")

        loop = asyncio.get_event_loop()
        future: asyncio.Future[str] = loop.create_future()

        pending = PendingQuery(
            query=query,
            top_k=top_k,
            future=future
        )

        async with self._lock:
            self._queue.append(pending)
            self._total_queries += 1
            logger.info(f"[Batcher] Query added to queue (queue_size={len(self._queue)})")

        logger.info(f"[Batcher] Waiting for result...")
        result = await future
        logger.info(f"[Batcher] Result received (len={len(result)} chars)")
        return result
    
    async def _batch_worker(self):
        """后台批处理工作循环"""
        logger.info(f"[Batcher] Worker started in event loop: {id(asyncio.get_event_loop())}")
        while self._running:
            try:
                await asyncio.sleep(self.check_interval)
                await self._try_process_batch()
            except asyncio.CancelledError:
                logger.info("[Batcher] Worker cancelled")
                break
            except Exception as e:
                logger.error(f"[Batcher] Worker error: {e}", exc_info=True)

        logger.warning(f"[Batcher] Worker EXITED! _running={self._running}")
        logger.warning(f"[Batcher] Worker exit stack trace:", exc_info=True)
    
    async def _try_process_batch(self):
        """尝试处理一批请求"""
        async with self._lock:
            if not self._queue:
                return

            now = time.time()
            oldest = self._queue[0].timestamp
            queue_age = now - oldest

            # 检查是否应该触发批处理
            # 触发条件：队列达到触发阈值 或 等待超时
            should_process = (
                len(self._queue) >= self.trigger_batch_size or
                queue_age >= self.max_wait_time
            )

            if not should_process:
                return

            logger.info(f"[Batcher] Triggering batch processing (queue_size={len(self._queue)}, age={queue_age:.3f}s)")
            # 收集一批请求（按 top_k 分组）
            batch = self._collect_batch()

        if batch:
            await self._process_batch(batch)
    
    def _collect_batch(self) -> List[PendingQuery]:
        """从队列收集一批请求"""
        batch: List[PendingQuery] = []
        
        while self._queue and len(batch) < self.max_batch_size:
            batch.append(self._queue.popleft())
        
        return batch
    
    async def _process_batch(self, batch: List[PendingQuery]):
        """
        处理一批请求

        使用 Faiss 批量检索接口
        """
        if not batch:
            return

        self._total_batches += 1
        self._total_batch_size += len(batch)

        start_time = time.time()
        logger.info(f"[Batcher] Processing batch of {len(batch)} queries...")

        try:
            # 1. 收集所有查询文本
            queries = [p.query for p in batch]

            # 找出最大的 top_k（批量检索使用统一的 k）
            max_top_k = max(p.top_k for p in batch)
            logger.info(f"[Batcher] Batch search: {len(queries)} queries, max_top_k={max_top_k}")

            # 2. 在线程池中执行同步的批量检索
            loop = asyncio.get_event_loop()
            logger.info(f"[Batcher] Submitting to thread pool executor...")
            results = await loop.run_in_executor(
                None,
                self._sync_batch_search,
                queries,
                max_top_k
            )
            logger.info(f"[Batcher] Thread pool executor returned results")

            elapsed = time.time() - start_time
            avg_latency = elapsed / len(batch) * 1000

            logger.info(
                f"[Batcher] 批处理完成: {len(batch)} 条, "
                f"耗时 {elapsed*1000:.1f}ms, 平均 {avg_latency:.1f}ms/条"
            )

            # 3. 分发结果（根据各自的 top_k 截断）
            for pending, result in zip(batch, results):
                if not pending.future.done():
                    # 如果请求的 top_k 小于 max_top_k，需要截断结果
                    if pending.top_k < max_top_k:
                        truncated = self._truncate_result(result, pending.top_k)
                        pending.future.set_result(truncated)
                    else:
                        pending.future.set_result(result)

        except Exception as e:
            logger.error(f"[Batcher] Batch processing error: {e}")
            # 所有请求返回错误
            for pending in batch:
                if not pending.future.done():
                    pending.future.set_exception(e)
    
    def _sync_batch_search(self, queries: List[str], top_k: int) -> List[str]:
        """
        同步批量检索（在线程池中执行）
        """
        logger.info(f"[Batcher] _sync_batch_search START: {len(queries)} queries, top_k={top_k}")
        result = self.rag_index.batch_query(queries, top_k=top_k)
        logger.info(f"[Batcher] _sync_batch_search DONE: returned {len(result)} results")
        return result
    
    @staticmethod
    def _truncate_result(result: str, top_k: int) -> str:
        """
        截断结果到指定的 top_k 数量
        
        结果格式: 多个文档用 "---" 分隔
        """
        if not result or top_k <= 0:
            return result
        
        # 按分隔符分割文档
        docs = result.split("\n---\n")
        
        if len(docs) <= top_k:
            return result
        
        # 截断并重新拼接
        return "\n---\n".join(docs[:top_k])
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        avg_batch_size = (
            self._total_batch_size / self._total_batches 
            if self._total_batches > 0 else 0
        )
        return {
            "total_queries": self._total_queries,
            "total_batches": self._total_batches,
            "avg_batch_size": round(avg_batch_size, 2),
            "queue_size": len(self._queue),
            "running": self._running,
            "trigger_batch_size": self.trigger_batch_size,
            "max_batch_size": self.max_batch_size,
            "max_wait_time": self.max_wait_time
        }


# ============================================================================
# RAG Backend
# ============================================================================

class RAGBackend(Backend):
    """
    RAG 检索后端
    
    特性:
    - 使用 QueryBatcher 批量处理请求
    - Faiss 批量检索提高吞吐量
    - 支持 mmap 加载大索引
    - 磁盘懒加载语料库
    
    工具列表:
    - rag:search - 检索文档
    - rag:stats - 获取统计信息
    
    配置项:
    - model_name: E5 模型名称
    - index_path: Faiss 索引路径
    - corpus_path: 语料库 JSONL 路径
    - device: 设备配置，支持格式：
        - "cuda:0"        → Encoder 用 cuda:0, Index 用 cpu
        - "cuda:0/cuda:1" → Encoder 用 cuda:0, Index 用 cuda:1
        - "cpu"           → 全部用 cpu
    - default_top_k: 默认返回结果数
    - batcher_trigger_batch_size: 触发批处理的阈值
    - batcher_max_batch_size: 单次批处理的最大数量
    - batcher_max_wait_time: 批处理最大等待时间（秒）
    """
    
    name = "rag"
    description = "RAG Retrieval Backend - 文档检索服务"
    version = "3.0.0"
    
    def __init__(self, config: Optional[BackendConfig] = None):
        if config is None:
            raise ValueError(
                "RAG Backend 需要配置信息。请在配置文件中提供以下必需参数:\n"
                "  - index_path: Faiss 索引文件路径\n"
                "  - corpus_path: 语料库 JSONL 文件路径\n"
                "  - model_name: E5 模型名称（可选，默认 intfloat/e5-base-v2）\n"
                "  - device: 设备配置（可选，默认 cuda:0）"
            )
        super().__init__(config)
        
        self._rag_index: Optional["DenseE5RAGIndex"] = None
        self._batcher: Optional[QueryBatcher] = None
        self._initialized = False
    
    async def warmup(self):
        """
        预热：加载模型和索引，启动 Batcher
        """
        if not is_faiss_available():
            raise ImportError("RAG Backend 需要 faiss: pip install faiss-gpu")
        
        cfg = self.config.default_config
        
        logger.info("=" * 60)
        logger.info("🔥 RAG Backend 预热开始")
        logger.info("=" * 60)
        
        # 1. 获取配置（必需参数）
        index_path = cfg.get("index_path")
        if not index_path:
            raise ValueError(
                "配置缺失: 'index_path' 是必需参数。\n"
                "请在配置文件中设置 RAG 索引文件路径，例如:\n"
                '  "index_path": "/path/to/faiss.index"\n'
                "或设置环境变量: RAG_INDEX_PATH"
            )

        corpus_path = cfg.get("corpus_path")
        if not corpus_path:
            raise ValueError(
                "配置缺失: 'corpus_path' 是必需参数。\n"
                "请在配置文件中设置语料库文件路径，例如:\n"
                '  "corpus_path": "/path/to/corpus.jsonl"\n'
                "或设置环境变量: RAG_CORPUS_PATH"
            )

        # 可选参数（有默认值）
        model_name = cfg.get("model_name", "intfloat/e5-base-v2")
        device = cfg.get("device", "cuda:0")
        
        logger.info(f"   设备配置: {device}")
        
        # 2. 加载 RAG 索引（同步操作，在线程池中执行）
        loop = asyncio.get_event_loop()
        self._rag_index = await loop.run_in_executor(
            None,
            lambda: DenseE5RAGIndex(
                index_path=index_path,
                model_name=model_name,
                corpus_path=corpus_path,
                device=device
            )
        )
        
        # 确保索引加载成功
        assert self._rag_index is not None, "RAG Index 加载失败"
        
        # 3. 创建并启动 Batcher
        trigger_size = cfg.get("batcher_trigger_batch_size", 16)
        max_size = cfg.get("batcher_max_batch_size", 32)
        max_wait = cfg.get("batcher_max_wait_time", 0.05)
        
        self._batcher = QueryBatcher(
            rag_index=self._rag_index,
            trigger_batch_size=trigger_size,
            max_batch_size=max_size,
            max_wait_time=max_wait
        )
        await self._batcher.start()
        
        self._initialized = True
        
        # 显示实际使用的设备
        actual_encoder_device = self._rag_index.encoder_device
        actual_index_device = self._rag_index.index_device
        
        logger.info("=" * 60)
        logger.info("✅ RAG Backend 预热完成")
        logger.info(f"   - 模型: {model_name}")
        logger.info(f"   - Encoder 设备: {actual_encoder_device}")
        logger.info(f"   - Index 设备: {actual_index_device}")
        logger.info(f"   - 索引: {self._rag_index.index.ntotal:,} 向量")
        logger.info(f"   - 语料: {len(self._rag_index.corpus):,} 文档")
        logger.info(f"   - Batcher: trigger={trigger_size}, max={max_size}")
        logger.info("=" * 60)
    
    async def shutdown(self):
        """关闭：停止 Batcher，释放资源"""
        logger.info("🛑 RAG Backend 关闭中...")
        
        if self._batcher:
            await self._batcher.stop()
            self._batcher = None
        
        if self._rag_index:
            # 显式释放 GPU 资源
            try:
                self._rag_index.release()
            except Exception as e:
                logger.warning(f"RAG Index release warning: {e}")
            self._rag_index = None
        
        # 额外的垃圾回收
        import gc
        gc.collect()
        
        # 清理 CUDA 缓存
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        self._initialized = False
        logger.info("✅ RAG Backend 已关闭")
    
    # ========================================================================
    # 工具方法
    # ========================================================================
    
    @tool("rag:search")
    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        检索文档

        Args:
            query: 查询文本
            top_k: 返回结果数（默认使用配置值）
            session_id: 会话 ID (可选)
            trace_id: 追踪 ID (可选)

        Returns:
            标准化响应: {code, message, data, meta}
        """
        with ResponseTimer() as timer:
            try:
                if not self._initialized or not self._batcher:
                    return build_error_response(
                        code=ErrorCode.BACKEND_NOT_INITIALIZED,
                        message="RAG Backend 未初始化，请先调用 warmup()",
                        tool="rag:search",
                        data={
                            "query": query,
                            "details": "backend not initialized or batcher unavailable"
                        },
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="rag",
                        session_id=session_id,
                        trace_id=trace_id
                    )

                actual_top_k = top_k or self.config.default_config.get("default_top_k", 5)

                logger.info(f"🔍 [rag:search] START: query='{query[:50]}...', top_k={actual_top_k}")

                try:
                    # 通过 Batcher 提交请求
                    logger.info(f"   ↳ Submitting to batcher...")
                    context = await self._batcher.submit(query, top_k=actual_top_k)
                    logger.info(f"   ↳ Batcher returned result (len={len(context)} chars)")

                    return build_success_response(
                        data={
                            "query": query,
                            "context": context
                        },
                        tool="rag:search",
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="rag",
                        session_id=session_id,
                        trace_id=trace_id
                    )
                except Exception as e:
                    logger.error(f"[rag:search] 错误: {e}")
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message=str(e),
                        tool="rag:search",
                        data={
                            "query": query,
                            "details": str(e)
                        },
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="rag",
                        session_id=session_id,
                        trace_id=trace_id
                    )
            except Exception as e:
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[RAG] Error: {str(e)}",
                    tool="rag:search",
                    data={"details": str(e)},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="rag",
                    session_id=session_id,
                    trace_id=trace_id
                )
    @tool("rag:batch_search")
    async def batch_search(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量检索文档

        Args:
            queries: 查询文本列表
            top_k: 返回结果数
            session_id: 会话 ID (可选)
            trace_id: 追踪 ID (可选)

        Returns:
            标准化响应: {code, message, data, meta}
        """
        with ResponseTimer() as timer:
            try:
                if not self._initialized or not self._batcher:
                    return build_error_response(
                        code=ErrorCode.BACKEND_NOT_INITIALIZED,
                        message="RAG Backend 未初始化",
                        tool="rag:batch_search",
                        data={
                            "queries": queries,
                            "details": "backend not initialized or batcher unavailable"
                        },
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="rag",
                        session_id=session_id,
                        trace_id=trace_id
                    )

                actual_top_k = top_k or self.config.default_config.get("default_top_k", 5)

                logger.debug(f"🔍 [rag:batch_search] {len(queries)} 条查询")

                try:
                    # 并发提交所有请求
                    tasks = [
                        self._batcher.submit(q, top_k=actual_top_k)
                        for q in queries
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # 处理结果
                    contexts = []
                    errors = []
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            contexts.append(f"[Error] {str(result)}")
                            errors.append({"index": i, "error": str(result)})
                        else:
                            contexts.append(result)

                    if len(errors) == 0:
                        # All successful
                        return build_success_response(
                            data={
                                "count": len(queries),
                                "contexts": contexts
                            },
                            tool="rag:batch_search",
                            execution_time_ms=timer.get_elapsed_ms(),
                            resource_type="rag",
                            session_id=session_id,
                            trace_id=trace_id
                        )
                    elif len(errors) == len(queries):
                        # All failed
                        return build_error_response(
                            code=ErrorCode.ALL_REQUESTS_FAILED,
                            message="All queries failed",
                            tool="rag:batch_search",
                            data={
                                "count": len(queries),
                                "contexts": contexts,
                                "errors": errors,
                                "details": "all batch queries failed"
                            },
                            execution_time_ms=timer.get_elapsed_ms(),
                            resource_type="rag",
                            session_id=session_id,
                            trace_id=trace_id
                        )
                    else:
                        # Partial failure
                        return build_error_response(
                            code=ErrorCode.PARTIAL_FAILURE,
                            message=f"{len(errors)} out of {len(queries)} queries failed",
                            tool="rag:batch_search",
                            data={
                                "count": len(queries),
                                "contexts": contexts,
                                "errors": errors,
                                "details": "partial batch query failure"
                            },
                            execution_time_ms=timer.get_elapsed_ms(),
                            resource_type="rag",
                            session_id=session_id,
                            trace_id=trace_id
                        )
                except Exception as e:
                    logger.error(f"[rag:batch_search] 错误: {e}")
                    return build_error_response(
                        code=ErrorCode.UNEXPECTED_ERROR,
                        message=str(e),
                        tool="rag:batch_search",
                        data={
                            "queries": queries,
                            "details": str(e)
                        },
                        execution_time_ms=timer.get_elapsed_ms(),
                        resource_type="rag",
                        session_id=session_id,
                        trace_id=trace_id
                    )
            except Exception as e:
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[RAG] Error: {str(e)}",
                    tool="rag:batch_search",
                    data={"details": str(e)},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="rag",
                    session_id=session_id,
                    trace_id=trace_id
                )
    @tool("rag:stats")
    async def get_stats(
        self,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取统计信息

        Args:
            session_id: 会话 ID (可选)
            trace_id: 追踪 ID (可选)

        Returns:
            标准化响应: {code, message, data, meta}
        """
        with ResponseTimer() as timer:
            try:
                stats = {
                    "initialized": self._initialized,
                    "backend_version": self.version
                }

                if self._rag_index:
                    stats["index"] = self._rag_index.get_stats()

                if self._batcher:
                    stats["batcher"] = self._batcher.get_stats()

                return build_success_response(
                    data=stats,
                    tool="rag:stats",
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="rag",
                    session_id=session_id,
                    trace_id=trace_id
                )

            except Exception as e:
                return build_error_response(
                    code=ErrorCode.UNEXPECTED_ERROR,
                    message=f"[RAG] Error: {str(e)}",
                    tool="rag:stats",
                    data={"details": str(e)},
                    execution_time_ms=timer.get_elapsed_ms(),
                    resource_type="rag",
                    session_id=session_id,
                    trace_id=trace_id
                )

# ============================================================================
# 便捷函数
# ============================================================================

def create_rag_backend(
    model_name: str = "intfloat/e5-base-v2",
    index_path: str = "./data/index/faiss.index",
    corpus_path: str = "./data/corpus.jsonl",
    device: str = "cuda:0",
    default_top_k: int = 5,
    batcher_trigger_batch_size: int = 16,
    batcher_max_batch_size: int = 32,
    batcher_max_wait_time: float = 0.05,
    **kwargs
) -> RAGBackend:
    """
    创建 RAG 后端的便捷函数
    
    Args:
        model_name: E5 模型名称
        index_path: Faiss 索引路径
        corpus_path: 语料库路径
        device: 设备配置，支持格式：
        - "cuda:0"        → Encoder 用 cuda:0, Index 用 cpu
        - "cuda:0/cuda:1" → Encoder 用 cuda:0, Index 用 cuda:1
        - "cpu"           → 全部用 cpu
        default_top_k: 默认返回结果数
        batcher_trigger_batch_size: 触发批处理的阈值
        batcher_max_batch_size: 单次批处理的最大数量
        batcher_max_wait_time: 批处理最大等待时间
        
    Returns:
        RAGBackend 实例
    """
    config = BackendConfig(
        enabled=True,
        default_config={
        "model_name": model_name,
        "index_path": index_path,
        "corpus_path": corpus_path,
        "device": device,
        "default_top_k": default_top_k,
        "batcher_trigger_batch_size": batcher_trigger_batch_size,
        "batcher_max_batch_size": batcher_max_batch_size,
        "batcher_max_wait_time": batcher_max_wait_time,
        **kwargs
        }
    )
    return RAGBackend(config)
