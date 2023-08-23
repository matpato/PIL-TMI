# RS-Algorithms with similarity calculations

This framework is based on a Hybrid Semantic Recommender Algorithm for Chemical Compounds. 
It tests several recommender algorithms:  

* ALS (https://implicit.readthedocs.io/en/latest/quickstart.html)
* BPR (https://implicit.readthedocs.io/en/latest/quickstart.html)
* ONTO (three semantic similarity metrics)
* ALS_ONTO
* BPR_ONTO 

[Hybrid Semantic Recommender System for Chemical Compounds](https://link.springer.com/chapter/10.1007/978-3-030-45442-5_12)
 

## Requirements:
* Python > 3.5
* mySQL
* check requirements.txt


## Input:

1 -  csv with a dataset with the format of <user,item,rating>, where the items are Chemical Compounds in the ChEBI ontology and users are Disease ontology.

    * These files may be found in datasets folder
        


2 - mySQL DB with the compounds similarities:

sudo docker run --detach --name=sim-mysql --env="MYSQL_ROOT_PASSWORD=1234" --publish 6603:3306 --volume=<path>/db_mysql:/var/lib/mysql mysql

sudo docker inspect sim-mysql | grep IPAddress

sudo docker exec -it sim-mysql bash

mysql --host=<host> --user=root --password=1234 entities_sim_med2care_rs

```
CREATE DATABASE entities_sim_med2care_rs;
USE entities_sim_med2care_rs;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `similarity`;
CREATE TABLE `similarity` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `comp_1` INT NOT NULL,
  `comp_2` INT NOT NULL,
  `sim_resnik` FLOAT NOT NULL,
  `sim_lin` FLOAT NOT NULL,
  `sim_jc` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX sim (`comp_1`,`comp_2`) 
) ENGINE=InnoDB;


SET FOREIGN_KEY_CHECKS = 1;

exit database
```


## Run:

* The first thing to do is to change the config.ini file. 
* Second you should run the file main.py in the src folder. 

* The output will be a set of CSV files with the results for all the algorithms tested with the evaluation metrics:
    * Precision
    * Recall
    * Mean Reciprocal Rank
    * nDCG
    
    
If you wish to use a docker container, here we have an example of how to run:

./docker.sh rs_eval <path_input_data>  sim-mysql

# create similarity database and execute recommender system algorithms, plus metrics
python3 main.py

# to create heatmaps 

pyhton3 heatmaps.py

The results are saved as CSV files in the folder corresponding to data/results



