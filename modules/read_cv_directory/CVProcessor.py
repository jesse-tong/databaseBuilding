from itertools import groupby
from modules.read_cv_directory.ProcessCVFileClass import ICVFileProcessor, PDFProcessor, DOCXProcessor, ODTProcessor
from langchain_core.documents import Document
from typing import List, Union
import mimetypes, re, os

from modules.read_cv_directory.GDriveDownload import GDriveDownload, isValidCVFileType



class CVProcessor:
    def __init__(self, gDriveUrlOrDirectory: str, savePath: str = 'cv_files'):
        self.gDriveSavePath = savePath
        self.gDriveUrlOrDirectory = gDriveUrlOrDirectory
        self.processors = {
            'application/pdf': PDFProcessor(),
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DOCXProcessor(),
            'application/vnd.oasis.opendocument.text': ODTProcessor()
        }
        self.gDriveDownloader = GDriveDownload(self.gDriveSavePath)
        try:
            os.makedirs(self.gDriveSavePath, exist_ok=True)
        except Exception as e:
            print(f"Error creating save path {self.gDriveSavePath}: {e}")
            raise e
    
    def processCVFiles(self) -> List[Document]:
        if re.match(r"https?://(?:drive)\.google\.com/[^\s]+", self.gDriveUrlOrDirectory):
            filePaths = self.gDriveDownloader.downloadPdfFileOrFolder(self.gDriveUrlOrDirectory)
        else:
            with os.scandir(self.gDriveUrlOrDirectory) as entries:
                filePaths = [entry.path for entry in entries if entry.is_file() and isValidCVFileType(entry.path)]
        
        documents = []
        for filePath in filePaths:
            mime_type, _ = mimetypes.guess_type(filePath)
            if mime_type in self.processors:
                processor: ICVFileProcessor = self.processors[mime_type]
                documents.extend(processor.process(filePath))
            else:
                print(f"Unsupported file type: {filePath}")

        merged_documents = []
        documents.sort(key=lambda doc: doc.metadata.get('file_name', ''))
        for doc in documents:
            file_name = doc.metadata.get('file_name', 'unknown')
            if not merged_documents or merged_documents[-1].metadata.get('file_name') != file_name:
                merged_documents.append(doc)
            else:
                merged_documents[-1].page_content += "\n" + doc.page_content

        return merged_documents
    
