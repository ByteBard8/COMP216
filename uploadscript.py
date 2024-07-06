# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 17:24:30 2024

@author: Jaekyeong
"""

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

finally:
    # Close the SSH connection
    ssh_client.close()
    print("Connection closed.")
