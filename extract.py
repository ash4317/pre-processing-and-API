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
import xlwt
from xlwt import Workbook as wb
import clean_file as cf

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

def exportcsv(filename='export.csv', field1 = [], field2 = [], field3 = [], fields=['ISIN', 'Termsheet Link', 'Text']):
    if os.path.isfile(filename):
        os.remove(filename)

    append_list_as_row(filename, fields)
    i = 0
    for ilist in field1:
        append_list_as_row(filename, [ilist, field2[i], field3[i]])
        i += 1

#Exports data in the form of excel file, datalist is a list of lists, fields is a list of fields
def exportexcel(filename='export.xlsx', datalist=[], fields=['ISIN', 'Termsheet Link', 'Text']):

    workbook = Workbook(filename)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({'bold': True})
    i = 0
    for field in fields:
        worksheet.write(0, i, field, cell_format)
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
def extract(path, no_of_docs):
    df = pd.read_excel(path, sheet_name=0)
    try:
        urlList = df['Termsheet Link'].tolist()
        isinList = df['ISIN'].tolist()
    except:
        return 'Invalid File'
    if no_of_docs != 'all':
        urlList = urlList[:int(no_of_docs)]
        isinList = isinList[:int(no_of_docs)]
    ISINs = []
    URLs = []
    textlist = []
        
    count = 0
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
            count += 1
            print('Extracted:', count)
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

def write_json(data, fname):
    fhand = open(fname, 'w')
    js = json.dumps(data)
    fhand.write(js)
    fhand.close()


def read_json(fname):
    fhand = open(fname)
    data = fhand.read()
    js = json.loads(data)
    return js

#Returns data in json format
def tojson(ISINs, URLs, data):
    datajson = []
    i = 0
    for ISIN in ISINs:
        datajson.append({
            'ISIN': ISIN,
            'URL': URLs[i],
            'Data': data[i]
        })
        i += 1

    return datajson

#Returns data in json format
def tojsondf(ISINs, URLs, cluster):
    datajson = []
    i = 0
    for clust in cluster:
        datajson.append({
            'Cluster': clust,
            'ISIN': ISINs[i],
            'URL': URLs[i]
        })
        i += 1

    return datajson
    
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

#Returns lists from json data
def jsontolists(jsondata):
    ISINs = []
    URLs = []
    text = []
    for data in jsondata:
        ISINs.append(data['ISIN'])
        URLs.append(data['URL'])
        text.append(data['Data'])
    return ISINs, URLs, text  

    
def jsontolistsC(jsondata):
    ISINs = []
    URLs = []
    cluster = []
    for data in jsondata:
        ISINs.append(data['ISIN'])
        URLs.append(data['URL'])
        cluster.append(data['Cluster'])
    return cluster, ISINs, URLs

#Reads json file and prints data
def printjson(path):
    with open(path) as json_file:
        data = json.load(json_file)
        for p in data:
            print('ISIN: ' + p['ISIN'])
            print('URL: ' + p['URL'])
            print('Data: ' + p['Data'])
            print('')

def sort_by_key(x):
    return x[0]


def sort(results):
    '''
    Sort the dictionary by cluster number
    '''
    results = list(results.items())
    results.sort(key=sort_by_key)
    return dict(results)


def show_results(isin_list, urllist, clusters):
    '''
    This function will return a dictionary which stores all files in respective clusters
    '''
    results = dict()
    for i in range(len(clusters)):
        if clusters[i] in results.keys():

            # if list is already made
            results[clusters[i]].append([isin_list[i], urllist[i]])
        else:

            # initialize value of the key to a list
            results[clusters[i]] = list()
            results[clusters[i]].append([isin_list[i], urllist[i]])
    
    # function to sort results by cluster number
    results = sort(results)
    return results


def export_to_excel(results, fname):
    '''
    Writes all the doc URLs along with the cluster to which they belong
    '''
    fhand = wb()
    count = 1
    sheet = fhand.add_sheet('Sheet 1')
    style = xlwt.easyxf('font: bold 1')
    sheet.write(0, 0, 'Cluster', style)
    sheet.write(0, 1, 'ISIN', style)
    sheet.write(0, 2, 'Termsheet URL', style)
    for x, y in results.items():
        count += 2
        for data in y:
            sheet.write(count, 0, x)
            sheet.write(count, 1, data[0])
            sheet.write(count, 2, data[1])
            count += 1
    fhand.save(fname)