
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
        self.workExperiences = cvData.get("workExperiences", [])
        self.projects = cvData.get("projects", [])
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

        self.experiencedSkills = [
            {
                "skill": skill.get("skill"),
                "yearsOfExperience": roundYoE(str(skill.get('yearsOfExperience'))) if skill.get("yearsOfExperience") else None
            } for skill in cvData.get("experiencedSkills", [])   
        ]#cvData.get("experiencedSkills", [])

    