import re
import clean_file
import urllib3
import urllib.request, urllib.error, urllib.parse
import math
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
import string
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import punkt
from nltk.stem.porter import PorterStemmer
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import DBSCAN

def file_names_paths(paths, names, extension):
    path = 'file:///' + os.getcwd().replace('\\', '/') + '/ISIN_HTML/'
    for i in range(len(names)):
        paths.append(path + extension + names[i] + '.htm')
    return paths



def fetch_and_pre_process(url):
  data = urllib.request.urlopen(url).read().decode()
  soup = BeautifulSoup(data, "html.parser")
  corpus = soup.get_text()
  corpus = clean_file.text_cleaning(corpus)
 
  return corpus

files = []

# these lists will contain all the file paths
bullet_participation_files = list()
interest_rates_files = list()
snowball_files = list()

# these lists will contain all the .htm file names
print("Getting file names from Bullet_Participation ...")
bullet_participation = [y.replace('.htm', '') for y in [x for x in os.walk(os.getcwd() + '/ISIN_HTML/Bullet_Participation/')][0][2]]
print("Getting file names from Interest_Rates ...")
interest_rates = [y.replace('.htm', '') for y in [x for x in os.walk(os.getcwd() + '/ISIN_HTML/Interest_Rates/')][0][2]]
print("Getting file names from Snowball ...")
snowball = [y.replace('.htm', '') for y in [x for x in os.walk(os.getcwd() + '/ISIN_HTML/Snowball/')][0][2]]
# these lists will contain all the .htm file names
print("Getting file paths from Bullet_Participation ...")
bullet_participation_files = file_names_paths(bullet_participation_files, bullet_participation, 'Bullet_Participation/')
print("Getting file paths from Interest_Rates ...")
snowball_files = file_names_paths(snowball_files, snowball, 'Snowball/')
print("Getting file paths from Snowball ...")
interest_rates_files = file_names_paths(interest_rates_files, interest_rates, 'Interest_Rates/')

for file in bullet_participation_files:
    files.append(file)
for file in interest_rates_files:
    files.append(file)
for file in snowball_files:
    files.append(file)

url_list = files
doc_list=[]

for x in url_list:
  doc_list.append(fetch_and_pre_process(x))
    
#Count Vectoriser then tidf transformer


vectorizer = CountVectorizer()
X = vectorizer.fit_transform(doc_list)

#vectorizer.get_feature_names()

#print(X.toarray())     


transformer = TfidfTransformer(smooth_idf=False)
tfidf = transformer.fit_transform(X)
print("\n")
print("tfidf matrix shape:")
print(tfidf.shape) 



db = DBSCAN(eps=0.18, min_samples=3, metric='cosine').fit(tfidf)
clusters_3 = db.labels_.tolist()

idea_3={'Idea':doc_list, 'Cluster':clusters_3} #Creating dict having doc with the corresponding cluster number.
frame_3=pd.DataFrame(idea_3,index=[clusters_3], columns=['Idea','Cluster']) # Converting it into a dataframe.

print("\n")
print(frame_3['Cluster'].value_counts()) #Print the counts of doc belonging to each cluster.
print("\n")
print("Cluster number of every document:")
print(clusters_3)
