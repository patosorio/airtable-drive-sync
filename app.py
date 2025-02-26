from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from google.auth.transport.requests import Request
import pickle

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/contacts"]

TOKEN_FILE = "token.pickle"

def get_credentials():
    credentials = None

    # Load saved credentials if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    # If credentials are invalid or expired, re-authenticate
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("oauth_client.json", SCOPES)
            credentials = flow.run_local_server(port=8080)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)

    return credentials

credentials = get_credentials()
service = build("people", "v1", credentials=credentials)


def create_google_contact(data):
    """
    Create a new contact in Google Contacts
    """

    contact = {}

    if data.get("name"):
        contact["names"] = [{"givenName": data["name"]}]
    if data.get("email"):
        contact["emailAddresses"] = [{"value": data["email"]}]
    if data.get("phone"):
        contact["phoneNumbers"] = [{"value": data["phone"]}]
    if data.get("city") or data.get("country"):
        contact["addresses"] = [{"city": data.get("city", ""), "country": data.get("country", "")}]

    if not contact:
        print("Error: No valid fields provided. Contact cannot be created.")
        return None  # Prevent sending an invalid request

    # Store HR_ID and other metadata
    user_defined_fields = []
    if data.get("hr_id"):
        user_defined_fields.append({"key": "HR_ID", "value": data["hr_id"]})
    if data.get("last_synced"):
        user_defined_fields.append({"key": "LastSynced", "value": str(data["last_synced"])})
    if data.get("needs_sync") is not None:
        user_defined_fields.append({"key": "NeedsSync", "value": str(data["needs_sync"])})

    if user_defined_fields:
        contact["userDefined"] = user_defined_fields

    print("Sending contact data to Google API:")
    print(contact)

    try:
        response = service.people().createContact(body=contact).execute()
        contact_id = response.get("resourceName")  # Google-generated Contact ID
        print(f"Contact created with HR_ID: {data.get('hr_id')}, Google Contact ID: {contact_id}")
        return contact_id

    except Exception as e:
        print(f"Error creating contact: {e}")
        return None


def find_goohle_contact_by_hrid(hr_id):
    """
    Find a Google Contact by HR_ID (stored in userDefined fields).
    """
    try:
        results = service.people().connections().list(
            resourceName="people/me",
            personFields="names,emailAddresses,phoneNumbers,userDefined"
        ).execute()

        for person in results.get("connections", []):
            for field in person.get("userDefined", []):
                if field["key"] == "HR_ID" and field["value"] == hr_id:
                    return person["resourceName"]

        return None
    except Exception as e:
        print(f"Error finding contact by HR_ID: {e}")
        return None
    

def update_google_contact(hr_id, data):
    """
    Update a contact using HR_ID instead of Google Contact ID.
    """

    contact_id = find_goohle_contact_by_hrid(hr_id)
    if not contact_id:
        print(f"⚠️ Contact with HR_ID {hr_id} not found in Google Contacts.")
        return None

    contact = {
        "names": [{"givenName": data.get('name')}],
        "emailAddresses": [{"value": data.get('email')}],
        "phoneNumbers": [{"value": data.get('phone')}],
        "addresses": [{
            "city": data.get("city", ""),
            "country": data.get("country", "")
        }],
        "userDefined": [
            {"key": "HR_ID", "value": data.get("hr_id", "")},
            {"key": "LastSynced", "value": data.get("last_synced", "")},
            {"key": "NeedsSync", "value": str(data.get("needs_sync", ""))}
        ]
    }

    try:
        service.people().updateContact(
            resourceName=contact_id, 
            body=contact, 
            updatePersonFields="names,emailAddresses,phoneNumbers,addresses,userDefined"
        ).execute()
        print(f"Contact updated successfully: {contact_id}")
        return contact_id

    except Exception as e:
        print(f"Error updating contact: {e}")
        return None


def delete_google_contact(contact_id):
    """
    Delete a contact from Google Contacts
    """
    service.people().deleteContact(resourceName=contact_id).execute()

@app.route("/", methods=["GET"])
def home():
    return "Flask API is running!", 200

# Webhook Endpoint for Airtable
@app.route("/webhook", methods=["POST"])
def airtable_webhook():
    payload = request.json
    action = payload.get('action')
    record = payload.get('record', {})

    data = {
        "name": record.get("fields", {}).get("FullName"),  # Airtable Full Name
        "email": record.get("fields", {}).get("Email"),  # Email Address
        "phone": record.get("fields", {}).get("Mobile"),  # Mobile Number
        "city": record.get("fields", {}).get("City"),  # City
        "country": record.get("fields", {}).get("Country"),  # Country
        "hr_id": record.get("fields", {}).get("HR_ID"),  # HR ID
        "last_synced": record.get("fields", {}).get("LastSynced"),  # Last Synced Date
        "needs_sync": record.get("fields", {}).get("NeedsSync"),  # Boolean/Flag for Sync Status
    }


    try:
        if action == "create":
            contact_id = create_google_contact(data)
            print(f"Contact created in Google Contacts with ID: {contact_id}")

        elif action == "update":
            contact_id = update_google_contact(data["hr_id"], data)
            if contact_id:
                print(f"Contact updated in Google Contacts: {contact_id}")
            else:
                print(f"⚠️ Contact not found for HR_ID: {data['hr_id']}")

        elif action == "delete":
            delete_google_contact(data['contact_id'])
            print(f"Contact deleted in Google Contacts: {data['contact_id']}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    print("Starting Flask API on http://127.0.0.1:8080...")
    app.run(host="0.0.0.0", port=8080, debug=True)
