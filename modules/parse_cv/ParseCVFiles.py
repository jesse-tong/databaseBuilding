from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableMap
from langchain_core.output_parsers import StrOutputParser
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langfuse import observe, get_client

from settings import get_settings
from modules.parse_cv.ParsedCV import ParsedCV, roundYoE
from dateutil.parser import parse as date_parse
from datetime import datetime
import re

settings = get_settings()

openaiCVParsingModel = ChatOpenAI(
    model_name=settings.default_model,
    temperature=0.3,
    api_key=settings.openai_api_key,
    max_retries=3
)

langfuseTracer = Langfuse(
    secret_key=settings.langfuse_secret_key,
    public_key=settings.langfuse_public_key,
    host=settings.langfuse_host,
)

langfuseHandler = CallbackHandler()

cvParsingPrompt = """
    Instruction: Parse the following CV texts (each of them are between <CV> and </CV> tags) and extract the following information in the following format (answer with no other text):
    - Each parsed CV object should be in the <ParsedCV> and </ParsedCV> tags.
    - The values in each parsed CV object should be kept in the original language of the CV.
    - If a field is not present in the CV, it should be omitted from the output.
    - The name of the applicant should be in the <ApplicationName> and </ApplicationName> tags.
    - The email of the applicant should be in the <Email> and </Email> tags.
    - The phone number of the applicant should be in the <Phone> and </Phone> tags.
    - The LinkedIn profile URL of the applicant should be in the <LinkedIn> and </LinkedIn> tags.
    - Total years of experience (work experience + projects) of the applicant should be in the <YearOfExperience> and </YearOfExperience> tags.
    - The total years of experience should be calculated by summing the years of experience from work experiences and significant projects (such as internships, freelance work, college/university graduation projects,... etc.).
    - The Git repository URL (like Github and GitLab) of the applicant should be in the <GitRepo> and </GitRepo> tags.
    - The address (their home address or current working address) of the applicant should be in the <Address> and </Address> tags.
    - Each work experience entry should be in the <WorkExperience> and </WorkExperience> tags.
    - In each work experience entry, the company name should be in <Company> and </Company>, followed by the position held in <Position> and </Position> tags, start date between <StartDate> and </StartDate> tags, 
    end date (if applicable) between <EndDate> and </EndDate> tags, and description of the work experience in <Description> and </Description> tags.
    - Each project entry should be in the <Project> and </Project> tags, in each project entry, the name of the project should be in <ProjectName> and </ProjectName> tags,
        followed by the description of the project in <Description> and </Description> tags, start date between <StartDate> and </StartDate> tags,
        end date (if applicable) between <EndDate> and </EndDate> tags.
    - Each education entry should be in the <Education> and </Education> tags with the following fields:
        + Degree: in the <Degree> and </Degree> tags.
        + Institution: in the <Institution> and </Institution> tags.
        + Year: in the <Year> and </Year> tags.
        + GPA: in the <GPA> and </GPA> tags.
    - Each skill entry should be in the <Skill> and </Skill> tags with all the text in that entry.
    - For skills and job titles with experience (e.g. Spring Boot, embedded programming, project management,...), for each of them 
    should be in the <ExperiencedSkill> and <ExperiencedSkill> tags with corresponding years of experience in the <YoE> and </YoE> tag in the same line of that skill/job title. 
    If that skill doesn't have a work experience with time associated with it, parse it like other skill entries (wrap it in <Skill> and </Skill> tags) instead.
    - Each certification entry should be in the <Certification> and </Certification> tags with all the text in that entry.

    Example (do not parse this example, just use it as a reference for the output format):
    <EXAMPLE_CV>
    Name: John Doe  Email: johndoe@gmail.com  Phone: +1234567890
    LinkedIn: https://www.linkedin.com/in/johndoe  Github: https://github.com/johndoe
    Address: 123 Main St, City, Country
    Work Experience:
    ExpriLabs          2022-2024
    - Developed AI models for natural language processing.
    - Led a team of 5 engineers as a project manager.
    TechCorp 2020-2022
    - Worked on cloud computing solutions.
    - Improved system performance by 30%.
    Projects:
    Detect Fraudulent Transactions using Machine Learning June 2019 - December 2019
    - Developed a model to detect fraudulent transactions in real-time.
    - Achieved 95% accuracy in detection.
    Education:
    Degree: Bachelor of Science in Computer Science    2016-2020
    Institution: University of Technology, GPA: 3.8
    Skills: Python, Machine Learning
    Certifications: Certified Data Scientist
    </EXAMPLE_CV>

    The output should be in the following format:

    <ParsedCV>
        <ApplicationName>John Doe</ApplicationName>
        <Email>johndoe@gmail.com</Email>
        <Phone>+1234567890</Phone>
        <LinkedIn>https://www.linkedin.com/in/johndoe</LinkedIn>
        <GitRepo>https://github.com/johndoe</GitRepo>
        <YearOfExperience>4</YearOfExperience>
        <Address>123 Main St, City, Country</Address>
        <WorkExperience>
            <Company>ExpriLabs</Company>
            <StartDate>2022</StartDate>
            <EndDate>2024</EndDate>
            <Position>Project Manager</Position>
            <Description>
            - Developed AI models for natural language processing.
            - Led a team of 5 engineers.
            </Description>
        </WorkExperience>
        <WorkExperience>
            <Company>TechCorp</Company>
            <StartDate>2020</StartDate>
            <EndDate>2022</EndDate>
            <Position>Cloud Engineer</Position>
            <Description>
            - Worked on cloud computing solutions.
            - Improved system performance by 30%.
            </Description>
        </WorkExperience>
        <Project>
            <ProjectName>Detect Fraudulent Transactions using Machine Learning</ProjectName>
            <StartDate>June 2019</StartDate>
            <EndDate>December 2019</EndDate>
            <Description>
            - Developed a model to detect fraudulent transactions in real-time.
            - Achieved 95% accuracy in detection.
            </Description>
        </Project>
        <Education>
            <Degree>Bachelor of Science in Computer Science</Degree>
            <Institution>University of Technology</Institution>
            <Year>2016-2020</Year>
            <GPA>3.8</GPA>
        </Education>
        <Skill>Python</Skill>
        <Skill>Machine Learning</Skill>
        <ExperiencedSkill>Cloud computing</ExperiencedSkill><YoE>2</YoE>
        <ExperiencedSkill>Project management</ExperiencedSkill><YoE>2</YoE>
        <Certification>Certified Data Scientist</Certification>
    </ParsedCV>

    End of instruction.
"""

cvParsingPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system", cvParsingPrompt
        ),
        (
            "human", "Now these are the CVs you need to parse:\n{cv_text}"
        )
    ]
)

cvParsingChain = (
    RunnableMap({
        "cv_text": RunnablePassthrough()
    }) |
    cvParsingPromptTemplate |
    openaiCVParsingModel |
    StrOutputParser() 
)

def parsingDateString(dateString: str) -> datetime | None:
    try:
        return date_parse(dateString)
    except ValueError:
        return None

def parseEachCVResponse(cvText: str) -> ParsedCV:
    name = re.search(r"<ApplicationName>(.*?)</ApplicationName>", cvText)
    email = re.search(r"<Email>(.*?)</Email>", cvText)
    phone = re.search(r"<Phone>(.*?)</Phone>", cvText)
    linkedIn = re.search(r"<LinkedIn>(.*?)</LinkedIn>", cvText)
    gitRepo = re.search(r"<GitRepo>(.*?)</GitRepo>", cvText)
    address = re.search(r"<Address>(.*?)</Address>", cvText)
    totalYoE = re.search(r"<YearOfExperience>(.*?)</YearOfExperience>", cvText)
    workExperiences = re.findall(r"<WorkExperience>(.*?)</WorkExperience>", cvText, re.DOTALL)
    projects = re.findall(r"<Project>(.*?)</Project>", cvText, re.DOTALL)
    educations = re.findall(r"<Education>(.*?)</Education>", cvText, re.DOTALL)
    skills = re.findall(r"<Skill>(.*?)</Skill>", cvText)
    experiencedSkills = re.findall(r"<ExperiencedSkill>(.*?)</ExperiencedSkill><YoE>(.*?)</YoE>", cvText)


    education_entries = []
    for education in educations:
        degree = re.search(r"<Degree>(.*?)</Degree>", education)
        institution = re.search(r"<Institution>(.*?)</Institution>", education)
        year = re.search(r"<Year>(.*?)</Year>", education)
        gpa = re.search(r"<GPA>(.*?)</GPA>", education)
        education_entries.append({
                "degree": degree.group(1) if degree else None,
                "institution": institution.group(1) if institution else None,
                "year": year.group(1) if year else None,
                "gpa": gpa.group(1) if gpa else None
        })

    work_experience_entries = []
    for workExperience in workExperiences:
        company = re.search(r"<Company>(.*?)</Company>", workExperience)
        position = re.search(r"<Position>(.*?)</Position>", workExperience)
        startDate = re.search(r"<StartDate>(.*?)</StartDate>", workExperience)
        endDate = re.search(r"<EndDate>(.*?)</EndDate>", workExperience)
        description = re.search(r"<Description>(.*?)</Description>", workExperience, re.DOTALL)

        work_experience_entries.append({
            "company": company.group(1) if company else None,
            "position": position.group(1) if position else None,
            "startDate": parsingDateString(startDate.group(1)) if startDate else None,
            "endDate": parsingDateString(endDate.group(1)) if endDate else None,
            "description": description.group(1).strip() if description else None
        })

    project_entries = []
    for project in projects:
        projectName = re.search(r"<ProjectName>(.*?)</ProjectName>", project)
        startDate = re.search(r"<StartDate>(.*?)</StartDate>", project)
        endDate = re.search(r"<EndDate>(.*?)</EndDate>", project)
        description = re.search(r"<Description>(.*?)</Description>", project, re.DOTALL)

        project_entries.append({
            "name": projectName.group(1) if projectName else None,
            "startDate": parsingDateString(startDate.group(1)) if startDate else None,
            "endDate": parsingDateString(endDate.group(1)) if endDate else None,
            "description": description.group(1).strip() if description else None
        })

    return ParsedCV({
        "name": name.group(1) if name else None,
        "email": email.group(1) if email else None,
        "phone": phone.group(1) if phone else None,
        "linkedIn": linkedIn.group(1) if linkedIn else None,
        "gitRepo": gitRepo.group(1) if gitRepo else None,
        "address": address.group(1) if address else None,
        "totalYearsOfExperience": roundYoE(totalYoE.group(1)) if totalYoE else None,
        "workExperiences": work_experience_entries,
        "projects": project_entries,
        "educations": education_entries,
        "skills": skills,
        "experiencedSkills": [
            {
                "skill": skill[0],
                "yearsOfExperience": skill[1]
            } for skill in experiencedSkills
        ]
    })


@observe(name="ParseCVs")
def parseCVs(cvTexts: list[str], batchSize=5) -> list[ParsedCV]:
    langfuseClient = get_client()

    cvCount = len(cvTexts)
    with langfuseClient.start_as_current_span(name="ParseCVs"):
        langfuseClient.update_current_trace(session_id="parse_cvs")
        langfuseClient.update_current_span(
            level="DEBUG",
            status_message=f"Parsing {cvCount} CVs with batch size {batchSize}",
        )

    if cvCount == 0:
        return []
    
    parsedCVs = []
    for i in range(0, cvCount, batchSize):
        batch = cvTexts[i:i + batchSize]
        cvText = "\n".join([f"<CV>{text}</CV>" for text in batch])

        maxAttempts = 3
        attempts = 0
        
        while attempts < maxAttempts:

            if attempts == maxAttempts - 1:
                with langfuseClient.start_as_current_span(name="ParseCVsError"):
                    langfuseClient.update_current_trace(session_id="parse_cvs")
                    langfuseClient.update_current_span(
                        level="ERROR",
                        status_message=f"Failed to parse CVs after {maxAttempts} attempts."
                    )
                raise Exception("Failed to parse CVs after multiple attempts.")
            
            # Invoke the parsing chain with the CV text
            # Use Langfuse to trace the invocation
            response = cvParsingChain.invoke({"cv_text": cvText}, config={"callbacks": [langfuseHandler], "metadata": {"langfuse_session_id": "parse_cvs"}})
            response = re.findall(r"<ParsedCV>(.*?)</ParsedCV>", response, re.DOTALL)
            
            if not response or not isinstance(response, list) or len(response) == 0:
                attempts += 1
                continue
            break
    
        for cv in response:
            parsedCV = parseEachCVResponse(cv)
            parsedCVs.append(parsedCV)

    return parsedCVs


