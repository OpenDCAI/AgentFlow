# rag_tools.py

from typing import List
import numpy as np
import openai
import os
import json
from tqdm import trange
from dotenv import load_dotenv, find_dotenv

from colbert import Searcher
from colbert.infra import Run, RunConfig

load_dotenv(find_dotenv(), override=True)

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
openai.base_url = os.environ.get("OPENAI_API_URL", "")

RAG_INDEX = {
    "chunks": [],
    "vectors": None
}


def save_index(index_path):
    if not os.path.exists(index_path):
        os.makedirs(index_path)

    chunks_file_path = os.path.join(index_path, "chunks.json")
    vectors_file_path = os.path.join(index_path, "vectors.npy")
    
    with open(chunks_file_path, 'w', encoding='utf-8') as f:
        json.dump(RAG_INDEX["chunks"], f, ensure_ascii=False, indent=4)
    
    if RAG_INDEX["vectors"] is not None:
        np.save(vectors_file_path, RAG_INDEX["vectors"])
    print(f"[Save Index]: Index saved in '{index_path}'")


def load_index(index_path):
    chunks_file_path = os.path.join(index_path, "chunks.json")
    vectors_file_path = os.path.join(index_path, "vectors.npy")

    if os.path.exists(chunks_file_path) and os.path.exists(vectors_file_path):
        global RAG_INDEX
        with open(chunks_file_path, 'r', encoding='utf-8') as f:
            RAG_INDEX["chunks"] = json.load(f)
        RAG_INDEX["vectors"] = np.load(vectors_file_path)
        print(f"Index loaded from '{index_path}', containing {len(RAG_INDEX['chunks'])} chunks.")
        return True
    print("[Load Index]: Cannot find existing index files.")
    return False


client = openai.OpenAI(
    api_key=openai.api_key,
    base_url=openai.base_url 
)


def get_embeddings_batch(texts, model="text-embedding-3-small"):
    processed_texts = [text.replace("\n", " ") for text in texts]
    response = client.embeddings.create(input=processed_texts, model=model)
    return [item.embedding for item in response.data]


def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   response = client.embeddings.create(input=[text], model=model)
   return response.data[0].embedding


def simple_chunker(text: str, chunk_size: int, overlap: int) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def BuildRAGIndex(file_path, need_chunk, index_path, chunk_size=100, overlap=25, batch_size=512) -> str:
    global RAG_INDEX

    if not file_path or not os.path.exists(file_path):
        return f"[BuildRAGIndex] 错误: 文件路径 '{file_path}' 不存在或未提供。"

    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = json.load(f)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

        if need_chunk:
            chunks = simple_chunker(text_content, chunk_size=chunk_size, overlap=overlap)
        else:
            if file_path in ["data/hotpotqa_distractor_val_kb.json", "data/hotpotqa_distractor_val_kb_100.json"]:
                chunks = [sample["text"] for sample in text_content]

        if not chunks:
            return "[Index Tool] Error: No chunks created."

        RAG_INDEX["chunks"] = chunks

        print("Generating embeddings for chunks...")
        embeddings = []
        for i in trange(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_embeddings = get_embeddings_batch(batch)
            embeddings.extend(batch_embeddings)

        RAG_INDEX["vectors"] = np.array(embeddings)

        save_index(index_path)
        
        return f"[BuildRAGIndex] Done: Index created and saved from '{file_path}' with {len(chunks)} chunks."
    except Exception as e:
        return f"[BuildRAGIndex] Error: {str(e)}"


class QueryRAGIndexTool:
    name = "query_rag_index"
    description = (
        "To search in a previously built RAG index to find the most relevant chunks of text."
        "To answer the questions related to the indexed files."
    )
    parameters = [
        {
            'name': 'query',
            'type': 'string',
            'description': 'the query text to search for relevant text chunks.',
            'required': True
        },
        {
            'name': 'top_k',
            'type': 'integer',
            'description': 'the number of top relevant chunks to retrieve (default is 3).',
            'required': False
        }
    ]

    def call(self, params: dict, **kwargs) -> str:
        global RAG_INDEX
        query = params.get("query")
        top_k = params.get("top_k", 3)

        if RAG_INDEX["vectors"] is None:
            return "[Query Tool] Error: RAG index is not built yet."

        if not query:
            return "[Query Tool] Error: Query parameter is required."

        try:
            query_vector = np.array(get_embedding(query))
            
            index_vectors = RAG_INDEX["vectors"]
            query_norm = query_vector / np.linalg.norm(query_vector)
            index_norms = index_vectors / np.linalg.norm(index_vectors, axis=1)[:, np.newaxis]
            similarities = np.dot(index_norms, query_norm)
            top_k_indices = np.argsort(similarities)[-top_k:][::-1]
            retrieved_chunks = [RAG_INDEX["chunks"][i] for i in top_k_indices]
            context = "\n---\n".join(retrieved_chunks)
            
            return f"""### Retrieved Context:
{context}
"""
        except Exception as e:
            return f"[Query Tool] 错误: 查询索引时发生异常: {str(e)}"
        

class QueryColbertIndexTool:
    name = "query_rag_index"
    description = (
        "To search in a pre-built ColBERT index (e.g., Wikipedia) to find the most relevant documents. "
        "Use this for general knowledge questions."
    )
    parameters = [
        {
            'name': 'query',
            'type': 'string',
            'description': 'The query text to search for relevant documents.',
            'required': True
        },
        {
            'name': 'top_k',
            'type': 'integer',
            'description': 'The number of top relevant documents to retrieve (default is 3).',
            'required': False
        }
    ]

    def __init__(self, index_path: str):
        """
        Initializes the ColBERT searcher from an existing index path.
        """
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"ColBERT index path does not exist: {index_path}")
        
        print(f"[ColBERT] Initializing searcher with index at '{index_path}'...")
        index_name = os.path.basename(index_path)
        with Run().context(RunConfig(experiment=index_path, root=os.path.dirname(index_path))):
            self.searcher = Searcher(index=index_name)
        print("[ColBERT] Searcher initialized successfully.")


    def call(self, params: dict, **kwargs) -> str:
        query = params.get("query")
        top_k = params.get("top_k", 3)

        if not query:
            return "[ColBERT Tool] Error: Query parameter is required."

        try:
            print(f"#> Searching ColBERT with query: '{query}'")
            results = self.searcher.search(query, k=top_k)

            retrieved_chunks = []
            for passage_id, passage_rank, passage_score in zip(*results):
                passage_text = self.searcher.collection[passage_id]
                # 添加一些元数据，方便模型理解
                chunk_info = f"Source Rank: {passage_rank}, Score: {passage_score:.2f}\nContent: {passage_text}"
                retrieved_chunks.append(chunk_info)

            context = "\n---\n".join(retrieved_chunks)
            
            return f"""### Retrieved Context from ColBERT:
{context}
"""
        except Exception as e:
            return f"[ColBERT Tool] Error: An exception occurred during search: {str(e)}"
