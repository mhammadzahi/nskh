# PostgreSQL Backup to Google Drive

Automated backup system that dumps all PostgreSQL databases and uploads them to Google Drive. Designed to run as a Linux cron job with absolute paths.

## Features

- Automatically discovers all databases on PostgreSQL server
- Creates timestamped .sql dump files for each database
- Uploads dumps to Google Drive
- Full logging with rotation support
- Cleanup of local files after successful upload

## Setup

### 1. Install Dependencies

```bash
/usr/bin/python3 -m pip install -r /Users/owner/Documents/nskh/requirements.txt
```

### 2. Configure PostgreSQL

Ensure PostgreSQL is running and you have:
- Database username and password
- Permission to access all databases you want to back up

### 3. Set up Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Create Service Account
   - Grant it appropriate permissions
   - Create and download JSON key file
5. Save the credentials file as `credentials.json`
6. (Optional) Share a Google Drive folder with the service account email

### 4. Configure the Application

Copy the example environment file and edit it:

```bash
cp /Users/owner/Documents/nskh/.env.example /Users/owner/Documents/nskh/.env
```

Edit `.env` and update these values:

```env
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password
CREDENTIALS_FILE=/absolute/path/to/credentials.json
DRIVE_FOLDER_ID=your_folder_id_or_leave_empty
```

**Important**: All paths must be absolute for cron job compatibility.

### 5. Test the Script

```bash
/usr/bin/python3 /Users/owner/Documents/nskh/app.py
```

### 6. Set up Cron Job

Edit crontab:
```bash
crontab -e
```

Add one of these entries:

**Daily backup at 2:00 AM:**
```cron
0 2 * * * /usr/bin/python3 /Users/owner/Documents/nskh/app.py >> /var/log/pg_backup/cron.log 2>&1
```

**Every 6 hours:**
```cron
0 */6 * * * /usr/bin/python3 /Users/owner/Documents/nskh/app.py >> /var/log/pg_backup/cron.log 2>&1
```

**Weekly backup (Sunday at 3:00 AM):**
```cron
0 3 * * 0 /usr/bin/python3 /Users/owner/Documents/nskh/app.py >> /var/log/pg_backup/cron.log 2>&1
```

## File Naming Convention

Backup files are named: `{database_name}_{timestamp}.sql`

Example: `myapp_db_20260115_020000.sql`

## Logs

Logs are stored in `/var/log/pg_backup/` with daily rotation.

## Directory Structure

```
nskh/
├── app.py                  # Main application
├── modules/
│   ├── pg-server.py       # PostgreSQL backup logic
│   └── drive-service.py   # Google Drive upload logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (not in git)
├── .env.example           # Environment configuration template
├── credentials.json        # Google service account credentials (not in git)
└── README.md              # This file
```

## Troubleshooting

### PostgreSQL Connection Issues

- Verify PostgreSQL is running: `systemctl status postgresql`
- Check pg_hba.conf for authentication settings
- Ensure user has proper permissions

### Google Drive Upload Issues

- Verify credentials.json is valid
- Check service account has necessary permissions
- If using folder ID, ensure folder is shared with service account email

### Cron Job Not Running

- Check cron service: `systemctl status cron`
- Verify absolute paths in crontab
- Check cron logs: `grep CRON /var/log/syslog`
- Ensure script has execute permissions: `chmod +x /Users/owner/Documents/nskh/app.py`

### Permission Issues

Create log directory with proper permissions:
```bash
sudo mkdir -p /var/log/pg_backup
sudo chown $USER:$USER /var/log/pg_backup
```

## Security Notes

- Keep `credentials.json` secure and never commit to git
- Consider encrypting sensitive configuration data
- Regularly rotate service account keys
- Monitor Google Drive storage usage
- Consider implementing backup retention policies
