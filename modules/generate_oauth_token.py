#!/usr/bin/env python3
"""
Script to generate OAuth2 token (creds_token.json) for Google Drive API
This script should be run once to authorize the application and generate the token file.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define the scopes required for Google Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to your OAuth2 credentials (downloaded from Google Cloud Console)
# You need to download this from: https://console.cloud.google.com/apis/credentials
CREDENTIALS_FILE = 'credentials.json'

# Output token file
TOKEN_FILE = 'creds_token.json'


def generate_token():
    """Generate OAuth2 token for Google Drive API"""
    
    creds = None
    
    # Check if token file already exists
    if os.path.exists(TOKEN_FILE):
        print(f"Token file '{TOKEN_FILE}' already exists.")
        response = input("Do you want to regenerate it? (y/n): ")
        if response.lower() != 'y':
            print("Exiting without changes.")
            return
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"\n❌ Error: '{CREDENTIALS_FILE}' not found!")
                print("\n📋 To create this file:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create or select a project")
                print("3. Enable Google Drive API")
                print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'")
                print("5. Choose 'Desktop app' as application type")
                print("6. Download the JSON file and save it as 'credentials.json'")
                print(f"7. Place it in: {os.path.abspath('.')}")
                return
            
            print("\n🔐 Starting OAuth2 authorization flow...")
            print("A browser window will open. Please authorize the application.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Successfully generated '{TOKEN_FILE}'")
        print(f"📁 Location: {os.path.abspath(TOKEN_FILE)}")
        print("\n✨ You can now use this token file with your Google Drive service!")
    else:
        print(f"✅ Token is still valid: {TOKEN_FILE}")


if __name__ == '__main__':
    print("=" * 60)
    print("Google Drive OAuth2 Token Generator")
    print("=" * 60)
    
    try:
        generate_token()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("- credentials.json file is valid")
        print("- Google Drive API is enabled in your project")
        print("- OAuth consent screen is configured")
