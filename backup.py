import subprocess
import datetime
import os
import shutil

def backup_database():
    """Backup MySQL database"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    
    # Create backups directory if not exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_file = os.path.join(backup_dir, f"hotel_management_{timestamp}.sql")
    
    # MySQL dump command
    cmd = f'mysqldump -u root hotel_management > "{backup_file}"'
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Database backup created: {backup_file}")
        
        # Keep only last 10 backups
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.sql')])
        while len(backups) > 10:
            os.remove(os.path.join(backup_dir, backups[0]))
            backups.pop(0)
        
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def backup_code():
    """Backup source code"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    code_backup = os.path.join(backup_dir, f"code_backup_{timestamp}.zip")
    
    # Folders to backup
    folders = ['flask_app', 'java_services']
    
    try:
        shutil.make_archive(code_backup.replace('.zip', ''), 'zip', '.', 
                           lambda path: any(folder in path for folder in folders))
        print(f"✅ Code backup created: {code_backup}")
        return True
    except Exception as e:
        print(f"❌ Code backup failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting backup process...")
    backup_database()
    backup_code()
    print("Backup complete!")