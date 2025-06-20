from modules.parse_cv.ParseCVFiles import parseCVs
from modules.read_cv_directory.CVProcessor import CVProcessor
from pprint import pprint
import dotenv
from settings import get_settings

if __name__ == "__main__":
    # Example usage of CVProcessor
    gDriveUrl = "https://drive.google.com/file/d/1pIxbxRgk4bE83fgIZV4CR2ZWSLmwS83R/view?usp=sharing"
    cvProcessor = CVProcessor(gDriveUrl, savePath='cv_files')
    
    try:
        documents = cvProcessor.processCVFiles()
        for doc in documents:
            print(doc) 
    except Exception as e:
        print(f"Error processing CV files: {e}")

    # Example usage of parseCVs
    parsed_cvs = parseCVs(documents)
    for parsed_cv in parsed_cvs:
        pprint(parsed_cv.__dict__)