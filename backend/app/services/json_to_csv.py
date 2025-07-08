from flask import Blueprint, jsonify
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

import requests
import json
import csv
import os
import tempfile

json_to_csv_bp = Blueprint('json_to_csv', __name__)

def round_up_to_99(price):
    try:
        price = float(price)
        if price < 100:
            return ((price // 10) + 1) * 10 - 1
        elif price < 1000:
            return ((price // 100) + 1) * 100 - 1
        else:
            return ((price // 100) + 1) * 100 - 1
    except:
        return price

API_URL = "https://erp.nology.co.za/NologyDataFeed/api/Products/View"
USERNAME = os.getenv("NOLOGY_USERNAME")
SECRET = os.getenv("NOLOGY_SECRET")

def upload_to_gcs(local_file_path, bucket_name, destination_blob_name):
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json")
    creds_file.write(creds_json)
    creds_file.close()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_file.name
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_file_path)

def get_csv_row(item):
    return {
        "post_title": item.get("ShortDescription", ""),
        "post_name": "",
        "post_status": "draft",
        "sku": item.get("Model", ""),
        "downloadable": "no",
        "virtual": "no",
        "visibility": "visible",
        "stock": (
            "outofstock" if any(loc.get("CPT", 0.0) == 0.0 for loc in item.get("TotalQtyAvailable", []))
            else "instock"
        ),
        "stock_status": "no",
        "backorders": "no",
        "manage_stock": "",
        "regular_price": round_up_to_99(float(item.get("Price", 0)) * 1.20),
        "sale_price": round_up_to_99(float(item.get("Price", 0)) * 1.15),
        "weight": "",
        "length": "",
        "width": "",
        "height": "",
        "tax_status": "",
        "tax_class": "",
        "tax:product_type": "",
        "tax:product_cat": "",
        "tax:product_tag": "",
        "tax:product_brand": item.get("Brand", ""),
        "attribute:Color": "",
        "attribute_data:Color": "",
        "attribute:Size": "",
        "attribute_data:Size": "",
        "images": item.get("AllImages", "")
    }

@json_to_csv_bp.route("/products")
def get_products():
    if not USERNAME or not SECRET:
        return "Missing API credentials. Please set NOLOGY_USERNAME and NOLOGY_SECRET.", 500

    headers = {"Content-Type": "application/json"}
    payload = {
        "Username": USERNAME,
        "Secret": SECRET,
        "ImageData": True,
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

        csv_header = list(get_csv_row({}).keys())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="", encoding="utf-8") as tmp_file:
            writer = csv.DictWriter(tmp_file, fieldnames=csv_header)
            writer.writeheader()
            for item in data:
                writer.writerow(get_csv_row(item))
            local_file_path = tmp_file.name

        upload_to_gcs(local_file_path, bucket_name="nology-sync-bucket", destination_blob_name="nology_test.csv")

        return jsonify({"message": "CSV synced to GCS", "records": len(data)})

    except Exception as e:
        return f"Live API request failed: {str(e)}", 500

@json_to_csv_bp.route("/")
def home():
    return "Use /products (live sync), /dummy (test), or /download (local CSV)."
