###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#  (Adapted from Pedro Ruas)                                                  #  
# @last update:                                                               #  
#   version 1.1: 25 May 2022 - add sleep counter, create an auxiliar functions#
#   to create the <user, item, rating, year> dataset                          #      
#   (author: matilde.pato@gmail.com  )                                        # 
#                                                                             #   
#                                                                             #  
###############################################################################
#
# python3 create_med2care_recsys_dataset.py

import numpy as np
from pandas import DataFrame
from datetime import datetime
from utils.myconfiguration import MyConfiguration as Config
from utils.utils import get_blacklist, set_blacklist, save_to_csv, save_metadata
from utils.utils2json import open_json_file, get_date
import os

POSITIVE_RATING = 1
NEGATIVE_RATING = -1

# ------------------------------------------------------------------------------------------------ #

def get_id_name_list_entity(entity_field):
    name_id = [
        (entity[3].split('/')[-1], entity[2]) for entity in entity_field
    ]

    return name_id

# ------------------------------------------------------------------------------------------------ #

def create_dataset(path_entities, path_blacklist):
    """
    create the dataset with parameters <user, username, item, item_name, rating, date>
    :param path_entities: path of entities json files
    :param path_metadata: path of the metadata csv files
    :param path_blacklist: path with the blacklist (list of non-validate files)
    :return count: number of files processed (only for metadata)
    :return user_item_rating_all: list with <user, username, item, item_name, rating, date> values
    """

    import time
    user_item_rating_all = []
    entities_list_of_json_files = os.listdir(path_entities)

    # get all articles id that cannot be considered in use case
    entities_blacklist = get_blacklist(file=path_blacklist)
    # metadata = pd.read_csv(path_metadata)

    count = 0
    count_sleep = -1
    for file in entities_list_of_json_files:
        count += 1
        count_sleep += 1
        if file in entities_blacklist:
            continue
        print(count, "-", len(entities_list_of_json_files), ': ', file)

        # check valid json file, i.e. contains values
        try:
            j_file_entities = open_json_file(path_entities, file)
        except Exception as e:
            print(f'Json file does not contain values. Error message {e}')
            set_blacklist(path_blacklist, file.replace('_entities.json', ''))
            continue

        composition = get_id_name_list_entity(j_file_entities['composition'])
        therapeutic_indications = get_id_name_list_entity(j_file_entities['therapeutic_indications'])

        if len(composition) == 0 or len(therapeutic_indications) == 0:
            print(f'Json file does not contain values.')
            set_blacklist(path_blacklist, file.replace('_entities.json', ''))
            continue

        disease = get_id_name_list_entity(j_file_entities['disease'])
        incompatibilities = get_id_name_list_entity(j_file_entities['incompatibilities'])
        date = get_date(j_file_entities)

        dataset = []

        for item, item_name in composition:
            for user, username in therapeutic_indications:
                dataset.append((user, username, item, item_name, POSITIVE_RATING, date))

            for user, username in disease:
                dataset.append((user, username, item, item_name, NEGATIVE_RATING, date))

        user_item_rating_all.append(dataset)

        if count_sleep > 999:
            time.sleep(0.5)
            count_sleep = -1

    return count, user_item_rating_all

# ------------------------------------------------------------------------------------------------ #

def main():
    start_time = datetime.now()

    config: Config = Config.get_instance()

    # create the dataset with <user, username, item, item_name, rating, year> values
    n_files, user_item_rating_all = create_dataset(
        path_entities=config.entities_json_folder,
        path_blacklist=config.path_to_blacklist
    )

    flat_list = []
    for sublist in user_item_rating_all:
        for item in sublist:
            flat_list.append(item)

    array = np.array(flat_list)

    final_data = DataFrame(
        array,
        columns=[
            'user', 'username', 'item', 'item_name', 'rating', 'year'
        ]
    )

    final_data = final_data.drop_duplicates(keep='first')

    print('saving data')
    save_to_csv(
        df=final_data[['user', 'username', 'item', 'item_name', 'rating', 'year']],
        header=True,
        path=config.path_ds
    )

    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                No. Medicines: {n_files}\n\
                Results: {config.path_ds}\n\
                '
    save_metadata(config.path_to_info, metadata)
    print("FINISHED!")


if __name__ == '__main__':
    main()
