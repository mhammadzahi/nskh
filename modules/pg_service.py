import subprocess, psycopg2, os, logging
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLBackup:
    def __init__(self, host='localhost', port=5432, user='postgres', password='', dump_dir=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dump_dir = dump_dir or os.getenv('DUMP_DIR', '/tmp/pg_backups')
        
        # Create dump directory if it doesn't exist
        os.makedirs(self.dump_dir, exist_ok=True)
    
    def get_all_databases(self):
        """Retrieve all databases from PostgreSQL server"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database='postgres'
            )
            cursor = conn.cursor()
            
            # Get all databases except template databases
            cursor.execute("""
                SELECT datname FROM pg_database 
                WHERE datistemplate = false 
                AND datname NOT IN ('postgres')
            """)
            
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            logger.info(f"Found {len(databases)} databases: {databases}")
            return databases
            
        except Exception as e:
            logger.error(f"Error getting databases: {e}")
            return []
    
    def dump_database(self, database_name):
        """Create a dump file for a specific database"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_filename = f"{database_name}_{timestamp}.sql"
        dump_filepath = os.path.join(self.dump_dir, dump_filename)
        
        try:
            # Set environment variable for password
            env = os.environ.copy()
            if self.password:
                env['PGPASSWORD'] = self.password
            
            # Use absolute path for pg_dump
            pg_dump_cmd = [
                '/usr/bin/pg_dump',  # Absolute path
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.user,
                '-F', 'p',  # Plain text format
                '-f', dump_filepath,
                database_name
            ]
            
            logger.info(f"Creating dump for database: {database_name}")
            result = subprocess.run(
                pg_dump_cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully created dump: {dump_filepath}")
                return dump_filepath
            else:
                logger.error(f"Error dumping {database_name}: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Exception while dumping {database_name}: {e}")
            return None
    
    def dump_all_databases(self):
        """Dump all databases and return list of dump file paths"""
        databases = self.get_all_databases()
        dump_files = []
        
        for db in databases:
            dump_file = self.dump_database(db)
            if dump_file:
                dump_files.append(dump_file)
        
        return dump_files
