'''
This module contains ALL the text pre-processing functions
'''

# Modules imported
import nltk
nltk.download('words')
nltk.download('stopwords')
from nltk.corpus import stopwords, words
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
import re
from unidecode import unidecode
import pandas as pd
import math
import os
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA



# some lists defined which are referred to later for text cleaning
MONTHS = ['january', 'february', 'march', 'april', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
NUMBERS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'hundred', 'thousand']
EXTRA_WORDS = ['number', 'month', 'note', 'will', 'inc', 'citigroup', 'markets', 'price', 'would', 'without', 'follow']


def rmv_newline_char(text):
    '''
    removes newline character '\n' and non-breaking space '\xa0' from the doc
    '''
    text = text.replace('\n', ' ')
    text = text.replace('\xa0', ' ')
    return text


def rmv_stopWords(text):
    '''
    To remove stopwords, numbers, months and extra words that are not useful.
    It also removes words whose length is less than 3 since they're most likely not useful.
    '''
    global NUMBERS, MONTHS, EXTRA_WORDS
    words = stopwords.words('english')
    words = words + NUMBERS + MONTHS + EXTRA_WORDS
    data = ' '.join(w for w in word_tokenize(text) if not w in words and len(w) > 3)
    return data


def unusual_words(text):
    '''
    Remove non-english words
    '''
    text_vocab = set(w.lower() for w in text.split() if w.isalpha())
    english_vocab = set(w.lower() for w in words.words())
    unusual = text_vocab - english_vocab
    data = ' '.join(w for w in (text_vocab - unusual))
    return data


def rmv_punct(text):
    '''
    Removes punctuations
    '''
    punct = list(string.punctuation)
    data = ''.join(i for i in text if i not in string.punctuation)
    return data


def rmv_numbers(text):
    '''
    Removes numbers
    '''
    data = ''.join(i for i in text if not i.isdigit())
    return data


def rmv_unknown_char(text):
    '''
    Function to remove special characters that cannot be removed by RegEx
    '''

    # unknown_chars_ascii contains ascii values of some special characters that are present in the doc but cannot be removed using regex
    unknown_chars_ascii = [9642, 9618, 8212, 8220, 8221, 8217, 174, 167, 168, 183, 47, 8211, 8226]

    # unknown_chars is a list containing these special characters
    unknown_chars = [chr(x) for x in unknown_chars_ascii]

    for i in unknown_chars:
        # for character with ascii 8212 and 47 should be replaced by a whitespace

        if i == chr(8212) or i == chr(47):
            text = text.replace(i, ' ')
        else:
            text = text.replace(i, '')
    return text


def apply_stemming(text):
    '''
    Perform stemming on all the words
    '''
    stemmer = PorterStemmer()
    data = ' '.join(stemmer.stem(w) for w in word_tokenize(text))
    return data


def apply_lemmatization(text):
    '''
    Perform lemmatization on all the words
    '''
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    tokens = [lemmatizer.lemmatize(w, pos = 'a') for w in tokens]
    tokens = [lemmatizer.lemmatize(w, pos = 'v') for w in tokens]
    data = ' '.join(w for w in tokens)
    return data


def get_count(textlist):
    '''
    Returns document frequency of each word and list of most common and rare words
    '''
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


def rmv_common_words(textlist, DF):
    '''
    Removes words having document frequency = 1 or more than 75%
    '''
    data = []
    for text in textlist:
        dataitem = ' '.join(w for w in word_tokenize(text) if DF[w] < (len(textlist) * (75/100)) and DF[w] != 1)
        data.append(dataitem)
    return data


def rmv_URLs(text):
    '''
    Removes URLs
    '''
    txt = ''
    words = text.split()
    for word in words:
        if re.search('^www.*', word) or re.search('^us.*', word):
            continue
        txt += word + ' '
    txt = txt.strip()
    return txt


def tfidf(text):
    '''
    Calculates the tfidf matrix for the input pre-processed text
    '''
    vectorizer = TfidfVectorizer(smooth_idf=False)
    vectors = vectorizer.fit_transform(text)
    features = vectorizer.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=features)
    return df


def varThresh_tfidf(tfidf, thresh):
    '''
    Reduces features in the tfidf matrix using Variance Threshold.
    tfidf: tfidf matrix
    thresh: threshold of variance below which data has to be kept
    '''
    selector = VarianceThreshold(threshold=thresh) 
    selector.fit(tfidf)
    data = tfidf[tfidf.columns[selector.get_support(indices=True)]]
    return data


def pca_tfidf(tfidf, n):
    '''
    Applies Principal Component Analysis (PCA) to further reduce features.
    tfidf: tfidf matrix
    n: number of components to keep
    '''
    scaler = StandardScaler()
    segmentation_std = scaler.fit_transform(tfidf) 
    pca = PCA(n_components=n)
    scores_pca = pca.fit_transform(segmentation_std)
    df = pd.DataFrame(pca.components_,columns=tfidf.columns)
    ratio = pca.explained_variance_ratio_
    return ratio, scores_pca, df


def varThresh_textlist(text, thresh):
    '''
    Returns reduced features and document count for each word using VarianceThreshold.
    '''
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


def preprocessing(textdata, steps):
    '''
    Main function which performs all the pre-processing techniques that the user has selected.
    The techniques to be applied are present in the "steps" list.
    '''
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
        if 'unusual' in steps:
            text = unusual_words(text)
        if 'lemmatization' in steps:
            text = apply_lemmatization(text)
        if 'stemming' in steps:
            text = apply_stemming(text)
        data.append(text)
        count += 1
        print(f'Preprocessed: {count}')
    DF = get_count(data)
    data = rmv_common_words(data, DF)
    return data
