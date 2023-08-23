import pandas as pd
import numpy as np
from itertools import product
from data import id_to_index
from cross_val import \
    get_shuffle_items, \
    get_shuffle_users

# ---------------------------------------------------------------------------------------- #

def upload_dataset(csv_path, name_prefix):
    """
    :param csv_path: <user, item, rating, ... > csv file
    :param name_prefix: prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    :return: user, item, rating pandas dataframe
    """
    matrix = pd.read_csv(csv_path, header=0, sep=',')
    if len(matrix.columns) > 3:
        matrix.columns = ['user_name', 'item', 'rating', 'user', 'item_label']
        matrix = matrix[['user', 'item', 'rating']]
    else:
        matrix.columns = ['user', 'item', 'rating']

    if matrix.dtypes['item'] == np.object:
        # filter rows for specific ontology
        matrix = matrix[matrix['item'].astype(str).str.startswith(name_prefix)]
        # remove acronym of ontology and convert as int
        matrix['item'] = matrix['item'].str.replace(name_prefix, '').astype(int)

    matrix['rating']=1

    return matrix

# ---------------------------------------------------------------------------------------- #

def get_dataset_parts(config: str, dataset_file: str):
    
    # get the dataset in <user, item, rating> format
    ratings_original = upload_dataset(
        csv_path=f'{config.dataset_folder}/{dataset_file}',
        name_prefix=config.item_prefix
    )
    
    ratings, original_item_id, original_user_id = id_to_index(ratings_original)  # are not unique

    users_size = len(ratings.index_user.unique())
    items_size = len(ratings.index_item.unique())
    shuffle_users = get_shuffle_users(ratings)
    shuffle_items = get_shuffle_items(ratings)

    return ratings, original_item_id, original_user_id, users_size, items_size, shuffle_users, shuffle_items

# ---------------------------------------------------------------------------------------- #

def confirm_all_test_train_similarities(list1, list2, pairs_from_db):
    # check if all item-item pair was found in the database

    lists_combinations = pd.DataFrame(
        list(product(list1, list2)),
        columns=['l1', 'l2']
    )

    ss = lists_combinations.l1.isin(
        pairs_from_db.comp_1.astype('int64').tolist()) & lists_combinations.l2.isin(
        pairs_from_db.comp_2.astype('int64').tolist())

    ss2 = lists_combinations.l2.isin(
        pairs_from_db.comp_1.astype('int64').tolist()) & lists_combinations.l1.isin(
        pairs_from_db.comp_2.astype('int64').tolist())

    not_found_in_db = lists_combinations[(~ss) & (~ss2)]

    not_found_list_1 = not_found_in_db.l1.unique().tolist()
    not_found_list_2 = not_found_in_db.l2.unique().tolist()

    return not_found_list_1, not_found_list_2


# ---------------------------------------------------------------------------------------- #

def get_items_ids(dataset, name_prefix=None):
    """
    :param dataset: dataset
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    """
    #dataset.item = dataset.item.map(lambda x: x.lstrip(name_prefix)).astype(int)
    ids = dataset.item.unique()

    return ids