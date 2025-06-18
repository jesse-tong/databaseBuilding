from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form

from shared.Dependencies import getProcessCVController
from shared.QueryObject import SearchCVQuery
from controller.ProcessCVController import ProcessCVController
from typing import Annotated, Optional, List

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/upload")
async def uploadCVFiles(googleDriveUrl: Annotated[Optional[str], Form()] = None, files: Optional[List[UploadFile]] = File(None), 
                        processCVController: ProcessCVController = Depends(getProcessCVController)):
    """
    Upload CV files or a Google Drive link for processing.
    """
    try:
        return processCVController.addCVFiles(googleDriveUrl=googleDriveUrl, files=files)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
     
@router.put("/update/{id}")
async def updateCVFiles(id: int, 
                        googleDriveUrl: Annotated[Optional[str], Form()] = None, files: Optional[List[UploadFile]] = File(None), 
                        processCVController: ProcessCVController = Depends(getProcessCVController)):
    """
    Update CV files or a Google Drive link for an existing application.
    """
    try:
        return processCVController.updateCVFiles(id, googleDriveUrl=googleDriveUrl, files=files)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/search")
async def searchCVs(query: SearchCVQuery,
                    processCVController: ProcessCVController = Depends(getProcessCVController)):
    """
    Search for CVs based on various criteria.
    """
    try:
        return processCVController.searchApplications(query)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{id}")
async def getCV(id: str, 
                processCVController: ProcessCVController = Depends(getProcessCVController)):
    """
    Get details of a specific CV by ID.
    """
    try:
        application = processCVController.getApplication(id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        return application
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{id}")
async def deleteCV(id: str, 
                   processCVController: ProcessCVController = Depends(getProcessCVController)):
    """
    Delete a specific CV by ID.
    """
    try:
        return processCVController.deleteApplication(id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/")
async def listCVsByPage(page: int = 1, 
                        size: int = 10, 
                        processCVController: ProcessCVController = Depends(getProcessCVController)):
    """
    List CVs with pagination.
    """
    try:
        return processCVController.getApplications(page, size)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
