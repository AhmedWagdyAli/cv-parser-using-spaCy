import spacy
import re
from spacy.matcher import Matcher, PhraseMatcher


class CVParser:
    """Parses CV text to extract structured data."""

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.languages_list = ["Arabic", "English", "French", "Spanish", "German"]
        self.skills_list = [
            "Python",
            "Java",
            "SQL",
            "Testing",
            "Leadership",
            "Django",
            "Machine Learning",
            "Flutter",
        ]
        self.skills_matcher = PhraseMatcher(self.nlp.vocab)
        patterns = [self.nlp.make_doc(skill) for skill in self.skills_list]
        self.skills_matcher.add("SKILLS", None, *patterns)
        self.common_roles = {
            "Manager",
            "Team Leader",
            "Supervisor",
            "Consultant",
            "Analyst",
            "Accountant",
            "Auditor",
            "Engineer",
            "Developer",
            "Designer",
            "Teacher",
            "Marketer",
            "Specialist",
            "Coordinator",
            "Administrator",
            "Technician",
        }

        self.location_keywords = {
            "New York",
            "London",
            "Cairo",
            "San Francisco",
            "Paris",
            "Germany",
            "USA",
            "Canada",
            "India",
            "California",
            "Egypt",
            "Dubai",
            "Tokyo",
            "Japan",
            "Australia",
            "Ireland",
            "Singapore",
            "Brazil",
            "France",
            "Mexico",
            "Italy",
            "South Africa",
            "Russia",
            "China",
            "Korea",
            "Turkey",
            "Indonesia",
            "Pakistan",
            "Bangladesh",
            "Vietnam",
            "Philippines",
            "Taiwan",
            "Austria",
            "Netherlands",
            "Sweden",
            "Belgium",
            "Finland",
            "Norway",
            "Switzerland",
            "Denmark",
            "Iceland",
            "Greece",
            "Portugal",
            "Spain",
            "Ireland",
            "United Kingdom",
            "Germany",
            "France",
            "Italy",
            "Netherlands",
            "Belgium",
            "Finland",
            "Norway",
            "Sweden",
            "Denmark",
            "Iceland",
            "Greece",
            "Portugal",
            "Spain",
            "United Kingdom",
            "Germany",
            "France",
            "Italy",
            "Netherlands",
            "Belgium",
            "Finland",
            "Norway",
            "Sweden",
            "Denmark",
            "Cairo",
            "Alexandria",
            "Mansoura",
            "riyadh",
            "Jiddah",
            "Makkah",
            "Saudi Arabia",
            "Tawuniya",
            "High School",
            "Languages" "Experience",
            "Education",
            "Page 1 of 1",
            "Page 2 of 2",
            "Page 3 of 3",
            "Page 4 of 4",
            "Page 5 of 5",
            "Page 6 of 6",
            "Riyadh",
            "bachelor of",
            "university",
            "Bachelor’s Degree",
            "Certifications",
            "Experience",
            "Summary",
            # Add more location keywords as necessary
        }

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
            "experience": self.extract_experience(doc),
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
        return 0

    def extract_education(self, doc):
        education = []
        for sent in doc.sents:
            if any(
                keyword in sent.text.lower()
                for keyword in ["bachelor", "master", "phd", "education", "المؤهلات"]
            ):
                education.append(sent.text.strip())
        return "\n".join(education)

    def extract_certificates(self, doc):
        certificates = []
        for sent in doc.sents:
            if any(
                keyword in sent.text.lower()
                for keyword in ["certificate", "certified", "الشهادة"]
            ):
                certificates.append(sent.text.strip())
        # todo: insert into database here
        return "\n".join(certificates)

    def extract_languages(self, doc):
        languages = set()
        for token in doc:
            if token.text.capitalize() in self.languages_list:
                languages.add(token.text.capitalize())
        return ", ".join(languages)

    """ def extract_skills(self, doc):
        skills = set()

        # Match phrases using the PhraseMatcher
        matches = self.skills_matcher(doc)
        skills.update([doc[start:end].text for _, start, end in matches])

        # Regex for extracting common skill sections
        skill_sections = ["Programming Languages", "Design Patterns", "Skills","Soft Skills","المهارات"]
        section_pattern = r"(?i)(" + "|".join(skill_sections) + r")\s*:?(.+?)(\n\s*\n|$)"
        matches = re.findall(section_pattern, doc.text, re.DOTALL)

        for _, content, _ in matches:
            # Extract comma-separated or space-separated terms
            extracted_skills = re.split(r"[,\n]", content)
            skills.update(skill.strip() for skill in extracted_skills if skill.strip())

        # Ensure all items in `skills` are strings before joining
        # todo: insert into database here
      
        return ", ".join(map(str, sorted(skills))) if skills else "Skills not found" """

    """  def extract_skills(self, doc):
        skills = set()

        # Match phrases using the PhraseMatcher
        matches = self.skills_matcher(doc)
        skills.update([doc[start:end].text for _, start, end in matches])

        # Regex for extracting common skill sections
        skill_sections = [
            "Programming Languages",
            "Design Patterns",
            "Skills",
            "Soft Skills",
            "المهارات",
        ]
        section_pattern = (
            r"(?i)(" + "|".join(skill_sections) + r")\s*:?(.+?)(\n\s*\n|$)"
        )
        matches = re.findall(section_pattern, doc.text, re.DOTALL)

        for _, content, _ in matches:
            # Extract comma-separated or space-separated terms
            extracted_skills = re.split(r"[,\n]", content)
            for skill in extracted_skills:
                skill = skill.strip()
                # Skip skills resembling dates
                if re.match(
                    r"\b(\d{2}/\d{4}|\d{4}[-–]\d{4}|\d{4})\b", skill
                ):  # Matches dates or date ranges
                    continue
                skills.add(skill)

        # Ensure all items in `skills` are strings before joining
        return ", ".join(map(str, sorted(skills))) if skills else "Skills not found" """

    def extract_skills(self, doc):
        skills = set()

        # Match phrases using the PhraseMatcher
        matches = self.skills_matcher(doc)
        skills.update([doc[start:end].text for _, start, end in matches])

        # Regex for extracting common skill sections
        skill_sections = [
            "Programming Languages",
            "Design Patterns",
            "Skills",
            "Soft Skills",
            "المهارات",
        ]
        section_pattern = (
            r"(?i)(" + "|".join(skill_sections) + r")\s*:?(.+?)(\n\s*\n|$)"
        )
        matches = re.findall(section_pattern, doc.text, re.DOTALL)
        date_pattern = re.compile(
            r"(?i)(\b(january|february|march|april|may|june|july|august|september|october|november|december)\b\s*\d{4}"
            r"(\s*[-–]\s*(\b(january|february|march|april|may|june|july|august|september|october|november|december)\b\s*\d{4})?)?"
            r"(?:\s*\(\d+\s*(?:year|month|years|months)\))?)"
        )

        # Common locations or location-like terms to exclude

        for _, content, _ in matches:
            # Extract comma-separated or space-separated terms
            extracted_skills = re.split(r"[,\n]", content)
            for skill in extracted_skills:
                skill = skill.strip()
                # Skip skills resembling dates
                if re.match(
                    r"\b(\d{2}/\d{4}|\d{4}[-–]\d{4}|\d{4})\b", skill
                ):  # Matches dates or date ranges
                    continue
                if date_pattern.match(skill):
                    continue
                # Exclude locations
                if skill in self.location_keywords:
                    continue
                # Add valid skill
                skills.add(skill)

        # Ensure all items in `skills` are strings before joining
        return ", ".join(map(str, sorted(skills))) if skills else "Skills not found"

    """ def extract_experience(self, doc):
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

        return experience """

    def extract_experience(self, doc):
        self.nlp = spacy.load("en_core_web_sm")
        # Common roles across professions

        experience = []

        date_pattern = r"(\d{2}/\d{4}|\d{4}–\d{4}|\d{4}-\d{4}|\d{4})"

        # Split text by date patterns
        chunks = re.split(date_pattern, doc.text)
        for i in range(1, len(chunks), 2):  # Process pairs of date and related text
            dates = chunks[i].strip()
            related_text = chunks[i + 1].strip()

            experience_entry = {
                "dates": dates,
                "location": None,
                "role": None,
                "company": None,
                "description": None,
            }

            # Process the related text with SpaCy
            related_doc = self.nlp(related_text)

            # Extract entities dynamically
            for ent in related_doc.ents:
                if ent.label_ == "ORG" and not experience_entry["company"]:
                    experience_entry["company"] = ent.text
                elif ent.label_ == "GPE" and not experience_entry["location"]:
                    experience_entry["location"] = ent.text
                elif ent.label_ in {"PERSON", "TITLE"} and not experience_entry["role"]:
                    # Use title-like entities as roles
                    experience_entry["role"] = ent.text

            # Infer roles and descriptions heuristically
            lines = related_text.split("\n")
            for line in lines:
                # Check for a role using a broader list and heuristic patterns
                if any(role.lower() in line.lower() for role in self.common_roles):
                    experience_entry["role"] = line.strip()
                elif (
                    any(word.istitle() for word in line.split())
                    and not experience_entry["company"]
                ):
                    experience_entry["company"] = (
                        line.strip()
                    )  # Infer company from capitalized patterns
                else:
                    # Add to description if not identified as a role or company
                    if experience_entry["description"]:
                        experience_entry["description"] += f" {line.strip()}"
                    else:
                        experience_entry["description"] = line.strip()

            # Append entry only if valid data exists
            if any(value for value in experience_entry.values()):
                experience.append(experience_entry)

        return experience

    def extract_position(self, doc):
        """Extract the first role from the experience section."""
        experiences = self.extract_experience(doc)  # Use the parsed experience data
        if experiences and "role" in experiences[0]:
            return experiences[0]["role"]  # Return the first role found
        return "Position not found"
