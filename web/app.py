from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Visit /products to view Nology product data."

@app.route("/products")
def get_products():

    url = "http://154.72.246.201/NologyDataFeed/api/Products/View"

    headers = {
        "Accept": "application/json"
    }

    payload = {
        "Username": "INN008",
        "Secret": "1O_Wi2SY7z",
        "ImageData": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}", 500


if __name__ == "__main__":
    app.run()