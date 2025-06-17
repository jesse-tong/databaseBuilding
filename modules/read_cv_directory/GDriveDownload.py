import gdown, os, mimetypes

def isValidCVFileType(file_path: str) -> bool:
    """
    Checks if the file is a valid CV/resume file type (pdf, docx, odt).
    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file is a valid CV type, False otherwise.
    """
    validCVTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.oasis.opendocument.text']
    # Convert each '\\' to '/' for consistency as gdown use '\\' in returned file paths
    file_path = file_path.replace('\\', '/')
    mime_type, _ = mimetypes.guess_type(file_path)
    # Sometimes guessing the MIME type fails, so we check the file extension as a fallback
    file_extension = os.path.splitext(file_path)[-1].lower() 
    return mime_type in validCVTypes or file_extension in ['.pdf', '.docx', '.odt']

class GDriveDownload:
    def __init__(self, save_path):
        self.save_path = save_path

    def downloadPdfFileOrFolder(self, url: str) -> list[str]:
        """
        Downloads a PDF file or folder from Google Drive.

        Args:
            url (str): The URL of the Google Drive file or folder.

        Returns:
            list[str]: List of paths to downloaded PDF files.
        """
        # If the URL is a folder, use gdown.download_folder
        if "folders" in url:
            gdown.download_folder(url, output=self.save_path, use_cookies=False)
            # Delete any non-CV files in the folder
            for file in os.listdir(self.save_path):
                file_path = os.path.join(self.save_path, file)
                if not isValidCVFileType(file_path):
                    os.remove(file_path)
            # Return all valid files in the folder
            return [f"{self.save_path}/{file}" for file in os.listdir(self.save_path) if isValidCVFileType(f"{self.save_path}/{file}")]
        else:
            outputFileName = gdown.download(url, output=os.path.join(self.save_path, 'cv.pdf'), quiet=False, use_cookies=False)
            # Check if the downloaded file is a valid CV type
            if outputFileName != None and isValidCVFileType(outputFileName):
                return [self.save_path]
            else:
                print(f"Downloaded file is not a valid CV type: {self.save_path}")
                return []
        