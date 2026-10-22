import os
from functools import lru_cache

from langchain_core.embeddings import Embeddings


class MiniLMOnnxEmbeddings(Embeddings):
    """The same all-MiniLM-L6-v2 model, run through ONNX Runtime instead of PyTorch.

    Same vectors (normalised, 384 dimensions) at roughly a third of the memory, which is what lets the
    API fit on a 512 MB host. Uses the ONNX build that ships with chromadb, so there is nothing extra to
    install. Selected with EMBEDDINGS_BACKEND=onnx; the default is the original HuggingFace/PyTorch path.
    """

    def __init__(self):
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        self._model = ONNXMiniLM_L6_V2()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(x) for x in vector] for vector in self._model(list(texts))]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache(maxsize=1)
def get_embedding_model():

    if os.getenv("EMBEDDINGS_BACKEND", "huggingface").strip().lower() == "onnx":
        return MiniLMOnnxEmbeddings()

    # Imported here so the ONNX path never loads PyTorch.
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings
