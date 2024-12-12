from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    send_file,
    flash,
    jsonify,
)
from werkzeug.utils import secure_filename
import os
from cv_processor import CVProcessor  # Assuming CVProcessor is in the same directory
from cv_service import CVService
import random
from models import (
    db,
    CV,
    Certificates,
    Skills,
    Experiences,
)  # Import models from models.py
from flask_migrate import Migrate
from sqlalchemy import or_
import zipfile
from io import BytesIO

app = Flask(__name__)


app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["TEMPLATE_FOLDER"] = "./templates"  # For Word templates
app.config["OUTPUT_FOLDER"] = "./output"  # For filled CVs
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://cvflask_user:password@localhost:3306/cvflask"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)
# Ensure directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)


@app.route("/", methods=["get"])
def get_cv_form():
    return render_template("/upload.html")


@app.route("/upload", methods=["POST"])
def upload_cv():
    # Save the uploaded file
    file = request.files["file"]
    filename = secure_filename(file.filename)

    # Define the upload path (keep the original filename with its extension)
    upload_path = os.path.join(app.root_path, "uploads", filename)

    # Save the uploaded file to the target path
    file.save(upload_path)
    # Process the CV
    processor = CVProcessor()
    parsed_data = processor.process(upload_path)
    if not parsed_data:
        return "Error processing CV.", 500

    # Save parsed data to the database

    # Define output path
    output_dir = os.path.join(app.root_path, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f"filled_{filename}.docx")

    processor.fill_template(
        parsed_data, template_path="template.docx", output_path=output_path
    )
    service = CVService(db)
    parsed_data["path_of_cv"] = output_path

    service.save_cv(parsed_data)
    # Check if the file was created
    if not os.path.exists(output_path):
        return "Error: Output file not found.", 500

    # Send the file
    return send_file(output_path, as_attachment=True)


@app.route("/generate", methods=["GET"])
def generate_cv_form():
    return render_template("/generate.html")


@app.route("/generate_cv", methods=["POST"])
def get_cv_data():
    # Query the CV table by job_title
    try:
        # Extract job title from the form data
        job_title = request.form.get("job_title")
        company = request.form.get("company")
        min_experience = request.form.get("years_of_experience")
        skill = request.form.get("skill")
        print(min_experience)
        """  if not job_title:
            return jsonify({"error": "Job title is required"}), 400
         """
        # Query CV data
        """ cv = CV.query.filter(  # Join CV with Experience table
            or_(
                CV.years_of_experience
                == int(min_experience),  # Filter by years of experience
            ),
            # Ensure path_of_cv is not null
        ).first() """
        query = (
            CV.query.join(Experiences).join(Skills).filter(CV.path_of_cv.isnot(None))
        )

        if job_title:
            query = query.filter(CV.job_title.ilike(f"%{job_title}%"))

        if company:
            query = query.filter(Experiences.company.ilike(f"%{company}%"))

        if min_experience is not None:
            query = query.filter(CV.years_of_experience == min_experience)

        if skill:
            print(skill)
            query = query.filter(Skills.name.ilike(f"%{skill}%"))

        cvs = query.all()

        if not cvs:
            return jsonify({"error": "No CVs found with the given criteria"}), 404

        # Filter valid file paths
        valid_files = [cv.path_of_cv for cv in cvs if os.path.isfile(cv.path_of_cv)]

        if not valid_files:
            return jsonify({"error": "No valid CV files found on the server"}), 404

        # Create an in-memory ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in valid_files:
                # Add files to the ZIP archive
                zip_file.write(file_path, os.path.basename(file_path))

        # Prepare the ZIP file for download
        zip_buffer.seek(0)  # Move the cursor to the beginning of the buffer
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="matching_cvs.zip",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":

    app.secret_key = "supersecretkey"  # Needed for flash messages
    app.run(debug=True)
