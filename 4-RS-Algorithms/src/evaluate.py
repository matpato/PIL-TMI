import os
import numpy as np
import sys
from myconfiguration import MyConfiguration as Config
from cross_val import \
    prepare_train_test, \
    check_items_in_model, \
    add_dict, \
    calculate_dictionary_mean
from data import three_columns_matrix_to_csr, save_final_data
from dataset import get_dataset_parts
from algorithms import get_evaluation


# ------------------------------------------------------------------------------------------------ #

def get_metrics_dictionaries(n_ontology_sim_metric: int, n_rec_algorithms: int, n_metrics: int):
    total_dicts = n_ontology_sim_metric + n_rec_algorithms + (n_rec_algorithms * n_ontology_sim_metric * n_metrics)
    
    return tuple({} for _ in range(total_dicts))

# ---------------------------------------------------------------------------------------- #

# Function to update metric dictionaries
def update_dictionaries(dictionaries, results, *param_tuple):
    for key, value in dictionaries.items():
        if value is None:
            dictionaries[key] = {}
        dictionaries[key] = add_dict(dictionaries[key], results[key], *param_tuple)
    return dictionaries

# ------------------------------------------------------------------------------------------------ #

def evaluate_dataset(config: Config, dataset_file: str):


    print(f'Evaluating dataset {dataset_file}')
    cv_folds = config.cv
    n = config.n
    dataset_folder = config.dataset_folder.rsplit('/')[-1]
    count_cv = 0

    ratings, \
        original_item_id, \
        original_user_id, \
        users_size, \
        items_size, \
        shuffle_users, \
        shuffle_items = get_dataset_parts(config, dataset_file)


    # Initialize variables
    count_cv = 0
    count_cv_items = 0

    # Initialize dictionaries
    metric_dictionaries = {
        # CB (Content Based)
        'onto_lin': None,
        'onto_resnik': None,
        'onto_jc': None,
        # CF (Collaborative Filtering)
        'als': None,
        'bpr': None,
        # Hybrid
        'als_onto_lin_m1': None,
        'als_onto_resnik_m1': None,
        'als_onto_jc_m1': None,
        'bpr_onto_lin_m1': None,
        'bpr_onto_resnik_m1': None,
        'bpr_onto_jc_m1': None,
        'als_onto_lin_m2': None,
        'als_onto_resnik_m2': None,
        'als_onto_jc_m2': None,
        'bpr_onto_lin_m2': None,
        'bpr_onto_resnik_m2': None,
        'bpr_onto_jc_m2': None,
        'als_onto_lin_m3': None,
        'als_onto_resnik_m3': None,
        'als_onto_jc_m3': None,
        'bpr_onto_lin_m3': None,
        'bpr_onto_resnik_m3': None,
        'bpr_onto_jc_m3': None,
        'als_onto_lin_m4': None,
        'als_onto_resnik_m4': None,
        'als_onto_jc_m4': None,
        'bpr_onto_lin_m4': None,
        'bpr_onto_resnik_m4': None,
        'bpr_onto_jc_m4': None,
    }

    for test_users in np.array_split(shuffle_users, cv_folds):
        test_users_size = len(test_users)
        print("number of test users: ", test_users_size)

        count_cv_items = 0
        for test_items in np.array_split(shuffle_items, cv_folds):
            # models to be used
            test_items_size = len(test_items)
            print("number of test items: ", test_items_size)

            # prepare the data for implicit models
            ratings_test, ratings_train = prepare_train_test(ratings, test_users, test_items)
                
            test_items = check_items_in_model(ratings_train.index_item.unique(), test_items)
            ratings_sparse = three_columns_matrix_to_csr(ratings_train)  # item, user, rating
            # Get the dictionary with all values from  from the get_evaluation function
            evaluation_results = get_evaluation(
                test_users,
                test_users_size,
                count_cv,
                count_cv_items,
                ratings_test,
                ratings_sparse,
                test_items,
                ratings,
                original_item_id,
                config.sim_metric
            )   

            param_tuple = (count_cv, count_cv_items)

            # # Unpack the list of dataframes into separate variables
            metric_dictionaries = update_dictionaries(metric_dictionaries, evaluation_results, *param_tuple)

            count_cv_items += 1
        count_cv += 1

    # calculates mean and save to a csv file all metrics: [P, R, F, fpr, rr, nDCG, auc] (preference order)
    path = f"{config.path2res}/{dataset_file.rsplit('.')[0]}"
    str_folds = f'/results_nfolds{str(cv_folds)}'
    str_n = f'_nsimilar_{str(n)}'
    completed_path = f'{path}{str_folds}{str_n}'
    floated_folds = float(cv_folds * cv_folds)

    for key,value in metric_dictionaries.items():
        if value is None:
            metric_dictionaries[key] = {}
        metric_dictionaries[key] =  calculate_dictionary_mean(metric_dictionaries[key], floated_folds)
        save_final_data( metric_dictionaries[key],f'{completed_path}_{key}.csv' )
            