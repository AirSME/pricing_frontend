import re
import os
import pandas as pd
from io import BytesIO
from flask import Blueprint, request, session, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

excel_formatter_bp = Blueprint('excel_formatter', __name__)

SKU_PATTERN = re.compile(r'^[A-Z0-9]{1,6}[-/]?[A-Z0-9]{0,6}$')

def is_valid_sku(value):
    if pd.isna(value) or not isinstance(value, str):
        return False
    return bool(SKU_PATTERN.match(value.strip()))

@excel_formatter_bp.route('/upload', methods=['POST'])
def upload_file():
    print("Frontend hit /upload route")
    file = request.files.get('file')

    if not file or file.filename == '':
        return jsonify({"error": "No file provided"}), 400

    try:
        filename = secure_filename(file.filename)
        uploads_folder = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(uploads_folder, exist_ok=True)
        upload_path = os.path.join(uploads_folder, filename)
        print(f"Saving uploaded file to: {upload_path}")  
        file.save(upload_path)
        return jsonify({"message": "File uploaded", "filename": filename})
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500


@excel_formatter_bp.route('/clean', methods=['POST'])
def clean_file():
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({"error": "No filename provided"}), 400

    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))

    if not os.path.exists(upload_path):
        return jsonify({"error": "File not found"}), 404

    try:
        df = pd.read_excel(upload_path, engine='openpyxl', dtype=str)

        # Detect SKU-like columns
        sku_cols = [
            col for col in df.columns
            if not df[col].dropna().empty and is_valid_sku(str(df[col].dropna().iloc[0]))
        ]

        if not sku_cols:
            filtered = df[df.apply(lambda row: any(is_valid_sku(str(cell)) for cell in row), axis=1)]
        else:
            filtered = df[df[sku_cols].apply(lambda row: any(is_valid_sku(str(cell)) for cell in row), axis=1)]

        cleaned_filename = f"cleaned_{secure_filename(filename)}"
        cleaned_path = os.path.join(current_app.config['UPLOAD_FOLDER'], cleaned_filename)

        filtered.to_excel(cleaned_path, index=False, engine='openpyxl')

        return jsonify({
            "message": "File cleaned",
            "rows": len(filtered),
            "filename": cleaned_filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@excel_formatter_bp.route('/download', methods=['GET'])
def download_file():
    if 'cleaned' not in session:
        return jsonify({"error": "No cleaned file to download"}), 400

    try:
        df = pd.read_json(session['cleaned'])
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        return send_file(
            output,
            download_name='cleaned_products.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
