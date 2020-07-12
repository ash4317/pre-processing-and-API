'''
Module created for extracting data from input excel sheet and exporting various data in either list object or JSON object into excel or csv format.
This modules also includes functions to write data to json and read data from json, convert data from lists into json file and vice-versa.
'''

# modules imported
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import csv
from csv import writer  
import pandas as pd
import os
import nltk
nltk.download('words')
nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import digits
import xlsxwriter
from xlsxwriter.workbook import Workbook
import xlwt
from xlwt import Workbook as wb
import json
import clean_file as cf # module created for text cleaning


def check(string, sub_str):
    '''
    Checks for substring, returns 1 (present) or 0 (not present)
    '''
    if (string.find(sub_str) == -1):
        return 0
    else: 
        return 1


def append_list_as_row(file_name, list_of_elem):
    '''
    Appends new row to the existing csv file
    '''
    with open(file_name, 'a+', newline='',encoding="utf8") as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)
    

def exportcsv(uname, fname, filename='export.csv', field1 = [], field2 = [], field3 = [], fields=['ISIN', 'Termsheet Link', 'Text']):
    '''
    Export all the data in the fields into a csv file (by default, "export.csv")
    '''
    filename = give_filename(filename.split('.')[0] + '_' + uname + '_' + fname, '.' + filename.split('.')[1])
    if os.path.isfile(filename):
        os.remove(filename)
    append_list_as_row(filename, fields)
    i = 0
    for ilist in field1:
        append_list_as_row(filename, [ilist, field2[i], field3[i]])
        i += 1


def exportexcel(uname, fname, filename='export.xlsx', datalist=[], fields=['ISIN', 'Termsheet Link', 'Text']):
    '''
    Exports data in the form of excel file, datalist is a list of lists, fields is a list of fields
    '''
    filename = give_filename(filename.split('.')[0] + '_' + uname + '_' + fname, '.' + filename.split('.')[1])
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


def extract(isinList, urlList, no_of_docs):
    '''
    Extracts data, performs basic pre-processings and returns list of ISINs, URLs, and extracted text
    '''

    # if no_of_docs is 'all', then extract from ALL the URLs given in the excel sheet. If no_of_docs = int, select only those many URLs.
    if no_of_docs != 'all':
        urlList = urlList[:int(no_of_docs)]
        isinList = isinList[:int(no_of_docs)]

    ISINs = []
    URLs = []
    textlist = []
        
    count = 0
    i = 0
    for url in urlList:

        # only extract data from ".htm" or ".html" files
        r = check(url, ".htm")
        s = check(url, ".html")
        if r == 1 or s == 1:

            # check if url is valid
            try:
                html = urlopen(url).read().decode()
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

            # append all the extracted data to the respective lists
            ISINs.append(isinList[i])
            URLs.append(url)
            textlist.append(text)
            count += 1
            print('Extracted:', count)
        i = i+1

    return ISINs, URLs, textlist




def readdataset(path):
    '''
    Reads extracted dataset and returns ISINs, Termsheet links and Text
    '''
    if check(path, '.csv'):
        df = pd.read_csv(path)
    elif check(path, '.xlsx'):
        df = pd.read_excel(path)

    urlList = df['Termsheet Link'].tolist()
    isinList = df['ISIN'].tolist()
    text = df['Text'].tolist()
    return isinList, urlList, text

def write_json(data, fname):
    '''
    Write data into a JSON file
    '''
    fhand = open(fname, 'w')
    js = json.dumps(data)
    fhand.write(js)
    fhand.close()


def read_json(fname):
    '''
    Read data from a JSON file
    '''
    fhand = open(fname)
    data = fhand.read()
    js = json.loads(data)
    return js


def tojson(ISINs, URLs, data):
    '''
    Returns data in json format
    '''
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


def tojsondf(ISINs, URLs, cluster):
    '''
    Returns clustered data in json format
    '''
    datajson = dict()
    i = 0
    x = -100
    for clust in cluster:
        if clust == x:
            pass
        else:
            datajson['Cluster ' + str(clust)] = list()
        datajson['Cluster ' + str(clust)].append({'ISIN': ISINs[i], 'URL': URLs[i]})
        x = clust
        i += 1

    return datajson


def jsontolists(jsondata):
    '''
    Converts json data into lists
    '''
    ISINs = []
    URLs = []
    text = []
    for data in jsondata:
        ISINs.append(data['ISIN'])
        URLs.append(data['URL'])
        text.append(data['Data'])
    return ISINs, URLs, text


def export(data, format, fname):
    '''
    Exports the data to either excel file or a csv file depending on the "format" argument
    '''
    if format == 'excel':
        export_to_excel(data, fname, '.xls')
    elif format == 'csv':
        export_to_csv(data, fname, '.csv')
    else:
        print('Invalid file format. Valid file formats are "excel" and "csv". Could not export results.')


def export_to_excel(results, fname, extension):
    '''
    Writes all the doc URLs along with the cluster to which they belong to an excel file
    '''
    fhand = wb()
    count = 1
    sheet = fhand.add_sheet('Sheet 1')
    style = xlwt.easyxf('font: bold 1')
    sheet.write(0, 0, 'Cluster', style)
    sheet.write(0, 2, 'ISIN', style)
    sheet.write(0, 4, 'Termsheet URL', style)
    count = 2
    for c in results.keys():
        for val in results[c]:
            sheet.write(count, 0, c)
            sheet.write(count, 2, val['ISIN'])
            sheet.write(count, 4, val['URL'])
            count += 1
        count += 2
    fhand.save(fname + extension)

def export_to_csv(results, fname, extension):
    '''
    Writes all the doc URLs along with the cluster to which they belong to a csv file
    '''
    with open(fname + extension, 'w') as fhand:
        writer=csv.writer(fhand)
        writer.writerow(['Cluster No.', 'ISIN', 'URL'])
        for c in results.keys():
            for val in results[c]:
                c0 = c.split(' ')[0] + '_' + c.split(' ')[1]
                writer.writerow([c0, val['ISIN'], val['URL']])



def give_filename(fname, extension):
    '''
    Also adds date and time to the file name so that file can be identified
    '''
    date = datetime.now()
    name = date.strftime('%d') + '-' + date.strftime('%m')  + '-' + date.strftime('%Y') + '_' + date.strftime('%X').replace(':', '-')
    fname += '_' + name + extension
    return fname



def get_recent_file(name):
    '''
    Selects the most recent file updated/created
    '''
    names = [x for x in os.listdir() if name in x and '.json' in x]
    names.sort(reverse=True)
    return names[0]