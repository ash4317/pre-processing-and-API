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
json_dumps = json.dumps(datajson)



#Extract data
url = "http://127.0.0.1:5000/extract?no_of_docs=30&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url, json=datajson)
print(r.text)

#Export extracted data
url = "http://127.0.0.1:5000/extract/export?filepath=extract.xlsx&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
print(r.text)

#Pre-process data
url = "http://127.0.0.1:5000/preprocess?steps=url&steps=stemming&steps=lemmatization&steps=stopwords&steps=unusual&uname=admin&fname=ISINS_v3.xlsx" 
r = requests.post(url=url)
print(r.text)

#Export pre-processed data
url = "http://127.0.0.1:5000/preprocess/export?filepath=prep.xlsx&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
print(r.text)


#Returns elbow curve plot
url = "http://127.0.0.1:5000/clustering/elbow?uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
#img.save('elbow.png')
img.show()

#Returns optimal value of K using elbow curve
url = "http://127.0.0.1:5000/clustering/elbow?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

#Returns Silhouette score plot
url = "http://127.0.0.1:5000/clustering/silhouette?uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
#img.save('silhouette.png')
img.show()

#Returns optimal value of K using silhouette score
url = "http://127.0.0.1:5000/clustering/silhouette?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


#Perform K-Means clustering 
url = "http://127.0.0.1:5000/clustering/kmeans?k=4&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "http://127.0.0.1:5000/clustering/kmeans?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

# Get clustered data
url = "http://127.0.0.1:5000/clustering/summary?uname=admin"
r = requests.get(url=url)
print(r.text)

#Perform DBSCAN clustering
url = "http://127.0.0.1:5000/clustering/dbscan?eps=0.3&min=1&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "http://127.0.0.1:5000/clustering/dbscan?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)



#Perform Agglomerative clustering
url = "http://127.0.0.1:5000/clustering/agglomerative?k=5&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "http://127.0.0.1:5000/clustering/agglomerative?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)



#Perform Birch clustering
url = "http://127.0.0.1:5000/clustering/birch?k=5&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()

url = "http://127.0.0.1:5000/clustering/birch?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)
