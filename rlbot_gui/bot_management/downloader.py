from pathlib import Path
import urllib
import zipfile


def download_and_extract_zip(download_url: str, local_zip_path: Path, local_folder_path: Path):
    urllib.request.urlretrieve(download_url, local_zip_path)

    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(local_folder_path)
