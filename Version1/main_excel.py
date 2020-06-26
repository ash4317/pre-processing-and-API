import clean_file
import extract
import sys
import time
import os
from bs4 import BeautifulSoup
from urllib import request, parse, error
import xlrd
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.cluster import DBSCAN
from urllib.request import urlopen
import re
from csv import writer  


if __name__ == "__main__":
    '''
    Main function
    '''
    start_time = time.time()
    steps = ['numbers', 'url', 'stemming', 'lemmatization', 'punctuations', 'stopwords', 'case', 'words']
    ISINs, URLs, textlist = extract.extract('ISINS.xlsx')
    print("---%s seconds" % (time.time() - start_time))
    data = clean_file.preprocessing(textlist, steps)
    df = clean_file.tfidf(data)
    print(df.shape)
    filename = './prep.csv'
    fields = ['ISIN', 'Termsheet Link', 'Text'] 
    extract.exportexcel(filename, ISINs, URLs, data, fields)
    print("---%s seconds" % (time.time() - start_time))
