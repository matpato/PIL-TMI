import gc
import numpy as np
import pandas as pd
from pandas import DataFrame
from implicit.bpr import BayesianPersonalizedRanking
from implicit.als import AlternatingLeastSquares
from recommender_evaluation import \
    get_top_n, \
    get_real_item_rating, \
    false_positive_rate, \
    precision, \
    recall, \
    fmeasure, \
    reciprocal_rank, \
    ndcg_at_k, \
    get_auc, \
    get_relevants_by_user
from cross_val import calculate_dictionary_mean
from database import get_read_all
from myconfiguration import MyConfiguration as Config
from multiprocessing import cpu_count

RANDOM_STATE = 123321
config = Config.get_instance()
# ---------------------------------------------------------------------------------------- #


def recommendations_implicit(model, train_data, test_items, user):
    user_items = train_data.T.tocsr()  # user, item, rating
    return model.rank_items(userid=user, user_items=user_items, selected_items=test_items)

# ---------------------------------------------------------------------------------------- #

def map_original_id_to_system_id(item_score, original_item_id):
    """
    map the original id to the system ids
    :param item_score:
    :param original_item_id:
    :return:
    """
    prefix = config.item_prefix[:-1]
    iscore_ontology = item_score.rename(columns={"item": "item_" + prefix})
    iscore_ontology["item"] = iscore_ontology["item_" + prefix].map(
        original_item_id.set_index('item')["new_index"]).fillna(0)
    return iscore_ontology

# ---------------------------------------------------------------------------------------- #

def map_system_id_to_original_id(item_score, original_item_id):
    """
    map the id to the original ids
    :param item_score:
    :param original_item_id:
    :return:
    """
    prefix = config.item_prefix[:-1]
    item_score["item_" + prefix] = item_score["item"].map(
        original_item_id.set_index('new_index')["item"]).fillna(0)
    return item_score

# ---------------------------------------------------------------------------------------- #

def select_metric(scores_by_item, metric):
    """
    select the column with the metric to use
    :param scores_by_item: pd DataFrame with all compounds and metrics
    :param metric: metric to select to calculate the mean of the similarities
    :return: pd DataFrame with columns item, score
    """
    item_score = scores_by_item[['comp_1', metric]]

    item_score = item_score.groupby('comp_1').apply(
        lambda x: x.sort_values(metric, ascending=False).head(config.n).mean()
    )

    item_score = item_score.rename(columns={'comp_1': 'item', metric: 'score'})
    item_score.item = item_score.item.astype(int)

    return item_score

# ---------------------------------------------------------------------------------------- #

def onto_algorithm(train_ratings_for_t_us, test_items_onto_id, metric):
    """
    :param train_ratings_for_t_us:
    :param test_items_onto_id:
    :param metric:
    :return: pandas dataframe: columns = item, score (item with onto_id)
    """

    # get just the IDs of the items in the train set
    train_items_for_t_us = train_ratings_for_t_us.item.unique()
    # training items for this user to be used for finding the similarity
    # get the score for each item in the test set
    scores_by_item = get_score_by_item(test_items_onto_id, train_items_for_t_us)
    if len(scores_by_item) == 0:
        return [], [], []
    iscore_lin, iscore_resnik, iscore_jc = [], [], []

    if metric in ('sim_lin', 'all'):
        iscore_lin = select_metric(scores_by_item, 'sim_lin')
    if metric in ('sim_resnik', 'all'):
        iscore_resnik = select_metric(scores_by_item, 'sim_resnik')
    if metric in ('sim_jc', 'all'):
        iscore_jc = select_metric(scores_by_item, 'sim_jc')
    
    return iscore_lin, iscore_resnik, iscore_jc

# ---------------------------------------------------------------------------------------- #

def all_evaluation_metrics(item_score, ratings_t_us, test_items, relevant, metrics_dict):
    """
    calculate the top k (size of the list of recommendations) for all metrics:
        precision,
        recall,
        f1_score,
        false_positive_rate,
        reciprocal_rank,
        ndcg,
        auc
    :param item_score:
    :param ratings_t_us:
    :param test_items:
    :param relevant:
    :param metrics_dict:
    :return: list of the top k with all metrics in that specific order:
        precision,
        recall,
        f1_score,
        false_positive_rate,
        reciprocal_rank,
        ndcg,
        auc
    """

    user_r = [0.0]
    user_fpr = [0.0]
    k = config.topk
    for i in range(1, k + 1):
        top_n = get_top_n(item_score, i)
        top_n.item = top_n.item.astype(int)

        topn_real_ratings = get_real_item_rating(top_n, ratings_t_us).rating

        fpr_eval_metric = false_positive_rate(test_items, relevant, top_n)

        recs = np.array(top_n.item).astype(int)
        precision_eval_metric = precision(recs, np.array(relevant))
        recall_eval_metric = recall(recs, np.array(relevant))
        f1_score_eval_metric = fmeasure(precision_eval_metric, recall_eval_metric)
        reciprocal_rank_eval_metric = reciprocal_rank(topn_real_ratings)

        user_r.append(recall_eval_metric)
        user_fpr.append(fpr_eval_metric)

        ndcg_eval_metric = ndcg_at_k(topn_real_ratings, i, method=0)

        auc_eval_metric = get_auc(user_r, user_fpr)

        if len(metrics_dict) != k:
            metrics_dict.update(
                {
                    'top' + str(i): [
                        precision_eval_metric,
                        recall_eval_metric,
                        f1_score_eval_metric,
                        fpr_eval_metric,
                        reciprocal_rank_eval_metric,
                        ndcg_eval_metric,
                        auc_eval_metric
                    ]
                }
            )

        else:
            old = np.array(metrics_dict['top' + str(i)])
            new = np.array([
                precision_eval_metric,
                recall_eval_metric,
                f1_score_eval_metric,
                fpr_eval_metric,
                reciprocal_rank_eval_metric,
                ndcg_eval_metric,
                auc_eval_metric]
            )

            to_update = old + new
            metrics_dict.update({'top' + str(i): to_update})

    return metrics_dict

# ---------------------------------------------------------------------------------------- #
def process_sim(data, iscore, iscore_als, iscore_bpr, item_id, ratings, titems, relevant, ftuserssize, sim_name, metrics_count):
    
    sim_name = sim_name.split('_')[1]
    iscore = map_original_id_to_system_id(iscore, item_id)
    merge_data = {}    
    for m in range(1, metrics_count + 1):
        merge_data[f'iscore_als_onto_{sim_name}_m{m}'] = merge_algorithms_scores(iscore, iscore_als, m)
        merge_data[f'iscore_bpr_onto_{sim_name}_m{m}'] = merge_algorithms_scores(iscore, iscore_bpr, m)
 
    data['onto_' + sim_name] = {}    
    data['onto_' + sim_name] = all_evaluation_metrics(
        iscore, ratings, titems, relevant, data['onto_' + sim_name]
    )
    
    for m in range(1, metrics_count + 1):
        data[f'als_onto_{sim_name}_m{m}'] = {}
        data[f'als_onto_{sim_name}_m{m}'] = all_evaluation_metrics(
            merge_data[f'iscore_als_onto_{sim_name}_m{m}'], ratings, titems, relevant, data[f'als_onto_{sim_name}_m{m}']
        )
        data[f'bpr_onto_{sim_name}_m{m}'] = {}
        data[f'bpr_onto_{sim_name}_m{m}'] = all_evaluation_metrics(
            merge_data[f'iscore_bpr_onto_{sim_name}_m{m}'], ratings, titems, relevant, data[f'bpr_onto_{sim_name}_m{m}']
        )
    
    data['onto_' + sim_name] = calculate_dictionary_mean(data['onto_' + sim_name], ftuserssize)

    for m in range(1, metrics_count + 1):
        data[f'als_onto_{sim_name}_m{m}'] = calculate_dictionary_mean(data[f'als_onto_{sim_name}_m{m}'], ftuserssize)
        data[f'bpr_onto_{sim_name}_m{m}'] = calculate_dictionary_mean(data[f'bpr_onto_{sim_name}_m{m}'], ftuserssize)

    return data    

# ---------------------------------------------------------------------------------------- #

def get_evaluation(
        test_users,
        test_users_size,
        count_cv,
        count_cv_items,
        ratings_test,
        ratings_train_sparse_cf,
        test_items,
        all_ratings,
        original_item_id,
        metric
):
    """
    evaluate the results for all the algorithms and all the metrics, before save it in
    the csv file
    :param test_users:
    :param test_users_size:
    :param count_cv:
    :param count_cv_items:
    :param ratings_test:
    :param ratings_train_sparse_cf:
    :param test_items:
    :param all_ratings:
    :param original_item_id:
    :param metric:
    :return: metrics_dict* for all algorithms (and combinations) and all the metrics
    """

    als= {}
    bpr = {}
    
    model_als = AlternatingLeastSquares(
        factors=150,
        num_threads=cpu_count(),
        use_gpu=False,
        random_state=RANDOM_STATE
    )
    model_bayes = BayesianPersonalizedRanking(
        factors=150,
        num_threads=cpu_count(),
        use_gpu=False,
        random_state=RANDOM_STATE
    )
    model_als.fit(ratings_train_sparse_cf)
    model_bayes.fit(ratings_train_sparse_cf)

    progress = 0
    users_to_remove = 0
    relevant_items_sum = 0

    # to use in onto algorithm
    test_items_onto_id = all_ratings[
        all_ratings.index_item.isin(test_items)
    ].item.unique()

    for t_us in test_users:
        progress += 1
        print(progress, ' of ', test_users_size, "cv ", count_cv, "-", count_cv_items, end="\r")

        # all ratings for user t_us (index_user)
        all_ratings_for_t_us = all_ratings[all_ratings.index_user == t_us]

        # train ratings for user t_us
        train_ratings_for_t_us_cb = all_ratings_for_t_us[
            ~(all_ratings_for_t_us.index_item.isin(ratings_test.index_item))
        ]

        # verify it user has condition to be evaluated, i.e., it has al least one item in the test set
        ratings_test_t_us = all_ratings_for_t_us[
            (all_ratings_for_t_us.index_item.isin(ratings_test.index_item))
        ]
        
        if np.sum(ratings_test_t_us.rating) == 0:
            users_to_remove += 1
            continue

        if len(train_ratings_for_t_us_cb) == 0:
            users_to_remove += 1
            continue

        print("users size: ", test_users_size)
        test_users_size = test_users_size - users_to_remove
        floated_test_users_size = float(test_users_size)

        print("n users removed: ", users_to_remove)

        relevant = get_relevants_by_user(ratings_test_t_us, 0)

        relevant_items_sum += len(relevant)  # just calculating average

        iscore_implicit_als = get_score_by_implicit(model_als, ratings_train_sparse_cf, test_items, t_us)
        iscore_implicit_als = map_system_id_to_original_id(iscore_implicit_als, original_item_id)

        iscore_implicit_bpr = get_score_by_implicit(model_bayes, ratings_train_sparse_cf, test_items, t_us)
        iscore_implicit_bpr = map_system_id_to_original_id(iscore_implicit_bpr, original_item_id)    

        
        als = all_evaluation_metrics(iscore_implicit_als, ratings_test_t_us, test_items,
                                     relevant.index_item, als)
        bpr = all_evaluation_metrics(iscore_implicit_bpr, ratings_test_t_us, test_items,
                                     relevant.index_item, bpr)
        
        als = calculate_dictionary_mean(als, floated_test_users_size)
        bpr = calculate_dictionary_mean(bpr, floated_test_users_size)
        
        iscore_lin, iscore_resnik, iscore_jc = onto_algorithm(
            train_ratings_for_t_us_cb,
            test_items_onto_id,
            metric
        )

        if len(iscore_lin) == 0 or len(iscore_resnik) == 0 or len(iscore_jc) == 0:
            continue

        # Initialize a dictionary to store data
        dict_data = {'sim_lin': {}, 'sim_resnik': {}, 'sim_jc': {}}

        for m in dict_data.keys():
            if m in ('sim_lin', 'all'):
                dict_data[m] = process_sim(dict_data[m], 
                               iscore_lin, 
                               iscore_implicit_als,
                               iscore_implicit_bpr, 
                               original_item_id,
                               ratings_test_t_us,
                               test_items,
                               relevant.index_item,
                               floated_test_users_size,
                               m, 
                               4)
            if m in ('sim_resnik', 'all'):
                dict_data[m] = process_sim(dict_data[m], 
                               iscore_resnik, 
                               iscore_implicit_als,
                               iscore_implicit_bpr, 
                               original_item_id,
                               ratings_test_t_us,
                               test_items,
                               relevant.index_item,
                               floated_test_users_size,
                               m, 
                               4)
            if m in ('sim_jc', 'all'): 
                dict_data[m] = process_sim(dict_data[m], 
                               iscore_jc, 
                               iscore_implicit_als,
                               iscore_implicit_bpr, 
                               original_item_id,
                               ratings_test_t_us,
                               test_items,
                               relevant.index_item,
                               floated_test_users_size,
                               m, 
                               4)

    # Flatten the dictionary
    flattened_dict = {}
    for key, value in dict_data.items():
        flattened_dict.update(value)

    flattened_dict.update({'als': als})
    flattened_dict.update({'bpr': bpr})
    
    # Sort the keys alphabetically
    flattened_dict = {k: v for k, v in sorted(flattened_dict.items())}

    del model_bayes
    del model_als
    gc.collect()

    return flattened_dict


# ---------------------------------------------------------------------------------------- #

def get_score_by_item(test_items_onto_id, train_items_for_t_us):
    
    tablename = '_'.join([config.tablename, config.dataset_folder.split('/')[2]]) 
    sims = get_read_all(test_items_onto_id, train_items_for_t_us,tablename)
    sims_inverse = get_read_all(train_items_for_t_us, test_items_onto_id,tablename)
    if len(sims_inverse) !=0 :
        sims_inverse = sims_inverse.rename(columns={"comp_1": "comp_2", "comp_2": "comp_1"})
    sims_concat = pd.concat([sims, sims_inverse], axis=0, join='outer', ignore_index=True, sort=False)
    
    return sims_concat if len(sims_concat) > 0 else []

# ---------------------------------------------------------------------------------------- #

def merge_algorithms_scores(iscore_ontology, iscore_implicit, metric):
    """
    calculates the scores for each test item with hybrid algorithm
    :param iscore_ontology: item score from CB
    :param iscore_implicit: item score from CF
    :param metric: 1: multiplication of the scores; 2: mean of the scores
    :return: item score dataframe order descending
    """

    merged_item_scores = pd.merge(iscore_implicit, iscore_ontology, on='item')

    if metric == 1:  # 'geometric'
        merged_item_scores['score'] = merged_item_scores.score_x * merged_item_scores.score_y
    elif metric == 2:  # 'arithmetic'
        merged_item_scores['score'] = (merged_item_scores.score_x + merged_item_scores.score_y) / 2
    elif metric == 3:  # 'quadratic'
        merged_item_scores['score'] = np.sqrt(merged_item_scores.score_x ** 2 + merged_item_scores.score_y ** 2) / 2
    elif metric == 4:  # 'harmonic'
        merged_item_scores['score'] = 2 / (1 / merged_item_scores.score_x + 1 / merged_item_scores.score_y)

    return merged_item_scores[
        ['item', 'score', 'item_' + config.item_prefix + 'x']
    ].sort_values(by=['score'], ascending=False)

# ---------------------------------------------------------------------------------------- #

def get_score_by_implicit(model, ratings_sparse, test_items, t_us):
    item_score = recommendations_implicit(model, ratings_sparse, test_items, t_us)
    item_score = DataFrame(np.array(item_score), columns=["item", "score"])
    item_score.item = item_score.item.astype(int)
    return item_score

# ---------------------------------------------------------------------------------------- #

def get_score_by_ontology(test_items_onto_id, train_items_for_t_us):
    scores_by_item = get_score_by_item(test_items_onto_id, train_items_for_t_us)

    sim_metric = config.sim_metric
    item_score = scores_by_item[['comp_1', sim_metric]]
    item_score = item_score.rename(columns={'comp_1': 'item', sim_metric: 'score'})
    item_score.item = item_score.item.astype(int)

    return item_score
