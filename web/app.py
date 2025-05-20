from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return "Visit /products to view Nology product data."

@app.route("/products")
def get_products():
    
    username = os.getenv("NOLOGY_USERNAME")
    secret = os.getenv("NOLOGY_SECRET")

    url = "http://154.72.246.201/NologyDataFeed/api/Products/View"

    session = requests.Session()
    request = requests.Request(
        method='GET',
        url=url,
        json={
            "Username": username,
            "Secret": secret,
            "ImageData": False
        }
    )
    prepped = session.prepare_request(request)

    try:
        response = session.send(prepped)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)  
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run()