import os
import logging
from tqdm import tqdm
import argparse
import datetime
import time
import unicodedata

from sqlitedict import SqliteDict
import dropbox


def normalize(string):
    return unicodedata.normalize("NFC", string)


def get_logger(name, filename, level=logging.WARN):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(filename)
    ch = logging.StreamHandler()

    fh.setLevel(logging.DEBUG)
    ch.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def download_file_sub(entry):
    try:
        new_path = "{}{}".format(TARGET_FOLDER, normalize(entry.path_display))
        LOG.info("Downloading file {} -> {}.".format(normalize(entry.path_display), new_path))
        DBX.files_download_to_file(new_path, entry.path_display)
        if COMPARE_HASHES:
            HASHTABLE[normalize(entry.path_lower)] = {"id": normalize(entry.id),
                                                      "path_lower": normalize(entry.path_lower),
                                                      "path_display": normalize(entry.path_display),
                                                      "content_hash": normalize(entry.content_hash),
                                                      "entry": entry,
                                                      "last_updated": datetime.datetime.now().__str__()}
    except FileNotFoundError:
        # try to recreate the directory
        folder = "/".join(new_path.split("/")[:-1])
        if os.path.exists(folder):
            raise ValueError("Unknown error with {}.".format(new_path))
        else:
            LOG.warning("FileNotFoundError trying to recreate the folder {}.".format(new_path))
            os.makedirs(folder)
            download_file_sub(entry)
    except dropbox.exceptions.ApiError:
        LOG.warning("Unknown API Error with {}.".format(normalize(entry.path_display)))


def download_file(entry):
    if entry.is_downloadable:
        new_path = "{}{}".format(TARGET_FOLDER, normalize(entry.path_display))
        file_exists = os.path.exists(new_path)
        if file_exists:
            if not COMPARE_HASHES:
                LOG.info("File already exists - skipping: {}.".format(normalize(entry.path_display)))
            elif normalize(entry.path_lower) not in HASHTABLE:
                LOG.warning("Path exists but not registered in hashtable: {}".format(normalize(entry.path_display)))
                import ipdb
                ipdb.set_trace()
                download_file_sub(entry)
            else:
                if HASHTABLE[normalize(entry.path_lower)]["content_hash"] != normalize(entry.content_hash):
                    download_file_sub(entry)
                else:
                    LOG.info("Unchanged file {} <-> {}.".format(normalize(entry.path_display), new_path))
        else:
            download_file_sub(entry)
    else:
        LOG.warning("Entry not downloadable: {}.".format(normalize(entry.path_display)))


def download_folder(entry):
    new_path = "{}{}".format(TARGET_FOLDER, normalize(entry.path_display))
    file_exists = os.path.exists(new_path)
    if not file_exists:
        LOG.info("Creating folder {}.".format(new_path))
        os.makedirs(new_path)


def download_entry(entry):
    if isinstance(entry, dropbox.files.FolderMetadata):
        download_folder(entry)
    elif isinstance(entry, dropbox.files.FileMetadata):
        download_file(entry)


def download_entries(entries):
    for entry in tqdm(entries, desc="entries"):
        download_entry(entry)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default=None, type=str, required=True, help="Path to log file.")
    parser.add_argument("--hashtable", default=None, type=str, required=True, help="Path to hash table.")
    parser.add_argument("--target_folder", default=None, type=str, required=True,
                        help="Path to target folder where downloaded data is stored.")
    parser.add_argument("--compare_hashes", action="store_true", help="""Whether to compare hashes of incoming files to hashes in the hashtable.
    	If not set, all files are downloaded, regardless of existing versions.""")
    args = parser.parse_args()

    global LOG
    global HASHTABLE
    global TARGET_FOLDER
    global DBX
    global COMPARE_HASHES

    LOG = get_logger("dbdownload", args.log)
    COMPARE_HASHES = args.compare_hashes
    if COMPARE_HASHES:
        HASHTABLE = SqliteDict(args.hashtable, autocommit=True)
    token = os.environ.get("DB_TOKEN")
    DBX = dropbox.Dropbox(token)
    TARGET_FOLDER = args.target_folder

    crawler = DBX.files_list_folder('', recursive=True)
    pbar = tqdm(desc="crawler")
    pbar.update(1)
    download_entries(crawler.entries)
    while crawler.has_more:
        pbar.update(1)
        crawler = DBX.files_list_folder_continue(crawler.cursor)
        download_entries(crawler.entries)
    pbar.close()
    if COMPARE_HASHES:
        HASHTABLE.close()


def main_wrapper(N_RESTARTS):
    if N_RESTARTS >= 10:
        raise ValueError("Too many restarts... Shutting down.")
    try:
        main()
    except KeyboardInterrupt:
        command = input("Are you sure you want to terminate the download (y/n)?")
        if command == "y":
            LOG.info("Terminating. Closing Hashtable...")
            if COMPARE_HASHES:
                HASHTABLE.close
        else:
            LOG.info("Continuing...")
            main_wrapper(N_RESTARTS)
    except:
        N_RESTARTS += 1
        LOG.warning("Unknown error, restarting (try: {}).".format(N_RESTARTS))
        time.sleep(60)
        main_wrapper(N_RESTARTS)


if __name__ == '__main__':
    main_wrapper(0)
