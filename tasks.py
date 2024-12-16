import os
from spacy import load
from werkzeug.utils import secure_filename
from cv_processor import (
    CVProcessor,
)  # Assuming CVProcessor is the class you use to process CVs
from cv_service import (
    CVService,
)  # Assuming CVService handles saving parsed CV data to the database
import io

from models import db


class tasks:

    @staticmethod
    def parse_cv(file_name, file_content):
        # Secure the file name
        filename = secure_filename(file_name)

        # Define the upload path
        upload_path = os.path.join("uploads", filename)

        with open(upload_path, "wb") as f:
            f.write(file_content)

        processor = CVProcessor()
        parsed_data = processor.process(upload_path)

        if not parsed_data:
            raise Exception("Error processing CV.")

        # Define the output directory for the filled CV
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define the output path
        output_path = os.path.join(output_dir, f"filled_{filename}.docx")

        # Fill the template with parsed data
        processor.fill_template(
            parsed_data, template_path="template.docx", output_path=output_path
        )

        # Save parsed data to the database
        service = CVService(db)
        parsed_data["path_of_cv"] = output_path
        service.save_cv(parsed_data)

        # Check if the output file was created
        if not os.path.exists(output_path):
            raise Exception("Error: Output file not found.")

        return {"status": "success", "output_path": output_path}
