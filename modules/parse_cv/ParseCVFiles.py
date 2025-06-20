from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableMap
from langchain_core.output_parsers import StrOutputParser
from settings import get_settings
from modules.parse_cv.ParsedCV import ParsedCV, roundYoE

import re

settings = get_settings()

openaiCVParsingModel = ChatOpenAI(
    model_name=settings.default_model,
    temperature=0.3,
    api_key=settings.openai_api_key,
    max_retries=3
)

cvParsingPrompt = """
    Instruction: Parse the following CV texts (each of them are between <CV> and </CV> tags) and extract the following information in the following format (answer with no other text):
    - Each parsed CV object should be in the <ParsedCV> and </ParsedCV> tags.
    - The values in each parsed CV object should be kept in the original language of the CV.
    - If a field is not present in the CV, it should be omitted from the output.
    - The name of the applicant should be in the <Name> and </Name> tags.
    - The email of the applicant should be in the <Email> and </Email> tags.
    - The phone number of the applicant should be in the <Phone> and </Phone> tags.
    - The LinkedIn profile URL of the applicant should be in the <LinkedIn> and </LinkedIn> tags.
    - Total years of experience (work experience + projects) of the applicant should be in the <YearOfExperience> and </YearOfExperience> tags.
    - The total years of experience should be calculated by summing the years of experience from work experiences and significant projects (such as internships, freelance work, college/university graduation projects,... etc.).
    - The Git repository URL (like Github and GitLab) of the applicant should be in the <GitRepo> and </GitRepo> tags.
    - The address (their home address or current working address) of the applicant should be in the <Address> and </Address> tags.
    - Each work experience entry should be in the <WorkExperience> and </WorkExperience> tags with all the text in that entry.
    - Each project entry should be in the <Project> and </Project> tags with all the text in that entry.
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
    Detect Fraudulent Transactions using Machine Learning
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
        <Name>John Doe</Name>
        <Email>johndoe@gmail.com</Email>
        <Phone>+1234567890</Phone>
        <LinkedIn>https://www.linkedin.com/in/johndoe</LinkedIn>
        <GitRepo>https://github.com/johndoe</GitRepo>
        <YearOfExperience>4</YearOfExperience>
        <Address>123 Main St, City, Country</Address>
        <WorkExperience>
        ExpriLabs 2022-2024
        - Developed AI models for natural language processing.
        - Led a team of 5 engineers.
        </WorkExperience>
        <WorkExperience>
        TechCorp 2020-2022
        - Worked on cloud computing solutions.
        - Improved system performance by 30%.
        </WorkExperience>
        <Project>
        Detect Fraudulent Transactions using Machine Learning
        - Developed a model to detect fraudulent transactions in real-time.
        - Achieved 95% accuracy in detection.
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


def parseEachCVResponse(cvText: str) -> ParsedCV:
    name = re.search(r"<Name>(.*?)</Name>", cvText)
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

    return ParsedCV({
        "name": name.group(1) if name else None,
        "email": email.group(1) if email else None,
        "phone": phone.group(1) if phone else None,
        "linkedIn": linkedIn.group(1) if linkedIn else None,
        "gitRepo": gitRepo.group(1) if gitRepo else None,
        "address": address.group(1) if address else None,
        "totalYearsOfExperience": roundYoE(totalYoE.group(1)) if totalYoE else None,
        "workExperiences": workExperiences,
        "projects": projects,
        "educations": education_entries,
        "skills": skills,
        "experiencedSkills": [
            {
                "skill": skill[0],
                "yearsOfExperience": skill[1]
            } for skill in experiencedSkills
        ]
    })



def parseCVs(cvTexts: list[str], batchSize=5) -> list[ParsedCV]:
    cvCount = len(cvTexts)
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
                raise Exception("Failed to parse CVs after multiple attempts.")
            
            response = cvParsingChain.invoke({"cv_text": cvText})
            response = re.findall(r"<ParsedCV>(.*?)</ParsedCV>", response, re.DOTALL)
            
            if not response or not isinstance(response, list) or len(response) == 0:
                attempts += 1
                continue
            break
    
        for cv in response:
            parsedCV = parseEachCVResponse(cv)
            parsedCVs.append(parsedCV)

    return parsedCVs


