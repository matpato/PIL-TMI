import os
import ssmpy
import sys

from calculate_semantic_similarity_chunks import calculate_semantic_similarity_chunks
from database import check_database, create_table, drop_duplicates
from dataset import upload_dataset, get_items_ids


def calculate_similarity(config, dataset_file):
    # connect db
    check_database()
    
    # read dataset; select the right columns; select items only from ontology
    df_dataset = upload_dataset(
        csv_path=f'{config.dataset_folder}/{dataset_file}',
        name_prefix=config.item_prefix
        )

    # check ontology database
    if not os.path.isfile(config.path_to_ontology):
        print("Database from owl does not exit. Creating...")

        ssmpy.create_semantic_base(
            config.path_to_owl,
            config.path_to_ontology,
            "http://purl.obolibrary.org/obo/",
            "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            ""
        )
    else:
        print("Database ontology file already exists")

    # get item id in the input dataset
    items_ids = get_items_ids(df_dataset, config.item_prefix)
    print("n of ids: ", items_ids.shape)

    ssmpy.semantic_base(config.path_to_ontology)
   
    create_table(
        database = config.database,
        tablename = '_'.join([config.tablename, config.dataset_folder.split('/')[2]]) 
        )
    
    # connection to sqlite database
    conn = ssmpy.create_connection(config.path_to_ontology)

    calculate_semantic_similarity_chunks(
        entry_ids = items_ids,
        db = config.dataset_folder.split('/')[2],
        conn = conn,
        tablename = config.tablename,
        n_split = config.n_split,
        prefix = config.item_prefix
    )

    drop_duplicates('_'.join([config.tablename, config.dataset_folder.split('/')[2]]) )
    # close connection
    conn.close()