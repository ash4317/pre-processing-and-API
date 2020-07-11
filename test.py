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



#Extract data
url = "https://preprocess-and-cluster-api.herokuapp.com/extract?no_of_docs=30&uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.post(url=url, json=datajson)
print(r.text)

#Export extracted data
url = "https://preprocess-and-cluster-api.herokuapp.com/extract/export?filepath=extract.xlsx&uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
print(r.text)

#Pre-process data
url = "https://preprocess-and-cluster-api.herokuapp.com/preprocess?steps=url&steps=stemming&steps=lemmatization&steps=stopwords&steps=unusual&uname=ash4317&fname=ISINS_v3.xlsx" 
r = requests.post(url=url)
print(r.text)

#Export pre-processed data
url = "https://preprocess-and-cluster-api.herokuapp.com/preprocess/export?filepath=prep.xlsx&uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
print(r.text)



#Perform K-Means clustering 
url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/kmeans?k=4&format=csv&uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/kmeans?uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

# Get clustered data
url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/summary?uname=ash4317"
r = requests.get(url=url)
print(r.text)

#Perform DBSCAN clustering
url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/dbscan?eps=0.3&min=1&format=csv&uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/dbscan?uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/summary?uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)



#Perform Agglomerative clustering
url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/agglomerative?k=5&format=csv&uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/agglomerative?uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/summary?uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)



#Perform Birch clustering
url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/birch?k=5&format=csv&uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/birch?uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "https://preprocess-and-cluster-api.herokuapp.com/clustering/summary?uname=ash4317&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)
