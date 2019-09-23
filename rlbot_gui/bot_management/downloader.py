import os
import tempfile
import urllib.request
import zipfile
import json
import eel
import time
from pathlib import Path
from shutil import rmtree


def download_and_extract_zip(download_url: str, local_folder_path: Path,
                             clobber: bool = False, progress_callback: callable = None,
                             unzip_callback: callable = None):
    """
    :param clobber: If true, we will delete anything found in local_folder_path.
    :return:
    """

    with tempfile.TemporaryDirectory() as tmpdirname:
        downloadedZip = os.path.join(tmpdirname, 'downloaded.zip')
        urllib.request.urlretrieve(download_url, downloadedZip, progress_callback)

        if clobber and os.path.exists(local_folder_path):
            rmtree(local_folder_path)

        if unzip_callback:
            unzip_callback()

        with zipfile.ZipFile(downloadedZip, 'r') as zip_ref:
            zip_ref.extractall(local_folder_path)


def get_json_from_url(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read())


def get_repo_size(repo_full_name):
    """
    Call GitHub API to get an estimate size of a GitHub repository.
    :param repo_full_name: Full name of a repository. Example: 'RLBot/RLBotPack'
    :return: Size of the repository in bytes, or 0 if the API call fails.
    """
    try:
        data = get_json_from_url('https://api.github.com/repos/' + repo_full_name)
        return int(data["size"]) * 1000
    except:
        return 0



class BotpackDownloader:
    """
    Downloads the botpack while updating the progress bar and status text.
    """

    PROGRESSBAR_UPDATE_INTERVAL = 0.1 # How often to update the progress bar (seconds)
    ZIP_PORTION = 0.6 # How much of total progress should the zip file take

    def __init__(self):
        self.status = ''
        self.current_progress = 0
        self.total_progress = 0

        self.estimated_zip_size = 0
        self.current_file_bytes_downloaded = 0
        self.lfs_file_count = 0
        self.lfs_files_completed = 0
        self.one_lfs_file_portion = 0
        self.last_progressbar_update_time = 0


    def update_progressbar_and_status(self):
        # it's not necessary to update on every callback, so update
        # only when some amount of time has passed
        now = time.time()
        if now > self.last_progressbar_update_time + self.PROGRESSBAR_UPDATE_INTERVAL:
            self.last_progressbar_update_time = now

            total_progress_percent = self.total_progress * 100
            current_progress_percent = int(self.current_progress * 100)
            status = f'{self.status} ({current_progress_percent}%)'

            eel.updateDownloadProgress(total_progress_percent, status)


    def zip_download_callback(self, block_count, block_size, _):
        self.current_file_bytes_downloaded += block_size
        self.current_progress = min(self.current_file_bytes_downloaded / self.estimated_zip_size, 1.0)
        self.total_progress = self.current_progress * self.ZIP_PORTION
        self.update_progressbar_and_status()


    def unzip_callback(self):
        eel.updateDownloadProgress(int(self.ZIP_PORTION * 100), 'Extracting ZIP file')


    def lfs_download_callback(self, block_count, block_size, total_size):
        self.current_file_bytes_downloaded += block_size
        self.current_progress = self.current_file_bytes_downloaded / total_size
        prev_files_progress = self.ZIP_PORTION + self.one_lfs_file_portion * self.lfs_files_completed
        self.total_progress = prev_files_progress + self.current_progress * self.one_lfs_file_portion
        self.update_progressbar_and_status()


    def download(self, repo_owner: str, repo_name: str, branch_name: str, checkout_folder: Path):
        repo_full_name = repo_owner + '/' + repo_name
        repo_url = 'https://github.com/' + repo_full_name
        repo_extraction_name = f'/{repo_name}-{branch_name}/'

        self.status = f'Downloading {repo_full_name}-{branch_name}'
        print(self.status)
        self.progress = 0

        # Unfortunately we can't know the size of the zip file before downloading it,
        # so we have to get the size from the GitHub API.
        self.estimated_zip_size = get_repo_size(repo_full_name) * 0.9

        # If we fail to get the repo size, set it to a fallback value,
        # so the progress bar will show atleast some progress.
        # Let's assume the zip file is around 50 MB.
        if self.estimated_zip_size == 0:
            self.estimated_zip_size = 50_000_000

        # Download the most of the files eg. https://github.com/RLBot/RLBotPack/archive/master.zip
        download_and_extract_zip(
            download_url=repo_url + '/archive/' + branch_name + '.zip',
            local_folder_path=checkout_folder, clobber=True,
            progress_callback=self.zip_download_callback,
            unzip_callback=self.unzip_callback)

        # Get paths of all LFS files we need to download from the .gitattributes file.
        lfs_file_paths = []
        gitattributes_file = open(checkout_folder + repo_extraction_name + '.gitattributes')
        for line in gitattributes_file:
            if line.split(' ')[1].endswith('=lfs'):
                lfs_file_paths.append(line.split(' ')[0])
        gitattributes_file.close()

        self.lfs_file_count = len(lfs_file_paths)
        # How much of total progress does one LFS file take:
        self.one_lfs_file_portion = (1.0 - self.ZIP_PORTION) / self.lfs_file_count

        # Download all LFS files.
        for lfs_file_path in lfs_file_paths:
            self.current_progress = 0
            self.current_file_bytes_downloaded = 0
            self.status = 'Downloading ' + lfs_file_path
            print(self.status)

            urllib.request.urlretrieve(
                repo_url + '/raw/' + branch_name + '/' + lfs_file_path,
                checkout_folder + repo_extraction_name + lfs_file_path,
                self.lfs_download_callback)

            self.lfs_files_completed += 1
