# Preparation of data for PIL

Guide to reproduce all the work from scratch.

This module allows you to extract, remove duplicates (deduplication) and all non-valid files. Non-valid files are those that are not in the language defined by the user (e.g. en), that do not have an medicine name or date. 

The langdetect library is used to define the language. 

This module uses the concept ELT (extract-load-transform). ELT is a type of data integration that refers to the three steps (extract, load, transform) used to blend data from multiple sources.

For our dataset, we only want to include files with the following characteristics:
- medicine' name
- available composition
- available therapeutic indications
- available contraindications


The next step will be extracts and normalizes entities in NER folder.

---------------------------------------------------------

## Summary
- [1. Run docker shell script](#1)
- [2. PILs](#2)
  - [2.1. Retrieve PILs dataset](#2.1)
- [3. Prepare PILs](#3)
  - [3.1. Check other versions](#3.1)
  - [3.2. Remove duplicates](#3.2)
  - [3.3. Clean data from non-valid articles](#3.3)
- [4. Requirements](#4)
  - [4.1. Libraries](#4.1)

---------------------------------------------------------


# 1. Run docker shell script<a name="1"></a>

You can run a shell script (docker.sh) that will create a docker image and the container. You just need to indicate the name of the docker image and the folder where you will save the results. The container name will be automatically created from the image (ended by ##\_ctr).

```
bash docker.sh <name_of_image> <name_of_data_folder>
```

Provide the execution permission (if needed) to the script by giving command
```
chmod +777 docker
```

# 2. CORD-19<a name="2"></a>

## 2.1. Retrieve the CORD-19 dataset<a name="2.1"></a>

Two options for extracting tar.gz files are implemented, such as:


### a) downloaded from url
Here we download and extract directly from url, based on date and tar.gz filename.

```
python3 extract_medicine_data_from_url.py 
python3 get_medicines_url.py 
```


# 3. Prepare PILs<a name=#3></a>

## 3.1. Check other versions<a name=#3.1></a>

If, you have already downloaded, then you can delete all the files you have downloaded in the past, because there is a list with all the downloaded files in a csv file 'list_json_files.csv'

````
python3 remove_duplicate_versions.py
````

## 3.2. Remove duplicates<a name=#3.2></a>

Find duplicates files in folders. After that, you can choose between 'copy' or 'move' uniques to another folder

````
python3 remove_duplicate_files.py 
````

## 3.3. Clean data from non-valid articles<a name=#3.3></a>

As valid articles, we define those that are written in English (or another language defined by user), contains an author name and date information

````
python3 cleaning_data.py
````

You must enter your email in utils2pubmed: Entrez.email = <INSERT_YOUR_EMAIL_HERE>

Multiple languages can be chosen, when separated by ','. The ids of the non-valid articles are registered in a text file (blacklist.txt), and the files will be moved to 'garbage' folder

# 4. Requirements<a name="4"></a>

## 4.1. Libraries<a name="4.1"></a>

- numpy
- pandas
- spacy==3.1.0
- scipy
- sklearn
- lenskit
- unidecode
- unicode
- requests
- langdetect==1.0.9
- metapub==0.5.5
- Bio
- entrezpy==2.1.3
- crossref-commons