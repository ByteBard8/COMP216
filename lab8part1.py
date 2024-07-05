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


if __name__ == "__main__":
    download_webm_files()