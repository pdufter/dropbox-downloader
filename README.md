# dropbox-downloader

**TL;DR: If you want to download all your dropbox file to an external hard drive, you can use this script.**


Python script to download all data from your dropbox account.

Assume you store large amounts of data in your dropbox (e.g., hundreds of GB) and 
you want to get hold of your data again (e.g., because you want to switch cloud provider
or simply want to have a local backup). As far as I can see you have some options: 

1) Download files and folder manually (cumbersome as dropbox has limiations on the size of the folder 
and maximum number of files). 
2) Synchronize a local machine with your dropbox account. Prerequisites: your internal hard drive is big 
enough to store all your data (unlikely). 

As I did not find any better alternative, I wrote this simple script, which uses the python dropbox
API to download all of your data to an external hard drive. As this is potentially a long process, 
it stores the hashes of the downloaded files to enable restarting of the process in case
you interrrupt it or it fails for some reason. 

If you come across a better solution on how to download your whole dropbox data, let me know. 



# Usage

1) In your Dropbox Account register an app to get a secret TOKEN (see [here](https://www.dropbox.com/developers/apps)). Store the secret token in an 
environment variable called `DB_TOKEN`.

2) Clone the repo an install the dependencies. 

3) Run the script
```
python dropbox_download.py \
--log {where to store the log file} \
--hashtable {where to store the hash table (sqlite)} \
--target_folder {where to download your data, potentially external hard drive} \
--compare_hashes
```
Use the flag `compare_hashes` when you only want to download files if the hash has changed or is not contained in the hash table. The Dropbox hashes are used.


(c) 2020 Philipp Dufter