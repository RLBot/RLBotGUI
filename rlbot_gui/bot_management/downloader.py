import json
import multiprocessing as mp
import os
import tempfile
import time
import urllib.request
import zipfile
from enum import Enum
from functools import partial
from pathlib import Path
from shutil import rmtree, copyfileobj
from typing import Optional

import eel
from rlbot_gui.persistence.settings import load_settings

RELEASE_TAG = 'latest_botpack_release_tag'
FOLDER_SUFFIX = 'master'

MAPPACK_DIR = 'RLBotMapPack-' + FOLDER_SUFFIX

class BotpackStatus(Enum):
    REQUIRES_FULL_DOWNLOAD = -1
    SKIPPED = 0
    SUCCESS = 1


# https://stackoverflow.com/a/64547381/10930209
def remove_empty_folders(root: Path):
    for path, _, _ in list(os.walk(root))[::-1]:
        if len(os.listdir(path)) == 0:
            # we need this because sometimes a folder is in use
            # we just delete what we can and move on, it isn't that big a deal - they're just empty folders
            try:
                os.rmdir(path)
            except Exception:
                continue



def download_and_extract_zip(download_url: str, local_folder_path: Path, local_subfolder_name: str = None,
                             clobber: bool = False, progress_callback: callable = None,
                             unzip_callback: callable = None):
    """
    :param local_subfolder_name: The folder inside RLBotPackDeletable - right now, this should be 'RLBotPack-master'
    :param clobber: If true, we will delete anything found in local_folder_path.
    :return:
    """

    with tempfile.TemporaryDirectory() as tmpdirname:
        downloaded_zip_path = os.path.join(tmpdirname, 'downloaded.zip')
        try:
            urllib.request.urlretrieve(download_url, downloaded_zip_path, progress_callback)
        except Exception as err:
            print(err)
            return BotpackStatus.SKIPPED

        if clobber and os.path.exists(local_folder_path):
            rmtree(local_folder_path)

        if unzip_callback:
            unzip_callback()

        with zipfile.ZipFile(downloaded_zip_path, 'r') as zip_ref:
            zip_ref.extractall(local_folder_path)

        full_path = local_folder_path if local_subfolder_name is None else os.path.join(local_folder_path, local_subfolder_name)
        if not os.path.exists(full_path):
            folder_name = os.listdir(local_folder_path)[0]
            os.rename(os.path.join(local_folder_path, folder_name), full_path)
    return BotpackStatus.SUCCESS



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


class RepoDownloader:
    """
    Downloads the given repo while updating the progress bar and status text.
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

    def download(self, repo_owner: str, repo_name: str, checkout_folder: Path, update_tag_setting=True):
        repo_full_name = repo_owner + '/' + repo_name
        folder_suffix = FOLDER_SUFFIX

        self.status = f'Downloading {repo_full_name}-{folder_suffix}'
        print(self.status)
        self.total_progress = 0

        # Unfortunately we can't know the size of the zip file before downloading it,
        # so we have to get the size from the GitHub API.
        # Github's compression ratio for the botpack is around 75%
        self.estimated_zip_size = get_repo_size(repo_full_name) * 0.75

        # If we fail to get the repo size, set it to a fallback value,
        # so the progress bar will show at least some progress.
        # Let's assume the zip file is around 60 MB.
        if not self.estimated_zip_size:
            self.estimated_zip_size = 60_000_000

        try:
            latest_release = get_json_from_url(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest")
        except Exception as err:
            print(err)
            return BotpackStatus.SKIPPED

        success = download_and_extract_zip(download_url=latest_release['zipball_url'],
                                 local_folder_path=checkout_folder,
                                 local_subfolder_name=f"{repo_name}-{folder_suffix}",
                                 clobber=True,
                                 progress_callback=self.zip_download_callback,
                                 unzip_callback=self.unzip_callback)
        
        if success is BotpackStatus.SUCCESS and update_tag_setting:
            settings = load_settings()
            settings.setValue(RELEASE_TAG, latest_release["tag_name"])

        return success


class BotpackUpdater:
    """
    Updates the botpack while updating the progress bar and status text.
    """
    def __init__(self):
        self.status = ''

        self.total_steps = 0
        self.current_step = 0

    def update_progressbar_and_status(self, status=None):
        total_progress_percent = int(min(self.current_step / self.total_steps, 1) * 100) if self.total_steps != 0 else 0
        if status is None: status = self.status
        status = f'{status} ({total_progress_percent}%)'
        eel.updateDownloadProgress(total_progress_percent, status)


    def download_single(self, tmpdir: Path, repo_url: str, tag: int):
        download_url = f"{repo_url}/releases/download/incr-{tag}/incremental.zip"
        downloaded_zip_path = os.path.join(tmpdir, f"downloaded-{tag}.zip")
        try:
            urllib.request.urlretrieve(download_url, downloaded_zip_path)
        except Exception as err:
            print(err)
            return False
        return tag


    def update(self, repo_owner: str, repo_name: str, checkout_folder: Path):
        repo_full_name = repo_owner + '/' + repo_name
        repo_url = 'https://github.com/' + repo_full_name
        master_folder = repo_name + "-" + FOLDER_SUFFIX

        settings = load_settings()
        local_release_tag = settings.value(RELEASE_TAG, type=str)

        try:
            latest_release = get_json_from_url(f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest")
        except Exception as err:
            print(err)
            return BotpackStatus.REQUIRES_FULL_DOWNLOAD

        # If the botpack is missing, just download the whole botpack
        if local_release_tag == "" or not os.path.exists(os.path.join(checkout_folder, master_folder)):
            return BotpackStatus.REQUIRES_FULL_DOWNLOAD

        if local_release_tag == latest_release["tag_name"]:
            print("The botpack is already up-to-date! Redownloading just in case.")
            return BotpackStatus.REQUIRES_FULL_DOWNLOAD

        releases_to_download = list(range(int(local_release_tag.replace("incr-", "")) + 1, int(latest_release["tag_name"].replace("incr-", "")) + 1))

        # If there are too many patches to be applied at once, don't bother and instead do a full redownload of the bot pack. Each patch has a certain
        # amount of overhead so at some point it becomes faster to do a full download. We also do not want to spam github with too many download requests.
        if len(releases_to_download) > 50:
            return BotpackStatus.REQUIRES_FULL_DOWNLOAD
            
        local_folder_path = Path(os.path.join(checkout_folder, master_folder))

        self.total_steps = len(releases_to_download)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Spawn up to 15 download threads, we want to download the updates at a fast speed without saturating the users network connection.
            # These threads only serve to initiate the download and mostly sit idle.
            with mp.Pool(min(15, len(releases_to_download))) as p:
                # It's very important that patches are applied in order
                # This is why we use imap and not imap_unordered
                # we want simultaneous downloads, but applying patches out of order would be a very bad idea
                for tag in p.imap(partial(self.download_single, tmpdir, repo_url), releases_to_download):
                    if tag is False:
                        print("Failed to complete botpack upgrade")
                        return BotpackStatus.SKIPPED
                    
                    # apply incremental patch
                    print(f"Applying patch incr-{tag}")
                    self.update_progressbar_and_status(f"Applying patch {tag}")
                    downloaded_zip_path = os.path.join(tmpdir, f"downloaded-{tag}.zip")
                    
                    with zipfile.ZipFile(downloaded_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(local_folder_path)

                    with open(local_folder_path / ".deleted", "r", encoding="utf-16") as deleted_ref:
                        files = deleted_ref.readlines()

                        for line in files:
                            if line.replace("\n", "").strip() != "":
                                file_name = local_folder_path / line.replace("\n", "")
                                if os.path.isfile(file_name):
                                    os.remove(file_name)
                                    
                    # encase something goes wrong in the future, we can save our place between commit upgrades
                    settings.setValue(RELEASE_TAG, f"incr-{tag}")
                    self.current_step += 1
        
        remove_empty_folders(local_folder_path)

        self.update_progressbar_and_status(f"Done")
        return BotpackStatus.SUCCESS


class MapPackUpdater:

    def __init__(self, location: Path, repo_owner: str, repo_name: str):
        self.location = location
        self.repo_owner = repo_owner
        self.repo_name = repo_name

        self.full_path = Path(location) / f"{repo_name}-{FOLDER_SUFFIX}"

    
    def needs_update(self) -> BotpackStatus:
        index = self.get_map_index()
        if not index:
            return BotpackStatus.REQUIRES_FULL_DOWNLOAD

        revision = index["revision"]

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        latest_release = get_json_from_url(url)
        latest_revision = int(latest_release["tag_name"][1:])

        if latest_revision > revision:
            return BotpackStatus.REQUIRES_FULL_DOWNLOAD
        else:
            print("Map pack is already the latest. Not downloading anything")
            return BotpackStatus.SUCCESS

    def get_map_index(self):
        """
        For a map pack, gets you the index.json data
        """
        index_path = self.full_path / "index.json"

        if index_path.exists():
            with open(index_path) as file:
                index = json.load(file)
            
            return index

    def hydrate_map_pack(self, old_index):
        """
        Compares the old_index with current index and for any
        maps that have updated the revision, we grab them
        from the latest revision
        """
        # Deletions not implemented. Only additions and updates

        # index looks like:
        # {revision: 1, maps: [{path: a/b.upk, revision: 2}]}

        new_index = self.get_map_index()
        new_maps = {info["path"]: info["revision"] for info in new_index["maps"]}

        old_maps = []
        if old_index:
            old_maps = {info["path"]: info["revision"] for info in old_index["maps"]}


        to_fetch = set()
        for path, revision in new_maps.items():
            old_revision = -1
            if path in old_maps:
                old_revision = old_maps[path]

            if old_revision < revision:
                to_fetch.add(path)
        
        if to_fetch:
            filename_to_path = {Path(p).name: p for p in to_fetch}

            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            latest_release = get_json_from_url(url)
            assets = latest_release["assets"]

            for asset in assets:
                if asset["name"] in filename_to_path:
                    local_path = filename_to_path[asset["name"]]
                    target_path = self.full_path / local_path
                    print("Will fetch updated map: ", asset["name"])

                    headers = {"Accept": "application/octet-stream"}
                    request = urllib.request.Request(asset["url"], headers=headers)
                    with urllib.request.urlopen(request) as response:
                        with open(target_path, "wb") as filehandle:
                            copyfileobj(response, filehandle)

