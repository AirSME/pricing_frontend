from flask import Flask, jsonify, send_file
import requests
import json
import csv
import os

app = Flask(__name__)

API_URL = "https://erp.nology.co.za/NologyDataFeed/api/Products/View"
USERNAME = os.getenv("NOLOGY_USERNAME")
SECRET = os.getenv("NOLOGY_SECRET")

@app.route("/")
def home():
    return "Use /products (live), /dummy (local), or /download (CSV)."

# 🔹 LIVE PRODUCT FEED (uses environment variables)
@app.route("/products")
def get_products():
    if not USERNAME or not SECRET:
        return "Missing API credentials. Please set NOLOGY_USERNAME and NOLOGY_SECRET.", 500

    params = {
        "Username": USERNAME,
        "Secret": SECRET,
        "ImageData": "false",
        "ReturnType": "JSON"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return f"Live API request failed: {str(e)}", 500

# 🔹 DUMMY DATA ONLY (offline testing)
@app.route("/dummy")
def get_dummy_data():
    try:
        with open("nology_raw.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return "nology_raw.json not found. Add your dummy file to the root directory.", 404
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
