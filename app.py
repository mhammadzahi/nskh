#!/usr/bin/env python3
"""
PostgreSQL Database Backup to Google Drive
Designed to run as a cron job with absolute paths
"""

import os, import sys, logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
# Use absolute path to .env file for cron compatibility
env_path = '/Users/owner/Documents/nskh/.env'
load_dotenv(dotenv_path=env_path)

# Add the modules directory to path using absolute path
sys.path.insert(0, '/Users/owner/Documents/nskh/modules')

from pg_service import PostgreSQLBackup
from drive_service import GoogleDriveService

# Configure logging
log_dir = os.getenv('LOG_DIR', '/var/log/pg_backup')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'backup_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 50)
    logger.info("Starting PostgreSQL backup process")
    logger.info("=" * 50)

    # Load configuration from environment variables
    PG_HOST = os.getenv('PG_HOST', 'localhost')
    PG_PORT = int(os.getenv('PG_PORT', 5432))
    PG_USER = os.getenv('PG_USER', 'postgres')
    PG_PASSWORD = os.getenv('PG_PASSWORD', '')
    
    # Google Drive credentials file (absolute path)
    CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
    
    # Google Drive folder ID (optional - leave empty to upload to root)
    DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID') or None
    
    try:
        # Step 1: Initialize PostgreSQL backup
        logger.info("Initializing PostgreSQL backup service...")
        pg_backup = PostgreSQLBackup(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASSWORD)
        
        # Step 2: Dump all databases
        logger.info("Dumping all databases...")
        dump_files = pg_backup.dump_all_databases()
        
        if not dump_files:
            logger.warning("No dump files were created")
            return 1
        
        logger.info(f"Created {len(dump_files)} dump file(s)")
        
        # Step 3: Initialize Google Drive service
        logger.info("Initializing Google Drive service...")
        drive_service = GoogleDriveService(credentials_file=CREDENTIALS_FILE, folder_id=DRIVE_FOLDER_ID)
        
        # Step 4: Upload all dump files to Google Drive
        logger.info("Uploading dump files to Google Drive...")
        results = drive_service.upload_multiple_files(dump_files)
        
        # Step 5: Report results
        successful_uploads = sum(1 for file_id in results.values() if file_id)
        logger.info(f"Successfully uploaded {successful_uploads}/{len(dump_files)} files")
        
        # Optional: Clean up local dump files after successful upload
        for file_path, file_id in results.items():
            if file_id:
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up local file: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not remove {file_path}: {e}")
        
        logger.info("=" * 50)
        logger.info("Backup process completed successfully")
        logger.info("=" * 50)
        return 0
        
    except Exception as e:
        logger.error(f"Backup process failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
