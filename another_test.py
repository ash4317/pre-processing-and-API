import requests
#python -m pip install --upgrade pillow
from PIL import Image
import io
import extract as ex
import json
import pandas as pd


def readlinks(path):
    '''
    Reads extracted dataset and returns ISINs, Termsheet links and Text
    '''
    if ex.check(path, '.csv'):
        df = pd.read_csv(path)
    elif ex.check(path, '.xlsx'):
        df = pd.read_excel(path)
    urlList = df['Termsheet Link'].tolist()
    isinList = df['ISIN'].tolist()
    return isinList, urlList


# sample JSON object consisting all ISINs and URLs
filename = 'ISINS_v3.xlsx'
ISINs, URLs = readlinks(filename)
datajson = dict()
i = 0
for ISIN in ISINs:
    datajson[ISIN] = URLs[i]    
    i += 1

keys = list(datajson)
extracted_data = list()
no_of_docs = 100
for i in range(0, no_of_docs, 15):
    print(i)
    p = {keys[j]:datajson[keys[j]] for j in range(i, i+15)}
    r = requests.post(url='https://preprocess-and-cluster-api.herokuapp.com/extract?uname=ash4317&fname=ISINS_v3.xlsx', json=p)
    r = requests.get('https://preprocess-and-cluster-api.herokuapp.com/extract?uname=ash4317&fname=ISINS_v3.xlsx')
    data = r.json()['data']
    extracted_data = extracted_data + data

fhand = open("extracted.json", "w")
js = json.dumps(extracted_data)
fhand.write(js)
fhand.close()