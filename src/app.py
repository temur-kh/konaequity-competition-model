from flask import Flask

# TODO: create API for the application and route requests to specific methods
# TODO: integrate Hubspot API

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
