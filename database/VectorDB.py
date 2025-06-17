from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from settings import get_settings
import torch

settings = get_settings()

embeddings_func = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
)

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_func,
    persist_directory=settings.default_vectordb_storage_path,  
)