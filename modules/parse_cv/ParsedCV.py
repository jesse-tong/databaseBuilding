
def roundYoE(yearsOfExperience: str) -> float | None:
    # Round the years of experience to multiples of 0.5
    try:
        years = float(yearsOfExperience)
        if years is None:
            return None
        return round(years * 2) / 2
    except ValueError:
        return None

class ParsedCV():
    """
    A class to represent a parsed CV with structured data.
    """
    def __init__(self, cvData: dict):
        self.name = cvData.get("name")
        self.email = cvData.get("email")
        self.phone = cvData.get("phone")
        self.linkedIn = cvData.get("linkedIn")
        self.gitRepo = cvData.get("gitRepo")
        self.address = cvData.get("address")
        self.totalYoE = roundYoE(str(cvData.get("totalYearsOfExperience", 0)))
        self.workExperiences = [
            {
                "company": we.get("company"),
                "position": we.get("position"),
                "startDate": we.get("startDate"),
                "endDate": we.get("endDate"),
                "description": we.get("description")
            } for we in cvData.get("workExperiences", dict())
        ]
        self.projects = [
            {
                "name": project.get("name"),
                "startDate": project.get("startDate"),
                "endDate": project.get("endDate"),
                "description": project.get("description")
            } for project in cvData.get("projects", dict())
        ]
        self.educations = [
            {
                "degree": edu.get("degree"),
                "institution": edu.get("institution"),
                "year": edu.get("year"),
                "gpa": edu.get("gpa")
            } for edu in cvData.get("educations", dict())
        ]
        self.skills = [
            skill for skill in cvData.get("skills", [])
        ]

        self.experiencedSkills = list(filter(lambda x: x != None, [
            {
                "skill": skill.get("skill"),
                "yearsOfExperience": roundYoE(str(skill.get('yearsOfExperience')))
            } if skill.get("yearsOfExperience") else None for skill in cvData.get("experiencedSkills", [])   
        ])) # Should only include skills with years of experience

    def __str__(self):
        return f"ParsedCV(name={self.name},\n  email={self.email},\n  phone={self.phone},\n  linkedIn={self.linkedIn},\n  gitRepo={self.gitRepo},\n  totalYoE={self.totalYoE}" + \
        f",\n  workExperiences={self.workExperiences},\n  projects={self.projects},\n  educations={self.educations},\n  skills={self.skills},\n  experiencedSkills={self.experiencedSkills})"
    
    

    