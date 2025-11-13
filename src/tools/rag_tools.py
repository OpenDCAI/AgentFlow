import os
import json
import numpy as np
import openai
from tqdm import trange

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
openai.base_url = (
    os.environ.get("OPENAI_API_URL")
    or os.environ.get("OPENAI_API_BASE")
    or os.environ.get("OPENAI_BASE_URL")
    or ""
)

_FAISS_AVAILABLE = True
try:
    import faiss
except ImportError:
    _FAISS_AVAILABLE = False


class RAGIndex:
    """
    A class to encapsulate RAG index building, loading, saving, and querying functionalities.
    """
    def __init__(self, client: openai.OpenAI, model: str = "text-embedding-3-small"):
        """
        Initializes the RAGIndex instance.

        Args:
            client (openai.OpenAI): An instance of the OpenAI client for generating embeddings.
            model (str): The name of the embedding model to use.
        """
        if not isinstance(client, openai.OpenAI):
            raise TypeError("The 'client' must be an instance of openai.OpenAI")
            
        self.client = client
        self.model = model
        self.chunks = []
        self.vectors = None
        self.normalized_vectors = None

    def _normalize_vectors(self):
        if self.vectors is not None:
            norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1e-9
            self.normalized_vectors = self.vectors / norms
            print("Vectors have been pre-normalized for faster querying.")

    def _get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a batch of texts."""
        # The OpenAI API recommends replacing newline characters with a space.
        processed_texts = [text.replace("\n", " ") for text in texts]
        response = self.client.embeddings.create(input=processed_texts, model=self.model)
        return [item.embedding for item in response.data]

    def build_index(self, file_path: str, batch_size: int = 512):
        """Builds the index from a source file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")

        # 1. Load and parse the data file
        kb_content = []
        if file_path.endswith('.jsonl'):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        kb_content.append(json.loads(line))
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                kb_content = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        # 2. Extract text chunks
        self.chunks = [
            sample["text"] for sample in kb_content
            if isinstance(sample, dict) and "text" in sample and isinstance(sample["text"], str) and sample["text"]
        ]
        if not self.chunks:
            print("Failed to extract any text chunks from the file.")
            return
        print(f"Successfully loaded {len(self.chunks)} text chunks.")

        # 3. Generate embeddings
        print("Generating embeddings for text chunks...")
        embeddings = []
        try:
            for i in trange(0, len(self.chunks), batch_size, desc="Generating Embeddings"):
                batch = self.chunks[i:i + batch_size]
                batch_embeddings = self._get_embeddings_batch(batch)
                embeddings.extend(batch_embeddings)
            self.vectors = np.array(embeddings, dtype=np.float32)
            print(f"Embeddings generated successfully. Vector shape: {self.vectors.shape}")
            self._normalize_vectors()
        except Exception as e:
            print(f"An error occurred while generating embeddings: {str(e)}")

    def save_index(self, index_path: str):
        """Saves the index to index_path."""
        if self.vectors is None or not self.chunks:
            raise ValueError("Index is empty and cannot be saved. Please call the build() method first.")

        os.makedirs(index_path, exist_ok=True)
        chunks_file = os.path.join(index_path, "chunks.json")
        vectors_file = os.path.join(index_path, "vectors.npy")

        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        
        np.save(vectors_file, self.vectors)
        print(f"Index saved successfully to {index_path}")

    @classmethod
    def load_index(cls, index_path: str, client: openai.OpenAI, model: str = "text-embedding-3-small"):
        """Loads an index from a directory and returns a new RAGIndex instance."""
        chunks_file = os.path.join(index_path, "chunks.json")
        vectors_file = os.path.join(index_path, "vectors.npy")

        if not os.path.exists(chunks_file) or not os.path.exists(vectors_file):
            raise FileNotFoundError(f"Index files 'chunks.json' or 'vectors.npy' not found in '{index_path}'.")

        instance = cls(client, model)
        with open(chunks_file, 'r', encoding='utf-8') as f:
            instance.chunks = json.load(f)
        instance.vectors = np.load(vectors_file)
        instance._normalize_vectors()
        
        print(f"Index loaded successfully from '{index_path}', containing {len(instance.chunks)} chunks.")
        return instance

    def query(self, query: str, top_k: int = 3) -> str:
        """Queries the index for the most relevant text chunks."""
        if self.vectors is None:
            raise RuntimeError("Index has not been built or loaded yet. Cannot perform query.")
        
        if not query:
            raise ValueError("Query text cannot be empty.")

        query_vector = np.array(self._get_embeddings_batch([query])[0], dtype=np.float32)
        query_norm = query_vector / np.linalg.norm(query_vector)
        similarities = np.dot(self.normalized_vectors, query_norm)
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]
        
        retrieved_chunks = [self.chunks[i] for i in top_k_indices]
        context = "\n---\n".join(retrieved_chunks)
        
        return f"### Retrieved Context:\n{context}"


class RAGIndex_faiss(RAGIndex):
    def __init__(self, client: openai.OpenAI, model: str = "text-embedding-3-small"):
        super().__init__(client, model)
        self.faiss_index = None

    def build_index(self, file_path: str, batch_size: int = 512) -> None:
        """Builds the index from a source file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")

        # 1. Load and parse the data file
        kb_content = []
        if file_path.endswith('.jsonl'):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        kb_content.append(json.loads(line))
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                kb_content = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        # 2. Extract text chunks
        self.chunks = [
            sample["text"] for sample in kb_content
            if isinstance(sample, dict) and "text" in sample and isinstance(sample["text"], str) and sample["text"]
        ]
        if not self.chunks:
            print("Failed to extract any text chunks from the file.")
            return
        print(f"Successfully loaded {len(self.chunks)} text chunks.")

        # 3. Generate embeddings
        print("Generating embeddings for text chunks...")
        embeddings = []
        try:
            for i in trange(0, len(self.chunks), batch_size, desc="Generating Embeddings"):
                batch = self.chunks[i:i + batch_size]
                batch_embeddings = self._get_embeddings_batch(batch)
                embeddings.extend(batch_embeddings)
            self.vectors = np.array(embeddings, dtype=np.float32)
            print(f"Embeddings generated successfully. Vector shape: {self.vectors.shape}")
            self._normalize_vectors()
        
            print("Build index with Faiss...")
            vectors = self.vectors
            d = vectors.shape[1]
            faiss.normalize_L2(vectors)
            self.faiss_index = faiss.IndexFlatIP(d)
            self.faiss_index.add(vectors)
            print(f"Build Faiss index sucessfully, containing {self.faiss_index.ntotal} vectors。")

        except Exception as e:
            print(f"An error occurred while building index: {str(e)}")

    def save_index(self, index_path: str):
        if self.faiss_index is None or not self.chunks:
            raise ValueError("Index is empty and cannot be saved. Please call the build() method first.")

        os.makedirs(index_path, exist_ok=True)
        chunks_file = os.path.join(index_path, "chunks.json")
        index_file = os.path.join(index_path, "index.faiss")

        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        
        faiss.write_index(self.faiss_index, index_file)
        print(f"Index saved successfully to {index_path}")

    @classmethod
    def load_index(cls, index_path: str, client: openai.OpenAI, model: str = "text-embedding-3-small"):
        chunks_file = os.path.join(index_path, "chunks.json")
        index_file = os.path.join(index_path, "index.faiss")

        if not (os.path.exists(chunks_file) and os.path.exists(index_file)):
            raise FileNotFoundError(f"index file in {index_path} not found")

        instance = cls(client, model)
        with open(chunks_file, 'r', encoding='utf-8') as f:
            instance.chunks = json.load(f)
        
        instance.faiss_index = faiss.read_index(index_file)
        
        print(f"Index loaded successfully from '{index_path}', containing {len(instance.chunks)} chunks.")
        return instance

    def query(self, query: str, top_k: int = 3) -> str:
        if self.faiss_index is None:
            raise RuntimeError("Index has not been built or loaded yet. Cannot perform query.")
        
        if not query:
            raise ValueError("Query text cannot be empty.")

        try:
            query_vector = np.array(self._get_embeddings_batch([query])[0], dtype=np.float32)
            faiss.normalize_L2(query_vector.reshape(1, -1))
            distances, top_k_indices = self.faiss_index.search(query_vector.reshape(1, -1), top_k)
            indices = top_k_indices[0]
            retrieved_chunks = [self.chunks[i] for i in indices if i != -1]
            context = "\n---\n".join(retrieved_chunks)
            
            return f"### Retrieved Context:\n{context}"
        except Exception as e:
            return f"[query] An error occurs: {e}"


def get_rag_index_class(use_faiss: bool = False):
    if use_faiss and _FAISS_AVAILABLE:
        print("✅ Faiss is available. Using RAGIndex_faiss.")
        return RAGIndex_faiss
    else:
        if use_faiss and not _FAISS_AVAILABLE:
            print("⚠️ Faiss not available, falling back to the base RAGIndex.")
        print("Using base RAGIndex (Numpy version).")
        return RAGIndex
    

class QueryRAGIndexTool:
    name = "local_search"
    description = (
        "Searches a pre-built RAG index to find the most relevant text chunks. "
        "Use this tool to answer questions related to the indexed files."
    )
    parameters = [
        {'name': 'query', 'type': 'string', 'description': 'The query text to search for relevant text chunks.', 'required': True},
        {'name': 'top_k', 'type': 'integer', 'description': 'The number of top relevant chunks to retrieve (default is 3).', 'required': False}
    ]

    def __init__(self, rag_index: RAGIndex):
        """
        Initializes the tool with a RAGIndex instance.
        
        Args:
            rag_index (RAGIndex): A pre-configured and loaded RAGIndex instance.
        """
        self.rag_index = rag_index

    def call(self, params: dict, **kwargs) -> str:
        """Executes the query."""
        query = params.get("query")
        top_k = params.get("top_k", 3)

        if not query:
            return "[Query Tool] Error: The 'query' parameter is required."

        try:
            return self.rag_index.query(query, top_k=top_k)
        except Exception as e:
            return f"[Query Tool] Error: An exception occurred during the search: {str(e)}"