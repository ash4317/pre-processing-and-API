'''
Run the file through terminal as: python main.py 50 - This will run the program for 50 URLs.
This file along with 'clean_file.py' and the directory with the excel file 'ISINS.xlsx' should be in the same directory.
This code reads and extract all the data from the .htm URLs present in the excel sheet and preprocesses it, calculates TFIDF matrix and makes clusters using DBSCAN algorithm.
'''

# User-Developed Modules
import clean_file as cf
import preprocessing as prep
import cluster

# Inbuilt modules for extracting data
import sys
import shutil
import json
import os
import pandas as pd


def get_links():
    '''
    Function that will return list of URLs of all the .htm files in a list.
    '''
    # function that takes no. of docs to be parsed as input.
    no_of_docs = int(sys.argv[1])
    
    # will store all the URLs to be parsed
    links = list()

    # defining path of the excel sheet
    file_path = os.getcwd().replace('\\', '/') + '/ISINS_Dataset/ISINS.xlsx'

    # object to read the excel sheet
    df = pd.read_excel(file_path, sheet_name=0)
    links = df['Termsheet Link'].tolist()

    # validation check
    if no_of_docs > len(links):
        sys.exit("No. of docs exceeds limit.")
    return links[:no_of_docs]



def removeCache():
    '''
    Removes cache file generated due to this code
    '''
    try:
        shutil.rmtree("__pycache__")
    except:
        pass


#-------------------------------------------------------------------MAIN FUNCTION---------------------------------------------------------------------------------------


if __name__ == "__main__":
    '''
    Main function
    '''

    # words_in_docs stores number of docs where every distinct word appears
    # word_list stores all the preprocessed data from all docs
    # common_words stores all words which appear very frequently or very rarely
    words_in_docs = dict()
    word_list = list()
    common_words = list()
    links = list()


    # get all the preprocessed text and no. of docs where words appear
    links = get_links()
    words_in_docs, word_list, links = prep.clean_all_files(links, words_in_docs, word_list)

    # get all common words from the preprocessed text (present in more than 80% of total docs or less than 2 docs)
    common_words = prep.get_commonWords(words_in_docs, int(sys.argv[1]))

    # remove common words
    word_list = cf.rmv_commonWords(word_list, common_words)
    
    # writing preprocessed text to the file 'preprocessed.json'
    prep.write_preprocessed(word_list)

    '''
    Calculate TFIDF matrix for the preprocessed text
    '''
    tfidf = cluster.calc_TFIDF(word_list, 0.05)

    # evaluate clusters with given epsilon and min_sample values
    cluster.eval_clusters(tfidf, word_list, links, epsilon=0.18, minSamples=3)
    '''
    cluster.eval_clusters(tfidf, word_list, links, epsilon=0.3, minSamples=5)
    cluster.eval_clusters(tfidf, word_list, links, epsilon=0.2, minSamples=1)
    cluster.eval_clusters(tfidf, word_list, links, epsilon=0.1, minSamples=5)
    cluster.eval_clusters(tfidf, word_list, links, epsilon=0.35, minSamples=1)
    '''
    # to remove useless cache data
    removeCache()