"""
Created on Sat Jul  6 17:24:30 2024

Adilet
Diego
Jaekyeong
Sandeep
"""

#Exercise - Download files via FTP:
#Write a Python script to use FTP to download files to a local drive. 
# The remote ftp site is ftp.gnu.org and develop an efficient manner to
#  find and retrieve all .webm files from the Video directory.
from ftplib import FTP
import os
from concurrent.futures import ThreadPoolExecutor


#source server
FTP_SERVER = "ftp.gnu.org"

#directory location
FTP_DIRECTORY = "/video"

#local directory to download
LOCAL_DIRECTORY = "./Downloads"  

# Create local directory if it doesn't exist
if not os.path.exists(LOCAL_DIRECTORY):
    os.makedirs(LOCAL_DIRECTORY)


def get_download_list(extension):
     # Connect to the FTP server
    ftp = FTP(FTP_SERVER)
    ftp.login()
    # Change to the target directory
    ftp.cwd(FTP_DIRECTORY)
    # list all files in pwd
    files = ftp.nlst()
    # get list of webm extensions
    webm_files = [file for file in files if file.endswith(extension)]
    #close
    ftp.quit()
    #return filtered list
    print(f"List to download:")
    print(webm_files)
    return webm_files


def download_file(file):
    try:
        # Connect to the FTP server
        ftp = FTP(FTP_SERVER)
        ftp.login()
        # Change to the target directory
        ftp.cwd(FTP_DIRECTORY)
        #define a local path
        local_file_path = os.path.join(LOCAL_DIRECTORY, file)
        print(f"Downloading file:\t{file}")
        with open(local_file_path, 'wb') as local_file:
            ftp.retrbinary(f"RETR {file}", local_file.write)
            print(f"Downloaded: {local_file_path}")
    except Exception as e:
        print(f"Error downloading {file}: {e}")


def download_webm_files():
    #get a list of files to download   
    files = get_download_list('webm')
    # start for loop
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(download_file, files)

#start downloading
download_webm_files()



#Write a Python script to use SSH and SFTP to create a Document directory 
# and upload a sample text file to the AWS Lightsail VM. 
# Note: The implementation requires the Paramiko library and 
# SSH Key Pair configuration between the AWS Lightsail VM 
# and the local machine
import paramiko

# Configuration details
hostname = '44.220.178.61'  
username = 'ec2-user'  
ssh_key_path = 'LightsailDefaultKey-us-east-1.pem'  
local_file_path = 'assignment.txt'  
remote_directory = '/home/ec2-user/Document'  
remote_file_path = f'{remote_directory}/assignment.txt'

# Initialize SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the Lightsail instance
try:
    ssh_client.connect(hostname=hostname, username=username, key_filename=ssh_key_path)
    print("Connected to the Lightsail instance.")

    # Create the remote directory
    stdin, stdout, stderr = ssh_client.exec_command(f'mkdir -p {remote_directory}')
    stdout.channel.recv_exit_status()  # Wait for command to complete
    print(f"Directory {remote_directory} created or already exists.")

    # Initialize SFTP client
    sftp_client = ssh_client.open_sftp()
    
    # Upload the local file to the remote directory
    sftp_client.put(local_file_path, remote_file_path)
    print(f"File {local_file_path} uploaded to {remote_file_path}.")

    # Close the SFTP client
    sftp_client.close()
except Exception as e:
    print(f"Error : {e}")
finally:
    # Close the SSH connection
    ssh_client.close()
    print("Connection closed.")