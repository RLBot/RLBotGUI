import os
import tempfile
import urllib.request
import zipfile
import json
import eel
import time
from pathlib import Path
from shutil import rmtree
from typing import Optional


def download_and_extract_zip(download_url: str, local_folder_path: Path,
                             clobber: bool = False, progress_callback: callable = None,
                             unzip_callback: callable = None):
    """
    :param clobber: If true, we will delete anything found in local_folder_path.
    :return:
    """

    with tempfile.TemporaryDirectory() as tmpdirname:
        downloaded_zip_path = os.path.join(tmpdirname, 'downloaded.zip')
        urllib.request.urlretrieve(download_url, downloaded_zip_path, progress_callback)

        if clobber and os.path.exists(local_folder_path):
            rmtree(local_folder_path)

        if unzip_callback:
            unzip_callback()

        with zipfile.ZipFile(downloaded_zip_path, 'r') as zip_ref:
            zip_ref.extractall(local_folder_path)


def get_json_from_url(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read())


def get_repo_size(repo_full_name) -> Optional[int]:
    """
    Call GitHub API to get an estimate size of a GitHub repository.
    :param repo_full_name: Full name of a repository. Example: 'RLBot/RLBotPack'
    :return: Size of the repository in bytes, or None if the API call fails.
    """
    try:
        data = get_json_from_url('https://api.github.com/repos/' + repo_full_name)
        return int(data["size"] * 1000)
    except:
        return None


class BotpackDownloader:
    """
    Downloads the botpack while updating the progress bar and status text.
    """

    PROGRESSBAR_UPDATE_INTERVAL = 0.1  # How often to update the progress bar (seconds)

    def __init__(self):
        self.status = ''
        self.total_progress = 0

        self.estimated_zip_size = 0
        self.downloaded_bytes = 0
        self.last_progressbar_update_time = 0

    def update_progressbar_and_status(self):
        # it's not necessary to update on every callback, so update
        # only when some amount of time has passed
        now = time.time()
        if now > self.last_progressbar_update_time + self.PROGRESSBAR_UPDATE_INTERVAL:
            self.last_progressbar_update_time = now

            total_progress_percent = int(self.total_progress * 100)
            status = f'{self.status} ({total_progress_percent}%)'

            eel.updateDownloadProgress(total_progress_percent, status)

    def zip_download_callback(self, block_count, block_size, _):
        self.downloaded_bytes += block_size
        self.total_progress = min(self.downloaded_bytes / self.estimated_zip_size, 1.0)
        self.update_progressbar_and_status()

    def unzip_callback(self):
        eel.updateDownloadProgress(100, 'Extracting ZIP file')

    def download(self, repo_owner: str, repo_name: str, branch_name: str, checkout_folder: Path):
        repo_full_name = repo_owner + '/' + repo_name
        repo_url = 'https://github.com/' + repo_full_name

        self.status = f'Downloading {repo_full_name}-{branch_name}'
        print(self.status)
        self.total_progress = 0

        # Unfortunately we can't know the size of the zip file before downloading it,
        # so we have to get the size from the GitHub API.
        self.estimated_zip_size = get_repo_size(repo_full_name) * 0.7

        # If we fail to get the repo size, set it to a fallback value,
        # so the progress bar will show atleast some progress.
        # Let's assume the zip file is around 40 MB.
        if not self.estimated_zip_size:
            self.estimated_zip_size = 40_000_000

        download_and_extract_zip(download_url=repo_url + '/archive/' + branch_name + '.zip',
                                 local_folder_path=checkout_folder,
                                 clobber=True,
                                 progress_callback=self.zip_download_callback,
                                 unzip_callback=self.unzip_callback)
