###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                     # 
#                                                                             #   
#                                                                             #  
###############################################################################
import datetime

import pandas as pd
import json
import unidecode


def open_json_file_pd(path, doc):
    """
    Convert a JSON string to pandas object, and return a dataframe
    :param path: path of the directory, which needs to be explored
    :param doc: name of json file
    """
    return pd.read_json(path + doc, orient='index')


def validateJSON(json_data):
    """
    Method to validate it as per the standard convention.
    :param  json_data: name of json
    :return boolean
    """
    try:
        json.loads(json_data)
    except ValueError as err:
        return False
    return True

def get_medicine_id(data: dict) -> str:
    return data['medicine_id']


def get_emc_id(data: dict) -> str:
    return data['emc_id']


def get_date(data: dict) -> str:
    return data['revision_date']


def get_year(data: dict) -> str:
    date = datetime.datetime.strptime(get_date(data), '%Y-%m-%d')
    return str(date.year)
