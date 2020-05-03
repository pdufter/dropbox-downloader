# dropbox-downloader

**TL;DR: If you want to download all your dropbox file to an external hard drive, you can use this script.**


Assume you store large amounts of data in your dropbox (e.g., hundreds of GB) and 
you want to get hold of your data again (e.g., because you want to switch cloud provider
or simply want to have a local backup). Those are your options:

1) Download files and folder manually (cumbersome as dropbox has limiations on the size of the folder 
and maximum number of files). 
2) Synchronize a local machine with your dropbox account. Prerequisites: your internal hard drive is big 
enough to store all your data (unlikely). 

As I did not find any better alternative, I wrote this simple script, which uses the python dropbox
API to download all of your data to an external hard drive. As this is potentially a long process, 
I tried to make it more stable by storing the hashes of downloaded files.

If you come across a better solution on how to download your whole dropbox data, let me know. 



# Usage

1) In your Dropbox Account register an app to get a secret TOKEN (see [here](https://www.dropbox.com/developers/apps)). Store the secret token in an 
environment variable called `DB_TOKEN`.

2) Clone the repo and install the dependencies. 

3) Run the script
```
python dropbox_download.py \
--log {where to store the log file} \
--hashtable {where to store the hash table (sqlite)} \
--target_folder {where to download your data, potentially external hard drive} \
--compare_hashes
```


(c) 2020 Philipp Dufter