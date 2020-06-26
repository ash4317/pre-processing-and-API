'''
Run the file through terminal as: python main.py 50 - This will run the program for 50 URLs.
This file along with 'clean_file.py' and the directory with the excel file 'ISINS.xlsx' should be in the same directory.
This code reads and extract all the data from the .htm URLs present in the excel sheet and preprocesses it, calculates TFIDF matrix and makes clusters using DBSCAN algorithm.
'''

# User-Developed Modules
import clean_file as cf

# Inbuilt modules for extracting data
import sys
import shutil
import json
import os
from bs4 import BeautifulSoup as bs
from urllib import request, parse, error
from unidecode import unidecode

# Modules for Clustering
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import VarianceThreshold
from sklearn.cluster import DBSCAN
from sklearn import metrics


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


def get_words(text, words_in_docs):
    '''
    Returns all the distinct words present along with number of docs in which they appear.
    '''
    all_words = dict()
    text = text.split()
    for word in text:
        all_words[word] = all_words.get(word, 0) + 1
    
    # This loop checks for all the distinct words stored in the dictionary 'all_words' and will increment count by 1 which will measure the number of docs where word appears.
    for word in all_words.keys():
        words_in_docs[word] = words_in_docs.get(word, 0) + 1
    return words_in_docs



def clean_all_files(links, words_in_docs, word_list):
    '''
    This function will return a list consisting of all the words in all the cleaned files.
    '''
    # keeps count of number of URLs processed.
    count = 0

    for url in links:

        # using beautiful soup to parse the .htm files
        # using error check because all files may not be able to get parsed
        try:
            data = request.urlopen(url).read().decode()
        except:
            continue
            
        soup = bs(data, "html.parser")
        text = soup.text

        # returns preprocessed text.
        text = unidecode(text)
        text = cf.rmv_newline_char(text)
        text = text.lower()
        text = cf.rmv_punctAndNos(text)
        text = cf.rmv_unknown_char(text)
        text = cf.rmv_unusual_words(text)
        text = cf.lemmatize(text)
        text = cf.stemming(text)
        text = cf.rmv_stopWords(text.split())
        text = cf.rmv_URLs(text)

        # Preprocessed text in every .htm file is added to the list 'word_list'
        word_list.append(text)

        # returns the number of docs in which words appear
        words_in_docs = get_words(text, words_in_docs)
        count += 1
        print(f"URLs checked: {count}")
    
    return words_in_docs, word_list


def write_preprocessed(word_list):
    '''
    Writes the preprocessed data into the file 'preprocessed.json'
    '''
    f = open("preprocessed-1.json", 'w')
    js = json.dumps(word_list)
    f.write(js)
    f.close()
    


def get_commonWords(words_in_docs, no_of_docs):
    '''
    Returns all words which are present in more than 80% of total docs and less than 3 docs
    '''
    return [word for word, count in words_in_docs.items() if count > (0.7 * no_of_docs) or count <= 2]



def calc_TFIDF(word_list, threshold):

    # object to transform words into vectors
    vectorizer = CountVectorizer()

    # for applying variance thrshold to reduce features
    selector = VarianceThreshold(threshold=threshold)

    '''
    Transform into TFIDF matrix, apply variance threshold to reduce features,
    print the order of TFIDF matrix and return the TFIDF matrix
    '''
    X = vectorizer.fit_transform(word_list)
    X = selector.fit_transform(X)
    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(X)
    print("\n")
    print(f"TFIDF matrix order: {tfidf.shape}")
    return tfidf


def eval_clusters(tfidf, word_list, epsilon, minSamples):
    '''
    This function applies DBSCAN clustering algorithm and prints clusters, number of features and Silhouette coefficient
    '''
    db = DBSCAN(eps=epsilon, min_samples=minSamples, metric='cosine').fit(tfidf)

    # get all clusters and clusters labels
    clusters = db.labels_.tolist()
    labels = db.labels_

    #Creating dictionary having doc with the corresponding cluster number.
    idea_3={'Idea':word_list, 'Cluster':clusters}

    # Converting it into a dataframe.
    frame_3=pd.DataFrame(idea_3,index=[clusters], columns=['Idea','Cluster'])

    print("\n")
    print(f"For epsilon:{epsilon}, minSamples:{minSamples}")

    #Print the counts of doc belonging to each cluster.
    print(frame_3['Cluster'].value_counts())
    print("\n")

    # Print the Silhouette Coefficient
    print(f"Silhouette Coefficient: {metrics.silhouette_score(tfidf, labels)}")


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


    # get all the preprocessed text and no. of docs where words appear
    words_in_docs, word_list = clean_all_files(get_links(), words_in_docs, word_list)

    # get all common words from the preprocessed text (present in more than 80% of total docs or less than 2 docs)
    common_words = get_commonWords(words_in_docs, int(sys.argv[1]))

    # remove common words
    word_list = cf.rmv_commonWords(word_list, common_words)
    
    # writing preprocessed text to the file 'preprocessed.json'
    write_preprocessed(word_list)

    '''
    Calculate TFIDF matrix for the preprocessed text
    '''
    tfidf = calc_TFIDF(word_list, 0.05)

    # evaluate clusters with given epsilon and min_sample values
    eval_clusters(tfidf, word_list, epsilon=0.18, minSamples=3)
    eval_clusters(tfidf, word_list, epsilon=0.3, minSamples=5)
    eval_clusters(tfidf, word_list, epsilon=0.2, minSamples=10)
    eval_clusters(tfidf, word_list, epsilon=0.1, minSamples=5)
    eval_clusters(tfidf, word_list, epsilon=0.35, minSamples=10)

    # to remove useless cache data
    removeCache()