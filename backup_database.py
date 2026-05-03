import subprocess
import datetime
import os

def backup_database():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_hotel_management_{timestamp}.sql"
    
    # MySQL dump command (adjust paths as needed)
    cmd = f'mysqldump -u root hotel_management > {backup_file}'
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Backup created: {backup_file}")
        
        # Optional: Keep only last 10 backups
        backups = sorted([f for f in os.listdir('.') if f.startswith('backup_hotel_management_')])
        while len(backups) > 10:
            os.remove(backups[0])
            backups.pop(0)
    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    backup_database()