from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleDriveService:
    def __init__(self, credentials_file, folder_id=None):
        """
        Initialize Google Drive service
        
        Args:
            credentials_file: Absolute path to service account JSON credentials file
            folder_id: Google Drive folder ID where files will be uploaded (optional)
        """
        self.credentials_file = credentials_file
        self.folder_id = folder_id
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate and return Google Drive service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            service = build('drive', 'v3', credentials=credentials)
            logger.info("Successfully authenticated with Google Drive")
            return service
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
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
