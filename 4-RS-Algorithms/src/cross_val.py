import numpy as np
from statistics import median
import sys

def get_shuffle_users(dataset):
    """
    shuffle the array of users
    :param dataset: pandas dataframe
    :return: array of shuffled users
    """
    users = np.array(dataset.index_user.unique())
    np.random.shuffle(users)
    # print("Users shape: ", users.shape)
    return users

# ---------------------------------------------------------------------------------------- #

def get_shuffle_items(dataset):
    """
    shuffle the array of items
    :param dataset: pandas dataframe
    :return: array of shuffled items
    """
    items = np.array(dataset.index_item.unique())

    np.random.shuffle(items)
    # print("Items shape: ",  items.shape)
    return items

# ---------------------------------------------------------------------------------------- #

def divide_users_train_test(users, min_val, max_val):
    return np.array(users)[min_val:max_val]


def divide_items_train_test(items, min_val, max_val):
    return np.array(items)[min_val:max_val]

# ---------------------------------------------------------------------------------------- #

def calculate_dictionary_mean(dictionary, division):
    for i in dictionary:
        dictionary[i] = [val / division for val in dictionary[i]]       
    return dictionary

# ---------------------------------------------------------------------------------------- #

def prepare_train_test_(ratings, test_users, test_items):
    """
    Serarates the test and the train from the whole dataset

    :param ratings: pandas dataframe of user, item, rating
    :param test_users: list of users IDs to be used as test
    :param test_items: list of items IDs to be used as test
    :return: pd DataFrame test_set, pd DataFrame train_set
    """
    test_set = ratings[(ratings.user.isin(test_users)) & (ratings.item.isin(test_items))]

    # train_set = ratings.drop(
    #    ratings[(ratings.user.isin(test_users)) & (ratings.item.isin(test_items))].index)  # train
    train_set = ratings[~(ratings.item.isin(test_items))]

    return test_set, train_set

# ---------------------------------------------------------------------------------------- #

def prepare_train_test(ratings, test_users, test_items):
    """
    Separates the test and the train from the whole dataset

    :param ratings: pandas dataframe of user, item, rating
    :param test_users: list of users IDs to be used as test
    :param test_items: list of items IDs to be used as test
    :return: pd DataFrame test_set, pd DataFrame train_set
    """

    test_set = ratings[(ratings.index_user.isin(test_users)) & (ratings.index_item.isin(test_items))]
    # train_set = ratings.drop(
    #    ratings[(ratings.user.isin(test_users)) & (ratings.item.isin(test_items))].index)  # train
    train_set = ratings[~((ratings.index_user.isin(test_users)) & (ratings.index_item.isin(test_items)))]

    return test_set, train_set

# ---------------------------------------------------------------------------------------- #

def check_items_in_model(train_items, test_items):
    # check = True
    mask = np.isin(train_items, test_items)

    if len(train_items[mask]) != len(test_items):
        # check = False
        mask2 = np.isin(test_items, train_items)

        print("Items in model: ", test_items[~mask2])

        test_items = test_items[mask2]

    # print(check)

    return test_items

# ---------------------------------------------------------------------------------------- #

def add_dict(dict1, dict2, count_cv, count_cv_items):
    if count_cv == 0 and count_cv_items == 0:
        return dict2
    else:
        union = set(dict1) | set(dict2)
        new_dict = {}
        for key in union:
            new_dict[key] = [x + y for x, y in zip(dict1[key], dict2[key])]
        return new_dict
