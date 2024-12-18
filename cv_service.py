from models import Certificates, Skills, CV, Experiences
import re


class CVService:
    def __init__(self, db):
        self.db = db

    def save_cv(self, parsed_data):
        """Save parsed data into the database."""
        print(parsed_data)
        phone = parsed_data.get("contact", {}).get("phone", None)
        email = parsed_data.get("contact", {}).get("email", None)

        if phone:
            # Clean up the phone number: remove unwanted characters (spaces, parentheses, etc.)
            phone = re.sub(r"[^\d\+]", "", phone)

        # Optionally: check if the phone number is valid (length or format check)

        cv = CV(
            job_title=parsed_data["position"],
            path_of_cv=parsed_data["path_of_cv"],
            years_of_experience=parsed_data["years_of_experience"],
            phone=phone,
            email=email,
        )
        self.db.session.add(cv)
        self.db.session.flush()  # Get the ID for CV

        # Insert certificates
        for cert in parsed_data["certificates"].split("\n"):
            if cert:
                certificate = Certificates(cv_id=cv.id, name=cert.strip())
                self.db.session.add(certificate)

        # Insert skills
        for skill in parsed_data["skills"].split(","):
            if skill:
                skill_entry = Skills(cv_id=cv.id, name=skill.strip())
                self.db.session.add(skill_entry)
        for experience in parsed_data["experience"]:
            truncated_description = (experience.get("description") or "")[:255] or None

            experience_entry = Experiences(
                cv_id=cv.id,
                company=experience.get("company"),
                start_date=experience.get("dates"),
                end_date=experience.get("end_date"),
                description=truncated_description,
            )
            self.db.session.add(experience_entry)
        # Commit to the database
        self.db.session.commit()
        return cv.id

    def get_cv(self, cv_id):
        cv = CV.query.filter_by(id=cv_id).first()

        if not cv:
            return "CV not found", 404

        # Fetch related objects using .all()
        skills = [skill.name for skill in cv.skills.all()]
        experiences = [exp for exp in cv.experiences.all()]

        if cv:
            return cv, skills, experiences
        return None
