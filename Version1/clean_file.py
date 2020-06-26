# module for text cleaning

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
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from collections import Counter
from pandas import DataFrame
from nltk.corpus import wordnet
from unidecode import unidecode
from csv import writer 

MONTHS = ['january', 'february', 'march', 'april', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
NUMBERS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'hundred', 'thousand']
EXTRA_WORDS = ['number', 'month', 'note', 'will']

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
    data = " ".join(w for w in word_tokenize(text) if not w in words or len(w) > 3)
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


def rmv_unknown_char(text):
    '''
    function to remove special characters that cannot be removed by RegEx
    '''
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
    data = []
    for text in textlist:
        tokens = word_tokenize(text)
        for w in tokens:
            try:
                DF[w].add(text)
            except:
                DF[w] = {text}

    for i in DF:
        if len(DF[i]) == 1 or len(DF[i]) >= (len(textlist) * (6 / 10)):
            data.append(i)
        DF[i] = len(DF[i])
    return DF, data

#Removes words having document frequency = 1 or more than 80%
def rmv_words(textlist, DF):
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

def tfidf(text):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(text)
    features = vectorizer.get_feature_names()
    print(len(features))
    dense = vectors.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=features)
    return df

def preprocessing(textdata, steps):
    data = []
    for text in textdata:
        # will be able to process all characters
        text = unidecode(text)
        text = rmv_newline_char(text)
        if steps.index('url', 0, len(steps)) != -1:
            text = rmv_URLs(text)
        if steps.index('numbers', 0, len(steps)) != -1:
            text = rmv_numbers(text)
        if steps.index('punctuations', 0, len(steps)) != -1:
            text = rmv_punct(text)
            text = rmv_unknown_char(text)
        if steps.index('stopwords', 0, len(steps)) != -1:
            text = unusual_words(text)    
            text = rmv_stopWords(text)
        if steps.index('lemmatization', 0, len(steps)) != -1:
            text = apply_lemmatization(text)
        if steps.index('stemming', 0, len(steps)) != -1:
            text = apply_stemming(text)
        text = unusual_words(text)
        data.append(text)
    DF, datawords = get_count(data)
    data = rmv_words(data, DF)
    return data
