import os
import shutil
import hashlib
import time
import argparse
import logging

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except FileNotFoundError:
        return None
    return hash_md5.hexdigest()

def sync_folders(source_folder, replica_folder):
    
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)
        
    for root, _, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        replica_path = os.path.join(replica_folder, relative_path)
        
        if not os.path.exists(replica_path):
            os.makedirs(replica_path)
            logging.info(f"Created directory: {replica_path}")
        
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_path, file)
            
            if not os.path.exists(replica_file) or calculate_md5(source_file) != calculate_md5(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Copied/Updated file: {source_file} -> {replica_file}")
    
    for root, _, files in os.walk(replica_folder):
        relative_path =  os.path.relpath(root, replica_folder)
        source_root =  os.path.join(source_folder, relative_path)
        
        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)
            
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed file: {replica_file}")
                
def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format = '%(asctime)s - %(levelname)s -%(message)s',#
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    ) 
    
def main():
    
    parser = argparse.ArgumentParser(description="One-way folder synchronization script.")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("interval", type=int, help="Synchronization delay in seconds")
    parser.add_argument("log_file", help="Path to the log File")
    args = parser.parse_args()
    
    setup_logging(args.log_file)
    
    logging.info("Starting folder synchronization...")
    while True:
        try:
            sync_folders(args.source_folder, args.replica_folder)
            logging.info(f"Synchronization completed. Waiting {args.interval} seconds for the next run.")
            time.sleep(args.interval)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            break
if __name__ == '__main__':
    main()