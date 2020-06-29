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
import json
import xlsxwriter

#Checks for substring, returns 1 (present) or 0 (not present)
def check(string, sub_str): 
    if (string.find(sub_str) == -1):
        return 0
    else: 
        return 1

#Appends new row to the existing csv file
def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='',encoding="utf8") as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)
    
#Converts csv file to excel file
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

#Exports data in the form of excel file, datalist is a list of lists, fields is a list of fields
def exportexcel(filename='export.xlsx', datalist=[], fields=['ISIN', 'Termsheet Link', 'Text']):
    if os.path.isfile(filename):
        os.remove(filename)

    workbook = Workbook(filename)
    worksheet = workbook.add_worksheet()
    i = 0
    for field in fields:
        worksheet.write(0, i, field)
        i += 1
    
    j = 0
    for data in datalist:
        i = 1
        for d in data:
            worksheet.write(i, j, d)
            i += 1
        j += 1

    workbook.close()

#Extracts data, performs basic pre-processings and returns list of ISINs, URLs, and extracted text
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
        if r == 1:
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

#Reads extracted dataset if in csv format and returns ISINs, Termshit links, and text
def readdataset(path):
    if check(path, '.csv'):
        df = pd.read_csv(path)
    elif check(path, '.xlsx'):
        df = pd.read_excel(path)

    urlList = df['Termsheet Link'].tolist()
    isinList = df['ISIN'].tolist()
    text = df['Text'].tolist()
    return isinList, urlList, text
    
#Exports data to json file
def exportjson(ISINs, URLs, data, path):
    datajson = []
    i = 0
    for ISIN in ISINs:
        datajson.append({
            'ISIN': ISIN,
            'URL': URLs[i],
            'Data': data[i]
        })
        i += 1

    with open(path, 'w') as outfile:
        json.dump(datajson, outfile)

#Reads json file and prints data
def printjson(path):
    with open(path) as json_file:
        data = json.load(json_file)
        for p in data:
            print('ISIN: ' + p['ISIN'])
            print('URL: ' + p['URL'])
            print('Data: ' + p['Data'])
            print('')
