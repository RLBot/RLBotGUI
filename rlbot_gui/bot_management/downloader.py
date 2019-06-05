from pathlib import Path
import urllib
import zipfile


def download_and_extract_zip(download_url: str, local_zip_path: Path, local_folder_path: Path):
    urllib.request.urlretrieve(download_url, local_zip_path)

    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(local_folder_path)


def download_gitlfs(repo_url: str, checkout_folder: Path, branch_name: str):
    print('Starting download of a git repo... this might take a while.')
    
    # Download the most of the files eg. https://github.com/RLBot/RLBotPack/archive/master.zip
    download_and_extract_zip(
        download_url=repo_url + '/archive/' + branch_name + '.zip',
        local_zip_path='github-bot-pack.zip',
        local_folder_path=checkout_folder)

    repo_extraction_name = '/' + repo_url.split('/')[-1] + '-' + branch_name + '/'

    file = open(checkout_folder + repo_extraction_name + '.gitattributes')
    for line in file:
        if line.split(' ')[1].endswith('=lfs'):
            # Download gitlfs file
            urllib.request.urlretrieve(
                repo_url + '/raw/' + branch_name + '/' + line.split(' ')[0],
                checkout_folder + repo_extraction_name + line.split(' ')[0])
    file.close()

    print('Done downloading git repo.')
