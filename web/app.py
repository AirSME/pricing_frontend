from flask import Flask, jsonify, send_file
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import csv
import os
import tempfile

def upload_to_gcs(local_file_path, bucket_name, destination_blob_name):
    from pathlib import Path

    key_path = Path(__file__).parent.parent / "file-uploader-key.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(key_path.resolve())

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)
    print(f"✅ Uploaded {local_file_path} to gs://{bucket_name}/{destination_blob_name}")


app = Flask(__name__)

API_URL = "https://erp.nology.co.za/NologyDataFeed/api/Products/View"
USERNAME = os.getenv("NOLOGY_USERNAME")
SECRET = os.getenv("NOLOGY_SECRET")

@app.route("/")
def home():
    return "Use /products (live), /dummy (local), or /download (CSV). /test-data"

# 🔹 LIVE PRODUCT FEED
@app.route("/products")
def get_products():
    if not USERNAME or not SECRET:
        return "Missing API credentials. Please set NOLOGY_USERNAME and NOLOGY_SECRET.", 500

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "Username": USERNAME,
        "Secret": SECRET,
        "ImageData": False,
        "ReturnType": "JSON"
    }

    try:
        response = requests.get(
            API_URL,
            headers=headers,
            auth=(USERNAME, SECRET),
            data=json.dumps(payload),
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

        # ✅ Create a temporary file and write JSON to it
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp_file:
            json.dump(data, tmp_file, indent=2)
            local_file_path = tmp_file.name

        # ✅ Upload to Google Cloud Storage
        upload_to_gcs(
            local_file_path,
            bucket_name="nology-sync-bucket",
            destination_blob_name="nology_test.json"
        )

        return jsonify({"message": "Synced to GCS", "records": len(data)})

    except Exception as e:
        return f"Live API request failed: {str(e)}", 500



# 🔹 DUMMY DATA (offline testing)
@app.route("/dummy")
def get_dummy_data():
    try:
        file_path = os.path.join(os.path.dirname(__file__), "nology_raw.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return "nology_raw.json not found in /web folder.", 404
    except Exception as e:
        return f"Failed to load dummy data: {e}", 500


# 🔹 DOWNLOAD CSV FROM DUMMY FILE
@app.route("/download")
def download_csv():
    try:
        with open("nology_raw.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        filename = "products_export.csv"
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "SKU", "Name", "Description", "Price", "Stock", "Image URL", "Category", "Brand"
            ])
            for item in data:
                writer.writerow([
                    item.get("SKUCode", ""),
                    item.get("ProductDescription", ""),
                    item.get("ProductLongDescription", ""),
                    item.get("SellPriceInclVAT", ""),
                    item.get("StockQuantity", ""),
                    item.get("ImageURL", ""),
                    item.get("CategoryName", ""),
                    item.get("BrandName", "")
                ])

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"CSV generation failed: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
