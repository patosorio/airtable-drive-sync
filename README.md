# Airtable to Google Contacts Sync

## Overview
This project is a Flask-based API that synchronizes contacts between Airtable and Google Contacts. It listens for webhook events from Airtable and updates Google Contacts accordingly.

## Features
- **Create Contacts**: Adds a new contact to Google Contacts when a new record is created in Airtable.
- **Update Contacts**: Updates an existing Google Contact when a record is modified in Airtable.
- **Delete Contacts**: Removes a contact from Google Contacts when a record is deleted in Airtable.
- **OAuth Authentication**: Uses Google OAuth2 authentication to interact with Google Contacts API.

## Prerequisites
Before running this project, ensure you have the following:
- Python 3 installed
- A Google Cloud project with People API enabled
- OAuth 2.0 credentials (`oauth_client.json`)
- Airtable API key (if needed)

## Installation
### 1. Clone the Repository
```sh
git clone https://github.com/patosorio/airtable-drive-sync.git
cd airtable-drive-sync
```

### 2. Create a Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure OAuth Credentials
Place your `oauth_client.json` file in the root directory.

### 5. Run the Flask Application
```sh
python app.py
```

The server will start at `http://127.0.0.1:8080`.

## API Endpoints
### 1. Home Endpoint
```http
GET /
```
Response:
```
Flask API is running!
```

### 2. Airtable Webhook Endpoint
```http
POST /webhook
```
#### Expected Payload (Example for Creating a Contact):
```json
{
  "action": "create",
  "record": {
    "fields": {
      "FullName": "John Doe",
      "Email": "johndoe@example.com",
      "Mobile": "+123456789",
      "City": "New York",
      "Country": "USA",
      "HR_ID": "12345",
      "LastSynced": "2024-02-26",
      "NeedsSync": true
    }
  }
}
```

## Airtable Integration
To enable Airtable to send webhook events to this API, you must:
1. **Write JavaScript code** within Airtable to create webhooks.
2. **Use Airtable Automations** to trigger webhooks when records are created, updated, or deleted.
3. **Point the webhook URL** to the `/webhook` endpoint of this Flask API.

## Authentication
Google OAuth2 is used to authenticate and obtain access to Google Contacts. The first time you run the app, a browser window will open to authenticate your Google account.

## Error Handling
The API includes error handling for failed Google API requests, missing fields, and authentication failures.

## License
This project is licensed under the MIT License.

## Author
[patosorio](https://github.com/patosorio/)

