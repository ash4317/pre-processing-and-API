import clean_file
import sys
import os
from bs4 import BeautifulSoup as bs
from urllib import request, parse, error
import xlrd
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.cluster import DBSCAN
from sklearn import metrics


def get_files(links):
    '''
    Function that will return list of URLs of all the .htm files in a list
    '''

    # defining path of the excel sheet
    file_path = os.getcwd().replace('\\', '/') + '/ISINS_Dataset/ISINS.xlsx'

    # wb = excel workbook object. Row starts from index 0
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)

    for i in range(1, 2830 + 1):
        links.append(sheet.cell_value(i, 1))
    return links


def get_words(text, words_in_docs, fhand):
    all_words = dict()
    text = text.split()
    for word in text:
        fhand.write(word + " ")
        all_words[word] = all_words.get(word, 0) + 1
    
    for word in all_words.keys():
        words_in_docs[word] = words_in_docs.get(word, 0) + 1
    return words_in_docs



def clean_all_files(links, words_in_docs, commonWords, word_list):
    '''
    This function will return a list consisting of all the words in all the cleaned files.
    '''
    count = 0
    try:
        os.remove("preprocessed.txt")
    except:
        pass

    f = open("preprocessed.txt", 'a')

    for url in links:

        # using beautiful soup to parse the .htm files
        try:
            data = request.urlopen(url).read().decode()
        except:
            continue
            
        soup = bs(data, "html.parser")
        text = soup.text
        text = clean_file.text_cleaning(text, commonWords)
        word_list.append(text)
        words_in_docs = get_words(text, words_in_docs, f)
        count += 1
        print(f"URLs checked: {count}")
    
    f.close()
    return words_in_docs, word_list


def load():
    f = open("common_words.txt")
    data = f.read().strip().split('\n')
    return data

def eval_clusters(tfidf, word_list, epsilon, minSamples):
    db = DBSCAN(eps=epsilon, min_samples=minSamples, metric='cosine').fit(tfidf)
    clusters = db.labels_.tolist()
    labels = db.labels_

    idea_3={'Idea':word_list, 'Cluster':clusters} #Creating dict having doc with the corresponding cluster number.
    frame_3=pd.DataFrame(idea_3,index=[clusters], columns=['Idea','Cluster']) # Converting it into a dataframe.

    print("\n")
    print(f"For epsilon:{epsilon}, minSamples:{minSamples}")
    print(frame_3['Cluster'].value_counts()) #Print the counts of doc belonging to each cluster.
    print("\n")
    print(f"Silhouette Coefficient: {metrics.silhouette_score(tfidf, labels)}")


if __name__ == "__main__":
    '''
    Main function
    '''

    # get all the links
    links = list()
    words_in_docs = dict()
    word_list = list()
    links = get_files(links)


    # get all the text
    words_in_docs, word_list = clean_all_files(links, words_in_docs, load(), word_list)
        

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(word_list)
    Y = vectorizer.get_feature_names()

    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(X)
    print("\n")
    print("tfidf matrix shape:")
    print(tfidf.shape)

    eval_clusters(tfidf, word_list, epsilon=0.18, minSamples=3)
    eval_clusters(tfidf, word_list, epsilon=0.3, minSamples=5)
    eval_clusters(tfidf, word_list, epsilon=0.2, minSamples=10)
    eval_clusters(tfidf, word_list, epsilon=0.1, minSamples=5)
    eval_clusters(tfidf, word_list, epsilon=0.35, minSamples=10)
    print(f"No. of features:{len(Y)}")
