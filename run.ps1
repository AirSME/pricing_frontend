$env:PYTHONPATH = "backend"
$env:FLASK_APP = "app:create_app"
$env:FLASK_ENV = "development"
flask run --port=5050
