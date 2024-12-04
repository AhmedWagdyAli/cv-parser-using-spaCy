import spacy
import re
from spacy.matcher import Matcher, PhraseMatcher


class CVParser:
    """Parses CV text to extract structured data."""

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.languages_list = ["Arabic", "English", "French", "Spanish", "German"]
        self.skills_list = ["Python", "Java", "SQL", "Testing", "Leadership", "Django", "Machine Learning", "Flutter"]
        self.skills_matcher = PhraseMatcher(self.nlp.vocab)
        patterns = [self.nlp.make_doc(skill) for skill in self.skills_list]
        self.skills_matcher.add("SKILLS", None, *patterns)

    def parse(self, cv_text):
        """Extract structured data."""
        doc = self.nlp(cv_text)
        data = {
            "name": self.extract_name(doc),
            "contact": self.extract_contact(doc),
            "position": self.extract_position(doc),
            "years_of_experience": self.extract_years_of_experience(doc),
            "education": self.extract_education(doc),
            "certificates": self.extract_certificates(doc),
            "languages": self.extract_languages(doc),
            "skills": self.extract_skills(doc),
            'experience': self.extract_experience(doc),
        }
        return data
    def extract_name(self, doc):
        """Extract the name by identifying the first PERSON entity."""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        # Fallback: Look for "Summary" or similar labels as hints
        summary_match = re.search(r"(Summary|Name):\s*(.+)", doc.text, re.IGNORECASE)
        if summary_match:
            return summary_match.group(2).strip()
        return "Name not found"

   

    def extract_contact(self, doc):
        """Extract email and phone number."""
        contact = {"email": None, "phone": None}

        # Email extraction
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        email_match = re.search(email_pattern, doc.text)
        if email_match:
            contact["email"] = email_match.group()

        # Phone number extraction
        phone_pattern = r"(\+?\d[\d\s\-\(\)]{7,15})"
        phone_match = re.search(phone_pattern, doc.text)
        if phone_match:
            contact["phone"] = phone_match.group()

        return contact



    def extract_years_of_experience(self, doc):
        for sent in doc.sents:
            match = re.search(r"(\d+)\s+(years|سنوات)", sent.text.lower())
            if match:
                return match.group(1)
        return "Experience not found"

    def extract_education(self, doc):
        education = []
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in ["bachelor", "master", "phd", "education", "المؤهلات"]):
                education.append(sent.text.strip())
        return "\n".join(education)

    def extract_certificates(self, doc):
        certificates = []
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in ["certificate", "certified", "الشهادة"]):
                certificates.append(sent.text.strip())
        return "\n".join(certificates)

    def extract_languages(self, doc):
        languages = set()
        for token in doc:
            if token.text.capitalize() in self.languages_list:
                languages.add(token.text.capitalize())
        return ", ".join(languages)

    def extract_skills(self, doc):
        """Extract technical skills, programming languages, and design patterns."""
        skills = set()

        # Match phrases using the PhraseMatcher
        matches = self.skills_matcher(doc)
        skills.update([doc[start:end].text for _, start, end in matches])

        # Regex for extracting common skill sections
        skill_sections = ["Programming Languages", "Design Patterns", "Skills","Soft Skills", "Design Patterns"]
        section_pattern = r"(?i)(" + "|".join(skill_sections) + r")\s*:?(.+?)(\n\s*\n|$)"
        matches = re.findall(section_pattern, doc.text, re.DOTALL)

        for _, content, _ in matches:
            # Extract comma-separated or space-separated terms
            extracted_skills = re.split(r"[,\n]", content)
            skills.update(skill.strip() for skill in extracted_skills if skill.strip())

        # Ensure all items in `skills` are strings before joining
        return ", ".join(map(str, sorted(skills))) if skills else "Skills not found"

       
    def extract_experience(self, doc):
        """Extract structured work history: company, dates, role, description."""
        experience = []
        date_pattern = r"(\d{2}/\d{4}|\d{4}–\d{4}|\d{4}-\d{4})"

        # Split text by date patterns
        chunks = re.split(date_pattern, doc.text)
        for i in range(1, len(chunks), 2):  # Process pairs of date and related text
            dates = chunks[i].strip()
            text = chunks[i + 1].strip()

            experience_entry = {"dates": dates, "location": None, "role": None, "company": None, "description": None}

            # Extract role and company
            lines = text.split("\n")
            for line in lines:
                if "Team Leader" in line or "Developer" in line:  # Match roles
                    experience_entry["role"] = line.strip()
                elif any(word.isupper() for word in line.split()):  # Heuristic for company name
                    experience_entry["company"] = line.strip()
                elif "Egypt" in line or "UAE" in line:  # Match locations
                    experience_entry["location"] = line.strip()
                else:  # Remaining lines are part of the description
                    if experience_entry["description"]:
                        experience_entry["description"] += f" {line.strip()}"
                    else:
                        experience_entry["description"] = line.strip()

            # Append only if there's valid data
            if any(value is not None for value in experience_entry.values()):
                experience.append(experience_entry)

        return experience
    def extract_position(self, doc):
        """Extract the first role from the experience section."""
        experiences = self.extract_experience(doc)  # Use the parsed experience data
        if experiences and "role" in experiences[0]:
            return experiences[0]["role"]  # Return the first role found
        return "Position not found"
