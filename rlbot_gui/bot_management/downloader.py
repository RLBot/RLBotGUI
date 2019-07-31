import os
import tempfile
import urllib
import zipfile
from pathlib import Path
import shutil

from distutils.dir_util import copy_tree



def download_and_extract_zip(download_url: str, local_folder_path: Path, clobber: bool = False):
    """
    :param clobber: If true, we will delete anything found in local_folder_path.
    :return:
    """

    with tempfile.TemporaryDirectory() as tmpdirname:
        downloadedZip = os.path.join(tmpdirname, 'downloaded.zip')
        urllib.request.urlretrieve(download_url, downloadedZip)

        if clobber and os.path.exists(local_folder_path):
            shutil.rmtree(local_folder_path)

        with zipfile.ZipFile(downloadedZip, 'r') as zip_ref:
            zip_ref.extractall(local_folder_path)


def download_gitlfs(repo_url: str, checkout_folder: Path, branch_name: str):
    print('Starting download of a git repo... this might take a while.')

    # Download the most of the files eg. https://github.com/RLBot/RLBotPack/archive/master.zip
    download_and_extract_zip(
        download_url=repo_url + '/archive/' + branch_name + '.zip',
        local_folder_path=checkout_folder, clobber=True)

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

def download_botfs(repo_url: str, checkout_folder: Path, branch_name: str, bot_path: str, bot_dir_name: str):
    print('Starting download of a git repo... this might take a while.')

    shutil.rmtree(checkout_folder, ignore_errors=True)

    # Download the most of the files eg. https://github.com/RLBot/RLBotPack/archive/master.zip
    download_and_extract_zip(
        download_url=repo_url + '/archive/' + branch_name + '.zip',
        local_folder_path=checkout_folder, clobber=True)

    repo_extraction_name = '/' + repo_url.split('/')[-1] + '-' + branch_name + '/'

    shutil.copytree(checkout_folder + repo_extraction_name + '/' + bot_dir_name, bot_path + '/' + bot_dir_name)

    print('Done downloading git repo.')
