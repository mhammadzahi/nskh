from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleDriveService:
    def __init__(self, credentials_file, folder_id=None, auto_create_timestamped_folder=True):
        """
        Initialize Google Drive service
        
        Args:
            credentials_file: Absolute path to OAuth2 token JSON file (creds_token.json)
            folder_id: Google Drive folder ID where files will be uploaded (optional, parent folder)
            auto_create_timestamped_folder: If True, creates a timestamped subfolder for this backup session
        """
        self.credentials_file = credentials_file
        self.parent_folder_id = folder_id
        self.folder_id = None
        self.service = self._authenticate()
        
        # Create timestamped folder if enabled
        if auto_create_timestamped_folder:
            folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.folder_id = self.create_folder(folder_name, parent_folder_id=self.parent_folder_id)
        else:
            self.folder_id = folder_id
    
    def _authenticate(self):
        """Authenticate and return Google Drive service using OAuth2"""
        try:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(
                    f"OAuth2 token file not found: {self.credentials_file}\n"
                    "Please run 'python modules/generate_oauth_token.py' to generate it."
                )
            
            # Load OAuth2 credentials from token file
            credentials = Credentials.from_authorized_user_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                logger.info("Refreshing expired OAuth2 token...")
                credentials.refresh(Request())
                
                # Save the refreshed token
                with open(self.credentials_file, 'w') as token:
                    token.write(credentials.to_json())
            
            service = build('drive', 'v3', credentials=credentials)
            logger.info("Successfully authenticated with Google Drive using OAuth2")
            return service
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: Parent folder ID (optional, if None creates in root)
        
        Returns:
            Folder ID if successful, None otherwise
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            # If parent folder is specified, create folder inside it
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Created folder '{folder_name}' (ID: {folder_id})")
            logger.info(f"View at: {folder.get('webViewLink')}")
            
            return folder_id
            
        except Exception as e:
            logger.error(f"Error creating folder '{folder_name}': {e}")
            return None
    
    def upload_file(self, file_path):
        """
        Upload a file to Google Drive
        
        Args:
            file_path: Absolute path to the file to upload
        
        Returns:
            File ID if successful, None otherwise
        """
        try:
            file_name = os.path.basename(file_path)
            
            file_metadata = {
                'name': file_name
            }
            
            # If folder_id is specified, upload to that folder
            if self.folder_id:
                file_metadata['parents'] = [self.folder_id]
            
            media = MediaFileUpload(
                file_path,
                mimetype='application/sql',
                resumable=True
            )
            
            logger.info(f"Uploading {file_name} to Google Drive...")
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            logger.info(f"Successfully uploaded {file_name} (ID: {file.get('id')})")
            logger.info(f"View at: {file.get('webViewLink')}")
            
            return file.get('id')
            
        except Exception as e:
            logger.error(f"Error uploading {file_path}: {e}")
            return None
    
    def upload_multiple_files(self, file_paths):
        """
        Upload multiple files to Google Drive
        
        Args:
            file_paths: List of absolute file paths
        
        Returns:
            Dictionary mapping file paths to their Google Drive file IDs
        """
        results = {}
        for file_path in file_paths:
            if os.path.exists(file_path):
                file_id = self.upload_file(file_path)
                results[file_path] = file_id
            else:
                logger.warning(f"File not found: {file_path}")
                results[file_path] = None
        
        return results
