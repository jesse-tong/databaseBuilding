from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import UnstructuredODTLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

class ICVFileProcessor:
    def process(self, file_path: str) -> list[Document]:
        raise NotImplementedError("Subclasses should implement this method.")
    
class PDFProcessor(ICVFileProcessor):
    def process(self, file_path: str) -> list[Document]:
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        # Add file name metadata to each document
        for doc in documents:
            doc.metadata['file_name'] = file_path.split('/')[-1]

        return documents
    
class DOCXProcessor(ICVFileProcessor):
    def process(self, file_path: str) -> list[Document]:
        loader = UnstructuredWordDocumentLoader(file_path)
        documents = loader.load()
        # Add file name metadata to each document
        for doc in documents:
            doc.metadata['file_name'] = file_path.split('/')[-1]

        return documents
    
class ODTProcessor(ICVFileProcessor):
    def process(self, file_path: str) -> list[Document]:
        loader = UnstructuredODTLoader(file_path)
        documents = loader.load()
        # Add file name metadata to each document
        for doc in documents:
            doc.metadata['file_name'] = file_path.split('/')[-1]

        return documents