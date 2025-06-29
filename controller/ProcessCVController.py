from modules.parse_cv.ParseCVFiles import parseCVs
from modules.read_cv_directory.CVProcessor import CVProcessor
from shared.QueryObject import SearchCVQuery

from controller.DBController import DBController
from fastapi import APIRouter, HTTPException, Depends
from schema.InitDB import SessionDep

from typing import Annotated, List, Union, Any
from pydantic import BaseModel
from fastapi import Request, UploadFile, File
from pathvalidate import sanitize_filename
import os, uuid, datetime, re

class ProcessCVController:
    def __init__(self, sqlEngine, vectorStore, baseCVStoragePath: str = 'cv_storage'):
        self.baseCVStoragePath = baseCVStoragePath
        self.dbController = DBController(sqlEngine, vectorStore)

    def _generateDownloadFolder(self, isGoogleDrive: bool = False) -> str:
        """
        Generates a unique folder path for storing CV files.
        """
        folder_name = f"cv_{'drive' if isGoogleDrive else 'local'}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
        folder_path = os.path.join(self.baseCVStoragePath, folder_name)
        return folder_path
    
    def addCVFiles(self, googleDriveUrl: str | None = None, files: Union[UploadFile, List[UploadFile]] | None = None):
        documents = []
        if not googleDriveUrl and not files:
            raise HTTPException(status_code=400, detail="No CV files or Google Drive link provided.")
        
        isGoogleDriveUrl = isinstance(googleDriveUrl, str) and re.match(r"https?://(?:drive)\.google\.com/[^\s]+", googleDriveUrl)
        if not isGoogleDriveUrl and not files:
            raise HTTPException(status_code=400, detail="No CV files or Google Drive link provided.")
        
        if isGoogleDriveUrl:
            # Process Google Drive link
            cvProcessor = CVProcessor(googleDriveUrl, self._generateDownloadFolder(True))
            documents.extend(cvProcessor.processCVFiles())

        if files != None and isinstance(files, UploadFile):
            files = [files]  # Ensure files is a list if a single file is provided

        if files != None:
            # Process uploaded files
            documents = []
            downloadPath = self._generateDownloadFolder()
            os.makedirs(downloadPath, exist_ok=True)
            for file in files:
                fileName = sanitize_filename(file.filename)
                filePath = os.path.join(downloadPath, fileName)
                with open(filePath, "wb") as f:
                    f.write(file.file.read())
            cvProcessor = CVProcessor(downloadPath, self.baseCVStoragePath)
            documents.extend(cvProcessor.processCVFiles())
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid CV files found.")
        
        parsed_cvs = parseCVs(documents)
        application_ids = []
        for parsed_cv in parsed_cvs:
            application_id = self.dbController.addApplication(parsed_cv)
            application_ids.append(application_id)
        
        return {"application_ids": application_ids, "message": f"Successfully added {len(application_ids)} applications."}
    
    def updateCVFile(self, id: int, googleDriveUrl: str | None = None, file: UploadFile | None = None):
        documents = []
        if not googleDriveUrl and not file:
            raise HTTPException(status_code=400, detail="No CV files or Google Drive link provided.")
        
        if isinstance(googleDriveUrl, str) and file:
            raise HTTPException(status_code=400, detail="Please provide either a Google Drive link or files, not both.")

        if isinstance(googleDriveUrl, str):
            # Process Google Drive link
            if 'folders' in googleDriveUrl:
                raise HTTPException(status_code=400, detail="Google Drive folders are not supported for updates.")
            if not re.match(r"https?://(?:drive)\.google\.com/[^\s]+", googleDriveUrl):
                raise HTTPException(status_code=400, detail="Invalid Google Drive link provided. We don't support other cloud storage providers yet.")
            
            cvProcessor = CVProcessor(googleDriveUrl, self._generateDownloadFolder(True))
            documents.extend(cvProcessor.processCVFiles())
        

        if file != None:
            # Process uploaded files
            documents = []
            downloadPath = self._generateDownloadFolder()
            os.makedirs(downloadPath, exist_ok=True)
            fileName = sanitize_filename(file.filename)
            filePath = os.path.join(downloadPath, fileName)
            with open(filePath, "wb") as f:
                f.write(file.file.read())
            cvProcessor = CVProcessor(downloadPath, self.baseCVStoragePath)
            documents.extend(cvProcessor.processCVFiles())
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid CV files found.")
        
        parsed_cvs = parseCVs(documents)
        application_id = self.dbController.updateApplication(id, parsed_cvs[0])
        if application_id is None:
            raise HTTPException(status_code=404, detail="Application not found. Cannot update application.")
        return {"application_ids": application_id, "message": f"Successfully updated application with id {application_id}."}
    
    def getApplication(self, id: int):
        application = self.dbController.getApplication(id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found.")
        
        return {
            "application": application["application"],
            "education": application["education"],
            "experiencedSkills": application["experiencedSkills"],
            "workExperiences": application["workExperiences"],
            "projects": application["projects"],
            "skillsAndExperience": application["skillsAndExperience"]
        }
    
    def deleteApplication(self, id: int):
        deleted_application = self.dbController.deleteApplication(id)
        if not deleted_application:
            raise HTTPException(status_code=404, detail="Application not found.")
        
        return {"message": "Application deleted successfully.", "application_id": deleted_application.id}
    
    def searchApplications(self, query: SearchCVQuery, vectorSearchK: int = 20):
        applications = self.dbController.searchApplications(query, vectorSearchK)
        if not applications:
            raise HTTPException(status_code=404, detail="No applications found matching the search criteria.")
        
        return applications
    
    def getApplications(self, page: int = 1, pageSize: int = 10, orderBy: str = None):
        """
        Get paginated list of applications.
        orderBy can be 'name', 'nameDesc', 'id', 'lastUpdated' (lastUpdated ascending), default sorting by 'lastUpdated' descending.
        """
        if page < 1 or pageSize < 1:
            raise HTTPException(status_code=422, detail="Page and page size must be greater than 0.")
        applications = self.dbController.getAllApplications(page, pageSize, orderBy)
        if not applications:
            raise HTTPException(status_code=404, detail="No applications found.")
        
        return applications
