###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#  (Adapted from Márcia Barros, Pedro Ruas, Diana Sousa)                      #  
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author:   )                                                              # 
#                                                                             #   
#                                                                             #  
###############################################################################

import os
import urllib.request
import requests
import shutil
from pathlib import Path
import rdflib
from rdflib import URIRef
from bioservices import ChEBI
from .myconfiguration import MyConfiguration as cfg


# --------------------------------------------------------------------------- #

def get_owl_path(entity):
    config = cfg.get_instance()
    if entity == 'doid':
        return config.path_owl_doid
    elif entity == 'chebi':
        return config.path_owl_chebi
    return ''


# --------------------------------------------------------------------------- #

def get_db_path(entity):
    config = cfg.get_instance()
    if entity == 'doid':
        return config.path_db_doid
    elif entity == 'chebi':
        return config.path_db_chebi
    return ''


# --------------------------------------------------------------------------- #

def get_owl(url, path):
    """
    Download owl file and save it in a pre-defined folder. If <path>
    does not exist script will create it in current working directory and save
    file in it
    This is written specially to large file. The chunk size that we want to
    download at a time is specified
    :param url: url of the ontology
           path: folder where owl will be save
    """
    # create folder if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(path, filename)

    print(f'Downloading ... {filename}')

    if url.startswith('ftp'):
        with urllib.request.urlopen(url) as r:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(r, f)
    else:
        r = requests.get(url, stream=True)
        if r.ok:
            with open(file_path, "wb") as owl:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        owl.write(chunk)
                        owl.flush()
                        os.fsync(owl.fileno())
        else:  # HTTP status code 4XX/5XX
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))


def loading_items(is_chebi=False, is_doid=False, is_go=False, is_hp=False):
    """
    Loading ontologies to get the entities label
    :param is_chebi, Indicates ontology must be loaded
    :param is_doid, Indicates ontology must be loaded
    :param is_go, Indicates ontology must be loaded
    :param is_hp: Indicates ontology must be loaded
    :return chebi, do, go, hp: owl graph
    """

    if is_chebi and not os.path.exists(get_owl_path('chebi')):
        url = "http://purl.obolibrary.org/obo/chebi/chebi_lite.owl"
        # "ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl"
        get_owl(url, path=os.path.dirname(get_owl_path('chebi')))

    # if doid.owl does not exist
    if is_doid and not os.path.exists(get_owl_path('doid')):
        url = " http://purl.obolibrary.org/obo/doid.owl"
        get_owl(url, path=os.path.dirname(get_owl_path('do')))


    # create a Graph
    chebi = doid = go = hp = rdflib.Graph()
    if is_chebi:
        print('Loading ... chebi')
        chebi = load_ontology(path=get_owl_path('chebi'))
    if is_doid:
        print('Loading ... doid')
        doid = load_ontology(path=get_owl_path('doid'))

    return chebi, doid


# --------------------------------------------------------------------------- #

def load_ontology(path):
    g = rdflib.Graph()
    g.parse(path)
    return g


def get_id(entity_uri, onto):
    # Extract the numeric part after "CHEBI_" or "DOID_" from the entity URI
    ids = []
    for id in entity_uri:
        ids.append(id.split('http://purl.obolibrary.org/obo/')[1])
    return ids


# --------------------------------------------------------------------------- #

def get_primary_ids(lst, prefix_onto):
    '''
    Get entities ids from http://purl.obolibrary.org/obo/ based on items prefix
    :param  lst: list of entities
            chebi: items prefix of entities
    :return label: list of primary chebi ids
    '''
    ids = []
    for id in lst:
        uri = URIRef('http://purl.obolibrary.org/obo/' + id)
        lab = prefix_onto.label(uri)
        # print(lab)
        if not lab:
            ch = ChEBI()
            try:
                res = ch.getCompleteEntity(id.replace('_', ':'))
                if res:
                    id = res.chebiId
                    id = id.replace(':', '_')
                    ids.append(id)
            except:
                print(" Error ")
            finally:
                print(f'Invalid, obsolete or deleted entity')
        else:
            ids.append(id)
    return ids


def get_entities_labels(lst, prefix_chebi, prefix_doid, prefix_go, prefix_hp):
    """
    Get entities lables from http://purl.obolibrary.org/obo/ based on items prefix
    :param  lst: list of entities
            chebi, doid, go, hp: items prefix of entities
    :return label: entities label
    """
    label = []
    for id in lst:
        uri = URIRef('http://purl.obolibrary.org/obo/' + id)
        if id.startswith('CHEBI'):
            lab = prefix_chebi.label(uri)
            if not lab:
                ch = ChEBI()
                try:
                    res = ch.getCompleteEntity(id.replace('_', ':'))
                    if res:
                        lab = res.chebiAsciiName
                except:
                    print(" Error ")
                finally:
                    print(f'Invalid, obsolete or deleted entity')
        elif id.startswith('GO'):
            lab = prefix_go.label(uri)
        elif id.startswith('HP'):
            lab = prefix_hp.label(uri)
        elif id.startswith('DOID'):
            lab = prefix_doid.label(uri)
        else:
            continue
        label.append(lab)
    return label
