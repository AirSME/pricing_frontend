from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import re
import pandas as pd
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return render_template('index.html', error="No file selected")
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session['original_file'] = filepath
            
            # Clean the data immediately after upload
            cleaned_path = os.path.join(app.config['UPLOAD_FOLDER'], 'cleaned_' + filename)
            df = pd.read_excel(filepath, engine='openpyxl', header=None, dtype=str)
            pattern = r'^[A-Z0-9/-]*[0-9][A-Z0-9/-]*$'
            matching_rows = df[df[0].apply(lambda x: bool(re.match(pattern, str(x))) if pd.notnull(x) else False)]
            matching_rows.to_excel(cleaned_path, index=False, header=False, engine='openpyxl')
            session['cleaned_file'] = cleaned_path
            
            return render_template('index.html', 
                                step="download",
                                original_filename=filename,
                                cleaned_filename='cleaned_' + filename)
    
    # Clear session if refreshing the page
    if request.method == 'GET' and 'original_file' in session:
        session.pop('original_file', None)
        session.pop('cleaned_file', None)
    
    return render_template('index.html', step="upload")

@app.route('/download')
def download():
    if 'cleaned_file' not in session or not os.path.exists(session['cleaned_file']):
        return redirect(url_for('index'))
    
    cleaned_path = session['cleaned_file']
    csv_path = cleaned_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
    
    # Convert to CSV
    pd.read_excel(cleaned_path, engine='openpyxl').to_csv(csv_path, index=False, encoding='utf-8')
    
    return send_file(
        csv_path,
        as_attachment=True,
        download_name='formatted_data.csv',
        mimetype='text/csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
    