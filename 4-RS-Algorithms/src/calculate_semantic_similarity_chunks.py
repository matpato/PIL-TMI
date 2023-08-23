import ssmpy
import numpy as np
import pandas as pd
from database import get_read_all, save_to_mysql
from dataset import confirm_all_test_train_similarities

def calculate_semantic_similarity_chunks(entry_ids, db, conn, tablename, n_split, prefix):
    """

    :param entry_ids: list of entries ids
    :param conn: connection object to sqlite
    :param tablename: name of the table where the data are saved
    :param n_split: number to split the list of entities
    :param n_split: int
    :param prefix: Prefix of the concepts to be extracted from the ontology
    :type prefix: string
    :return:
    """
    import time

    items_splitted  = np.array_split(np.array(entry_ids), n_split)
    
    aux_array = np.arange(0, n_split, 1)

    for i in aux_array:
        for n in aux_array:
            print(i, n)
            
            list_1 = items_splitted[i].tolist()
            list_2 = items_splitted[n].tolist()

            list_of_sims_from_db = get_read_all(list_1, list_2, '_'.join([tablename,db]))

            list_1, list_2 = confirm_all_test_train_similarities(list_1, list_2, list_of_sims_from_db)

            if len(list_1) | len(list_2) == 0:
                continue

            list_1 = [prefix + str(s) for s in list_1]
            list_2 = [prefix + str(s) for s in list_2]

            results = ssmpy.light_similarity(conn, list_1, list_2, 'all', 20)
            newlist = [item for items in results for item in items]
            sim_df = pd.DataFrame(newlist, columns=["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"])
            sim_df = sim_df[sim_df.comp_1 != sim_df.comp_2]    
            
            save_to_mysql( sim_df.drop_duplicates(['comp_1','comp_2'], keep='first'), '_'.join([tablename,db]), prefix)
            time.sleep(.25)                          
            print("save in mysql database")
        
        mask = np.where(aux_array == i)
        aux_array = np.delete(aux_array, mask)