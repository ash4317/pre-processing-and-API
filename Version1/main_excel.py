import clean_file
import extract
import time
import pandas as pd


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
    tfidf = clean_file.varThresh_tfidf(df, 0.001)
    print(tfidf.shape)
    tfidf.to_csv('new.csv')
    filename = './prep.xlsx'
    fields = ['ISIN', 'Termsheet Link', 'Text'] 
    datalist = [ISINs, URLs, data]
    extract.exportexcel(filename, datalist, fields)
    print("---%s seconds" % (time.time() - start_time))
