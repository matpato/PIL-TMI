import pandas as pd
import ssmpy
import mysql.connector as connector
from sqlalchemy import create_engine
import sqlite3
from sqlite3 import Error
from myconfiguration import MyConfiguration as Config


def create_default_connection_mysql():
    """
    create a default connection to the mysql database
        specified by host, user and password defined in configurations.ini
    :param
    :return: Connection object
    """
    conf = Config.get_instance()
    mydb = connector.connect(
        host=conf.host,
        user=conf.user,
        password=conf.password,
        # ssl_disabled=True,
    )
    return mydb

# ---------------------------------------------------------------------------------------- #

def create_connection_mysql():
    """ create a connection to the mysql database
       specified by host, user, password and
       database name defined in configurations.ini
   :param
   :return: Connection object
   """
    mydb = create_default_connection_mysql()
    mydb.database = Config.get_instance().database

    return mydb

# ---------------------------------------------------------------------------------------- #

def create_engine_mysql():
    """
    Create a pool and dialect together connection to provide a source of database
    and behavior
    :param:
    :return: Connection engine
    """
    # in case of connection error, change the host as in the next commented code
    conf = Config.get_instance()
    host = conf.host
    user = conf.user
    password = conf.password
    db_name = conf.database

    return create_engine(
        "mysql+pymysql://{user}:{pw}@{host}/{db}".format(
            user=user,
            pw=password,
            host=host,
            db=db_name
        ),
        pool_pre_ping=True
    )

# ---------------------------------------------------------------------------------------- #

def check_database():
    """
    check the existence of a database with the name defined in configurations.ini
    if none, a new is created as well as a table of similarity
    :param: none
    :return:
    """
    
    global mydb
    try:
        check = False
        mydb = create_default_connection_mysql()

        mycursor = mydb.cursor()

        db_name = Config.get_instance().database

        mycursor.execute( "SHOW DATABASES" )
        for x in mycursor:

            if x[0].decode( "unicode-escape" ) == db_name:  #scratchy
            # or,
            # if x[0].encode().decode( 'utf-8' ) == db_name: #chronos
                check = True

        if not check:
            print( "Will create database" )
            mycursor.execute( "CREATE DATABASE " + db_name )
            #create_table(tablename)
        else:
            print( "Database already exists" )

    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

# ---------------------------------------------------------------------------------------- #

def create_table(database: str, tablename: str):
    """
    create a table named similarity with id, comp_1, comp_2,
        sim_resnik, sim_lin, sim_jc as columns in mysql
    :param: none
    :return:
    """
    global mydb    
    try:
        mydb = create_connection_mysql()
        my_cursor = mydb.cursor()

        my_cursor.execute(f'use {database};')
        my_cursor.execute( "SET FOREIGN_KEY_CHECKS = 0" )
        my_cursor.execute( f"DROP TABLE IF EXISTS `{tablename}`" )

        my_cursor.execute(
            f"create table `{tablename}` ( "
            "`id` int not null auto_increment, "
            "`comp_1` int not null, "
            "`comp_2` int not null, "
            "`sim_resnik` float not null, "
            "`sim_lin` float not null, "
            "`sim_jc` float not null, "
            "primary key (`id`), "
            "index sim (`comp_1`,`comp_2`) "
            ") ENGINE = InnoDB"
        )

        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    except Exception as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            my_cursor.close()
            mydb.close()

# ---------------------------------------------------------------------------------------- #

def get_read_all(entry_ids_1, entry_ids_2, tablename):
    """
    Return all columns from database between 2 list of entries
    :param entry_ids_1: list of entries 1
    :param entry_ids_2: list of entries 2
    :return result: pandas Dataframe
    """
    global mydb
    if isinstance(entry_ids_1, list):
        list1 = entry_ids_1
    else:  
        list1 = entry_ids_1.tolist()
    if isinstance(entry_ids_2, list):
        list2 = entry_ids_2
    else:  
        list2 = entry_ids_2.tolist()
    
    try:
        mydb = create_connection_mysql()
        
        str1 = ','.join(['%s'] * len(list1))
        str2 = ','.join(['%s'] * len(list2))
        sql = "select * from " + tablename + " where comp_1 in (%s) and comp_2 in (%s);"
        str1 = str1 % tuple(list1)
        str2 = str2 % tuple(list2)
        sql = sql % (str1, str2)   
        return pd.read_sql_query(sql, con=mydb)
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb is not None and mydb.is_connected():
            mydb.close()

# ---------------------------------------------------------------------------------------- #

def save_to_mysql(df, tablename, prefix=None):
    """
    :param df: pandas DataFrame
    :param engine: connection to engine object
    :param tablename: name of the table where the data are saved
    :param prefix: Prefix of the concepts to be extracted from the ontology
    :type prefix: string
    """
    global mydb
    try: 
        host=Config.get_instance().host
        user=Config.get_instance().user
        passwd=Config.get_instance().password
        db_name = Config.get_instance().database
        
        engine = create_engine( "mysql+pymysql://{user}:{pw}@{host}/{db}"
                                .format( user=user,
                                            pw=passwd,
                                            host=host,
                                            db=db_name ),
                                pool_pre_ping=True )

        con = engine.connect()
        df.comp_1 = df.comp_1.map(lambda x: x.lstrip(prefix)).astype(int)
        df.comp_2 = df.comp_2.map(lambda x: x.lstrip(prefix)).astype(int)

        df.to_sql(tablename, con=con, if_exists='append', index=False, method='multi', chunksize=10000)
        print('end save values')
    except Error as e:
        print( "Error while connecting to MySQL", e )

# ---------------------------------------------------------------------------------------- #

def drop_duplicates(tablename):
    """
    Drop duplicates from table
    :param tablename: name of the table saved in mysql
    """
    global mydb
    try:
        # Open database connection
        mydb = create_connection_mysql()
        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()
        
        # Prepare SQL query to read a record into the database.        
        sql = f"delete t1 from {tablename} t1 inner join {tablename} t2 \
            where t1.id < t2.id and t1.comp_1 = t2.comp_1 and t1.comp_2 = t2.comp_2;"
        mycursor.execute( sql )
        print( f"Duplicated from {tablename} were removed" )
    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()