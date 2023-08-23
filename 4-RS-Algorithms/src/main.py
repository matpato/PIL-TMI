import os
import numpy as np
import sys
from myconfiguration import MyConfiguration as Config
from calculate_similarity import calculate_similarity
from evaluate import evaluate_dataset
from datetime import datetime
from utils import save_metadata

np.random.seed(42)

def main():
    start_time = datetime.now()

    config: Config = Config.get_instance()

    df_ds = config.dataset_folder

    for dataset_file in os.listdir(df_ds):
        print(f"Dataset file: {dataset_file}")
        # calculate similarity and save it in mysql database
        calculate_similarity(config,dataset_file)
        evaluate_dataset(config, dataset_file)

    # ---------------------------------------------------------------------------------------- #
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Run: python3 RS-Algorithms.py \n \
                Date: {datetime.now()} \n  \
                Duration: {datetime.now() - start_time} \n\
                Database: {config.database} \nDataset: {config.dataset_folder}\n\
                Ontologies: {config.item_prefix}\n\
                '
    save_metadata(config.path2info, metadata) 
    print("FINISHED!")
if __name__ == '__main__':
    main()
