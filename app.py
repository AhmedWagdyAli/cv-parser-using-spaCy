from flask import Flask, request, render_template, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
import os
from cv_processor import CVProcessor  # Assuming CVProcessor is in the same directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['TEMPLATE_FOLDER'] = './templates'  # For Word templates
app.config['OUTPUT_FOLDER'] = './output'       # For filled CVs

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
@app.route('/', methods=['get'])

def get_cv_form():
    return render_template('/upload.html')

@app.route('/upload', methods=['POST'])
def upload_cv():
    # Save the uploaded file
    file = request.files['file']
    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.root_path, 'uploads', filename)
    file.save(upload_path)

    # Process the CV
    processor = CVProcessor()
    parsed_data = processor.process(upload_path)

    if not parsed_data:
        return "Error processing CV.", 500

    # Define output path
    output_dir = os.path.join(app.root_path, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f"filled_{filename}")
    processor.fill_template(parsed_data, template_path='template.docx', output_path=output_path)

    # Check if the file was created
    if not os.path.exists(output_path):
        return "Error: Output file not found.", 500

    # Send the file
    return send_file(output_path, as_attachment=True)



if __name__ == "__main__":
    app.secret_key = "supersecretkey"  # Needed for flash messages
    app.run(debug=True)
