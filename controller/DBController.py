from langchain.vectorstores import VectorStore
from langchain_core.documents import Document
from sqlmodel import Session, select, and_
from sqlalchemy import func

from database.SqlQuery import SqlQueryObject
from database.VectorQuery import VectorQueryObject
from settings import get_settings
from schema.Application import Application, Education, ExperiencedSkill
from schema.InitDB import engine
from modules.parse_cv.ParsedCV import ParsedCV
from shared.QueryObject import SearchCVQuery

import uuid
from typing import List, Dict, Any

settings = get_settings()
class DBController:
    def __init__(self, sql_engine, vector_store):
        self.sql_query = SqlQueryObject(Application, sql_engine)
        self.sql_engine = sql_engine
        self.vector_query = VectorQueryObject(Document, vector_store)

    def processParsedCV(self, parsed_cv: ParsedCV):
        # Convert ParsedCV to Application schema
        vectorDbUuid = str(uuid.uuid4()) # UUID referencing the vector database document
        application = Application(
            vectorDbUuid=vectorDbUuid,
            name=parsed_cv.name,
            email=parsed_cv.email,
            phone=parsed_cv.phone,
            linkedIn=parsed_cv.linkedIn,
            gitRepo=parsed_cv.gitRepo,
            yearsOfExperience=parsed_cv.totalYoE,
            education=[
                Education(
                    degree=edu.get('degree'),
                    institution=edu.get('institution'),
                    year=edu.get('year'),
                    gpa=edu.get('gpa')
                ) for edu in parsed_cv.educations
            ],
            skills=[
                ExperiencedSkill(
                    skill=skill['skill'],
                    yearsOfExperience=skill['yearsOfExperience']
                ) for skill in parsed_cv.experiencedSkills
            ],
        )
        
        skillsAndExperienceDocument = Document(
            page_content=f"Address: {parsed_cv.address}\n" +
                         f"Skills: \n{', '.join(parsed_cv.skills)}\n\n" +
                         f"Work Experiences: \n{'\n'.join(parsed_cv.workExperiences)}\n\n" +
                         f"Projects: \n{'\n'.join(parsed_cv.projects)}",
            metadata={"application_id": application.id}
        )
        return application, skillsAndExperienceDocument
    
    def addApplication(self, parsed_cv: ParsedCV):
        application, skillsAndExperienceDocument = self.processParsedCV(parsed_cv)
        
        # Add to SQL database
        self.sql_query.add(application)
        
        # Add to Vector database
        skillsAndExperienceDocument.id = application.vectorDbUuid
        self.vector_query.add(skillsAndExperienceDocument, id=application.vectorDbUuid)
        
        return application.id
    
    def updateApplication(self, id: str, parsed_cv: ParsedCV):
        application, skillsAndExperienceDocument = self.processParsedCV(parsed_cv)
        application.id = id
        
        # Update in SQL database
        updateId = self.sql_query.updateWithObject(application.id, application)
        if updateId is None:
            return None
        
        # Update in Vector database
        self.vector_query.update(application.vectorDbUuid, skillsAndExperienceDocument)
        
        return application.id
    
    def getApplication(self, id: str):
        # Get from SQL database
        with Session(self.sql_engine) as session:
            sqlQuery = select(Application).where(Application.id == id)
            application = session.exec(sqlQuery).one_or_none()

            if not application:
                return None
            
            # Get from Vector database
            vectorDoc = self.vector_query.selectByIds([application.vectorDbUuid])
            
            return {
                "application": application,
                "education": application.education if application.education else [],
                "experiencedSkills": application.skills if application.skills else [],
                "skillsAndExperience": vectorDoc[0] if vectorDoc else None
            }
    
    def deleteApplication(self, id: str):
        # Delete from SQL database
        deleted_application = self.sql_query.delete(id)
        if not deleted_application:
            return None
        
        # Delete from Vector database
        self.vector_query.delete(deleted_application.vectorDbUuid)
        
        return deleted_application
    
    def searchApplications(self, query: SearchCVQuery, vectorSearchK: int = 20):
        with Session(self.sql_engine) as session:
            name = query.name
            email = query.email
            phone = query.phone
            linkedIn = query.linkedIn
            gitRepo = query.gitRepo
            experiencedSkills = query.experiencedSkills

            # Build SQL query
            sqlQuery = select(Application)
            if name:
                sqlQuery = sqlQuery.where(Application.name.ilike(f"%{name}%"))
            if email:
                sqlQuery = sqlQuery.where(Application.email.ilike(f"%{email}%"))
            if phone:
                sqlQuery = sqlQuery.where(Application.phone.ilike(f"%{phone}%"))
            if linkedIn:
                sqlQuery = sqlQuery.where(Application.linkedIn.ilike(f"%{linkedIn}%"))
            if gitRepo:
                sqlQuery = sqlQuery.where(Application.gitRepo.ilike(f"%{gitRepo}%"))

            if experiencedSkills:
                for skill, experience in experiencedSkills.items():
                    sqlQuery = sqlQuery.where(
                        and_(
                            ExperiencedSkill.skill.ilike(f"%{skill}%"),
                            ExperiencedSkill.yearsOfExperience >= experience
                        )
                    )

            # Search in vector database
            keywords: List[str] = query.keywords
            skills: List[str] = query.skills
            jobTitles: List[str] = query.jobTitles
            location = query.location
            requirementDescription = query.requirementDescription

            vectorQuery = ("Keywords: " + ", ".join(keywords) + "\n") if (keywords != None and keywords != []) else "" + \
                          ("Skills: " + ", ".join(skills) + "\n") if (skills != None and skills != []) else "" + \
                          ("Job Titles: " + ", ".join(jobTitles) + "\n") if (jobTitles != None and jobTitles != []) else "" + \
                          "Address: " + (location if location else "") + "\n" + \
                          "Description: " + (requirementDescription if requirementDescription else "")
            
            vectorDocs = self.vector_query.select(query=vectorQuery, k=vectorSearchK)
            documentIds = [doc.id for doc in vectorDocs if doc.id]

            if documentIds:
                sqlQuery = sqlQuery.where(Application.vectorDbUuid.in_(documentIds))

            results = session.exec(sqlQuery).all()
            applications = []

            for application in results:
                correspondingExperiencedDoc = next(filter(
                    lambda doc: doc.id == application.vectorDbUuid,
                    vectorDocs
                ), None)
                education = application.education if application.education else []
                experiencedSkills = application.skills if application.skills else []
                applications.append({
                    "application": application,
                    "education": education,
                    "experiencedSkills": experiencedSkills,
                    "skillsAndExperience": correspondingExperiencedDoc.page_content if correspondingExperiencedDoc else None
                })
        return applications
    
    def getAllApplications(self, page: int = 1, pageSize: int = 10, orderBy: str = "lastUpdated"):
        
        with Session(self.sql_engine) as session:
            offset = (page - 1) * pageSize
            sqlQuery = select(Application).offset(offset).limit(pageSize)
            if orderBy == "name":
                sqlQuery = sqlQuery.order_by(Application.name.asc())
            elif orderBy == "nameDesc":
                sqlQuery = sqlQuery.order_by(Application.name.desc())
            elif orderBy == "id":
                sqlQuery = sqlQuery.order_by(Application.id.asc())
            elif orderBy == "lastUpdated":
                sqlQuery = sqlQuery.order_by(Application.lastUpdated.asc())
            else: # Default to lastUpdated descending
                sqlQuery = sqlQuery.order_by(Application.lastUpdated.desc())

            results = session.exec(sqlQuery).all()
            totalPages = (session.exec(select(func.count(Application.id))).one() + pageSize - 1) // pageSize
            applications = []

            for application in results:
                vectorDoc = self.vector_query.selectByIds([application.vectorDbUuid])
                applications.append({
                    "application": application,
                    "education": application.education if application.education else [],
                    "experiencedSkills": application.skills if application.skills else [],
                    "skillsAndExperience": vectorDoc[0].page_content if vectorDoc else None
                })
        return { 'pageCount': totalPages, 'applications': applications }

            


            
            

        
