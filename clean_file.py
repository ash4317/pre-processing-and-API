from nltk.corpus import stopwords, words
from nltk.stem import PorterStemmer, WordNetLemmatizer
import re
from unidecode import unidecode
import pandas as pd
import numpy as np
import math
import os
import re
import string
import nltk
import csv
import time
from xlsxwriter.workbook import Workbook
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from nltk.tokenize import word_tokenize
from collections import Counter
from pandas import DataFrame
from nltk.corpus import wordnet
from unidecode import unidecode
from csv import writer 
from sklearn.feature_selection import VarianceThreshold
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
#from sknn import ae
import matplotlib.pyplot as plt


MONTHS = ['january', 'february', 'march', 'april', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
NUMBERS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'hundred', 'thousand']
EXTRA_WORDS = ['number', 'month', 'note', 'will']

#To remove newline characters
def rmv_newline_char(text):
    '''
    removes newline character '\n' and non-breaking space '\xa0' from the doc
    '''
    text = text.replace("\n", " ")
    text = text.replace("\xa0", " ")
    return text

#To remove stopwords
def rmv_stopWords(text):
    global NUMBERS, MONTHS, EXTRA_WORDS
    words = stopwords.words('english')
    extra = ["inc", "citigroup", "markets", "price", "would", "without", "follow"]
    words = words + extra + NUMBERS + MONTHS + EXTRA_WORDS
    data = " ".join(w for w in word_tokenize(text) if not w in words and len(w) > 3)
    return data

#Remove non-english words
def unusual_words(text):
    text_vocab = set(w.lower() for w in text.split() if w.isalpha())
    english_vocab = set(w.lower() for w in words.words())
    unusual = text_vocab - english_vocab
    data = " ".join(w for w in sorted(text_vocab - unusual))
    return data

#regex-remove punctuations
def rmv_punct(text):
    punct = list(string.punctuation)
    data = ''.join(i for i in text if i not in string.punctuation)
    return data

#Remove numbers
def rmv_numbers(text):
    data = ''.join(i for i in text if not i.isdigit())
    return data

#function to remove special characters that cannot be removed by RegEx
def rmv_unknown_char(text):
    # unknown_chars_ascii contains ascii values of some special characters that are present in the doc but cannot be removed using regex
    unknown_chars_ascii = [9642, 9618, 8212, 8220, 8221, 8217, 174, 167, 168, 183, 47, 8211, 8226]

    # unknown_chars is a list containing these special characters
    unknown_chars = [chr(x) for x in unknown_chars_ascii]

    for i in unknown_chars:
        # for character with ascii 8212 and 47 should be replaced by a whitespace

        if i == chr(8212) or i == chr(47):
            text = text.replace(i, " ")
        else:
            text = text.replace(i, "")
    return text


#Stemming
def apply_stemming(text):
    stemmer = PorterStemmer()
    data = " ".join(stemmer.stem(w) for w in word_tokenize(text))
    return data

#Lemmatization
def apply_lemmatization(text):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    tokens = [lemmatizer.lemmatize(w, pos = "a") for w in tokens]
    tokens = [lemmatizer.lemmatize(w, pos = "v") for w in tokens]
    data = " ".join(w for w in tokens)
    return data

#Returns document frequency of each word and list of most common and rare words
def get_count(textlist):
    DF = {}
    for text in textlist:
        tokens = word_tokenize(text)
        for w in tokens:
            try:
                DF[w].add(text)
            except:
                DF[w] = {text}

    for i in DF:
        DF[i] = len(DF[i])
    return DF

#Removes words having document frequency = 1 or more than 60%
def rmv_common_words(textlist, DF):
    data = []
    for text in textlist:
        dataitem = " ".join(w for w in word_tokenize(text) if DF[w] < (len(textlist) * (6/10)) and DF[w] != 1)
        data.append(dataitem)
    return data

#To remove URLs
def rmv_URLs(text):
    txt = ""
    words = text.split()
    for word in words:
        if re.search('^www.*', word) or re.search('^us.*', word):
            continue
        txt += word + " "
    txt = txt.strip()
    return txt

#To calculate tfidf
def tfidf(text):
    vectorizer = TfidfVectorizer(smooth_idf=False)
    vectors = vectorizer.fit_transform(text)
    features = vectorizer.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=features)
    return df

#To get reduce features using Variance Threshold. Parameters- tfidf dataframe, threshold
def varThresh_tfidf(tfidf, thresh):
    selector = VarianceThreshold(threshold=thresh) 
    selector.fit(tfidf)
    data = tfidf[tfidf.columns[selector.get_support(indices=True)]]
    #print(data)
    return data

def pca_tfidf(tfidf, n):
    scaler = StandardScaler()
    segmentation_std = scaler.fit_transform(tfidf) 
    pca = PCA(n_components=n)
    scores_pca = pca.fit_transform(segmentation_std)
    df = pd.DataFrame(pca.components_,columns=tfidf.columns)
    #print(df)
    ratio = pca.explained_variance_ratio_
    #print(ratio)
    return ratio, scores_pca, df

#Returns reduced features and document count for each word using VarianceThreshold. Parameters- textlist, threshold
def varThresh_textlist(text, thresh):
    vectorizer = CountVectorizer()
    selector = VarianceThreshold(threshold=thresh)
    vectors = vectorizer.fit_transform(text)
    features = vectorizer.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=features)
    selector.fit(df)
    data = df[df.columns[selector.get_support(indices=True)]]
    return data

#Apply pre-processing
def preprocessing(textdata, steps):
    data = []
    count = 0
    steps = set(steps)
    for text in textdata:
        # will be able to process all characters
        text = unidecode(text)
        text = rmv_newline_char(text)
        text = text.lower()
        #Checking in steps to customize pre-processing task according to user's need
        if 'url' in steps:
            text = rmv_URLs(text)
        text = rmv_numbers(text)
        text = rmv_punct(text)
        text = rmv_unknown_char(text)
        if 'unusual' in steps:
            text = unusual_words(text)
        if 'stopwords' in steps:  
            text = rmv_stopWords(text)
        text = unusual_words(text)  
        if 'lemmatization' in steps:
            text = apply_lemmatization(text)
        if 'stemming' in steps:
            text = apply_stemming(text)
        data.append(text)
        count += 1
        print(f"Preprocessed: {count}")
    DF = get_count(data)
    data = rmv_common_words(data, DF)
    return data
