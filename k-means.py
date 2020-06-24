from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import math
import os
import re
import string
import pickle
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from nltk.tokenize import word_tokenize
from collections import Counter
from pandas import DataFrame
from nltk.corpus import wordnet
from unidecode import unidecode

#To remove punctuations and special characters
def removepunct(my_str):
    punctuations = '''+*=/!()-[]\.“”–—Â¨—â€¢®×▪©{};§:'"\,<>.·/?@#$%^&*_~'''
    no_punct = ""
    for char in my_str:
        if char not in punctuations:
            no_punct = no_punct + char
    return no_punct

#To extract data from all documents of required directory
def scrapdir(dname):
    entries = os.listdir(dname)
    textdict = {}
    flist = []
    for entry in entries:
        fname = os.path.join(dname, entry)
        f = open(fname)
        soup = BeautifulSoup(f, 'html.parser')
        f.close()
        flist.append(entry)
        data = soup.findAll("text")
        str_cells = str(data)
        cleartext = BeautifulSoup(str_cells, "html.parser").get_text()
        textdict[entry] = cleartext
    return textdict, flist

#To extract data from all documents 
def scrapall():
    cwd = os.getcwd()
    entries = os.listdir(cwd)
    textdict = {}
    flist = []
    for entry in entries:
        if os.path.isdir(entry):
            subdir = os.listdir(entry)
            for files in subdir:
                fname = os.path.join(entry, files)
                f = open(fname)
                soup = BeautifulSoup(f, 'html.parser')
                f.close()
                flist.append(files)
                data = soup.findAll("text")
                str_cells = str(data)
                cleartext = BeautifulSoup(str_cells, "html.parser").get_text()
                textdict[files] = cleartext
    return textdict, flist

#To perform cleaning, tokenization and stemming of data
def preprocess(textdict):
    stemmer = SnowballStemmer('english')
    words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer() 
    cleandict = {}
    datadict = {}
    for text in textdict:
        data = str(textdict[text])
        data = data.lower()
        data = ''.join(i for i in data if not i.isdigit())
        data = removepunct(data)
        data = unidecode(data)
        tokens = word_tokenize(data)
        tokens = [lemmatizer.lemmatize(w) for w in tokens if not w in words]
        tokens = [lemmatizer.lemmatize(w, pos = "a") for w in tokens if not w in words]
        tokens = [lemmatizer.lemmatize(w, pos = "v") for w in tokens if not w in words]
        cleandict[text] = [stemmer.stem(w) for w in tokens  if not w in words and len(stemmer.stem(w)) > 1 ]
        datadict[text] = ' '.join([str(elem) for elem in cleandict[text]]) 
    df = DataFrame(list(datadict.items()),columns = ['Document name','Pre-processed data'])
    #df = DataFrame(list(cleandict.items()),columns = ['Document name','Pre-processed data'])
    return cleandict, datadict, df


def tfidf(datadict):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(datadict[ls] for ls in datadict)
    features = vectorizer.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=features)
    return df

def dbscan(tfidf, flist):
    x = 0.30
    y = 5
    db = DBSCAN(eps=x, min_samples=y, metric='euclidean').fit(tfidf)
    clusters = db.labels_.tolist()

    labeling={'Idea':flist, 'Cluster':clusters} #Creating dict having doc with the corresponding cluster number.
    frame=pd.DataFrame(labeling,index=[clusters], columns=['Cluster']) # Converting it into a dataframe.
    print(x," ",y)
    print("\n")
    print(frame['Cluster'].value_counts()) #Print the counts of doc belonging to each cluster.
    return frame

def kmeans(tfidf, flist):
    k = 10
    kmeans = KMeans(n_clusters=k, random_state=0).fit(tfidf)
    clusters = kmeans.labels_.tolist()
    frame = pd.DataFrame(clusters, columns=['Cluster'])
    print(k)
    print("\n")
    print(frame['Cluster'].value_counts()) #Print the counts of doc belonging to each cluster.
    return frame



#Process all folders
#textdict, flist = scrapdir('Interest Rates')
textdict, flist = scrapall()
dictn, datadict, pdf = preprocess(textdict)
df = tfidf(datadict)
print(df.shape)
cdf = kmeans(df, flist)
#cdf.to_csv("kmeans_all.csv")



textdict, flist = scrapdir('Interest Rates')
#textdict, flist = scrapall()
dictn, datadict, pdf = preprocess(textdict)
df = tfidf(datadict)
print(df.shape)
cdf = kmeans(df, flist)
#cdf.to_csv("kmeans_Interest_Rates.csv")



textdict, flist = scrapdir('Bullet Participation')
#textdict, flist = scrapall()
dictn, datadict, pdf = preprocess(textdict)
df = tfidf(datadict)
print(df.shape)
cdf = kmeans(df, flist)
#cdf.to_csv("kmeans_Bullet Participation.csv")



textdict, flist = scrapdir('Snowball')
#textdict, flist = scrapall()
dictn, datadict, pdf = preprocess(textdict)
df = tfidf(datadict)
print(df.shape)
cdf = kmeans(df, flist)
#cdf.to_csv("kmeans_kmeans_Snowball.csv")

