API Key System with FastAPI and MongoDB

This is an example implementation of an API key system using FastAPI and MongoDB. The system allows you to generate and manage API keys, and includes a middleware function to validate API keys in incoming requests.

Requirements

To run this application, you'll need the following:

Python 3.7 or higher
fastapi 0.70.0 or higher
pymongo 4.0.1 or higher
uvicorn 0.15.0 or higher
You can install these requirements by running pip install -r requirements.txt in the project directory.

Getting Started

Clone this repository to your local machine.
Install the required packages by running pip install -r requirements.txt.
Start the application by running uvicorn main:app --reload.
You can access the application at http://localhost:8000.
API Key Management

You can create new API keys by sending a POST request to the /api-keys endpoint with a JSON payload containing an owner field:

json
Copy code
{
    "owner": "John Doe"
}
The response will contain the new API key and secret key:

json
Copy code
{
    "api_key": "6QkS5G5Z5LpU6K9fY95O",
    "secret_key": "Uvdw6U1Q6S1O5z5G5f9K"
}
To use an API key in a request, include it in the x-api-key header:

vbnet
Copy code
GET /endpoint HTTP/1.1
Host: localhost:8000
x-api-key: 6QkS5G5Z5LpU6K9fY95O
License

This project is licensed under the MIT License. See the LICENSE file for details.

Contributing

Contributions to this project are welcome. If you find any bugs or have any feature requests, please create an issue in the project repository. If you'd like to contribute code, please fork the repository and submit a pull request with your changes.