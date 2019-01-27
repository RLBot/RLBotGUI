import urllib
import zipfile


def download_and_extract_zip(download_url, local_zip_path, local_folder_path):
    urllib.request.urlretrieve(download_url, local_zip_path)

    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(local_folder_path)
