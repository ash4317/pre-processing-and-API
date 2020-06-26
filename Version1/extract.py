from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from csv import writer  
import csv
import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import digits
from xlsxwriter.workbook import Workbook

def check(string, sub_str): 
    if (string.find(sub_str) == -1):
        return 1
    else: 
        return 0

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='',encoding="utf8") as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

def csv_to_excel(path):
    csvfile = path
    workbook = Workbook(csvfile[:-4] + '.xlsx')
    worksheet = workbook.add_worksheet()
    with open(csvfile, 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()


def exportexcel(filename, isinList, urlList, data, fields):
    if os.path.isfile(filename):
        os.remove(filename)
    append_list_as_row(filename, fields)
    i = 0
    for d in data:
        append_list_as_row(filename, [isinList[i], urlList[i], d])
        i += 1
    csv_to_excel(filename)
    if os.path.isfile(filename):
        os.remove(filename)

def extract(path):
    df = pd.read_excel(path, sheet_name=0)
    try:
        urlList = df['Termsheet Link'].tolist()
        isinList = df['ISIN'].tolist()
    except:
        return 'Invalid File'

    ISINs = []
    URLs = []
    textlist = []
        
    i = 0
    for url in urlList:
        r = check(url, ".htm")
        if r == 0:
            try:
                html = urlopen(url).read()
            except:
                continue
            soup = BeautifulSoup(html,features="html.parser")
            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out

            # get text
            text = soup.get_text()

            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)

            text = re.sub(r' +', ' ', text)
            text = re.sub(r'\n+', ' ', text)
            text = text.encode('ascii', 'ignore').decode()

            ISINs.append(isinList[i])
            URLs.append(url)
            textlist.append(text)
            print('Done:'+url)
            i = i+1

    return ISINs, URLs, textlist

