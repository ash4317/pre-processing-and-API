import requests
#python -m pip install --upgrade pillow
from PIL import Image
import matplotlib.pyplot as plt
import io
'''
#Extract data
url = "http://127.0.0.1:5000/extract?filepath=ISINS_v3.xlsx&no_of_docs=30"
r = requests.post(url=url)
print(r.text)


#Export extracted data
url = "http://127.0.0.1:5000/extract/export?filepath=extract.xlsx"
r = requests.get(url=url)
print(r.text)


#Pre-process data
url = "http://127.0.0.1:5000/preprocess?steps=url&steps=stemming&steps=lemmatization&steps=stopwords&steps=unusual" 
r = requests.post(url=url)
print(r.text)

#Export pre-processed data
url = "http://127.0.0.1:5000/preprocess/export?filepath=prep.xlsx"
r = requests.get(url=url)
print(r.text)

'''
#Perform K-Means clustering 
url = "http://127.0.0.1:5000/clustering/kmeans?filepath=prep.xlsx&k=4"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
print(img)
img.show()

url = "http://127.0.0.1:5000/clustering/kmeans"
r = requests.get(url=url)
print(r.text)

#Export clustered data
url = "http://127.0.0.1:5000/clustering/kmeans/export?filepath=kmeans.xlsx"
r = requests.get(url=url)
print(r.text)

# Get clustered data
url = "http://127.0.0.1:5000/clustering/kmeans/summary"
r = requests.get(url=url)
print(r.text)


#Perform DBSCAN clustering
url = "http://127.0.0.1:5000/clustering/dbscan?filepath=prep.xlsx&eps=0.3&min=1"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
print(img)
img.show()

url = "http://127.0.0.1:5000/clustering/dbscan"
r = requests.get(url=url)
print(r.text)

#Export clustered data
url = "http://127.0.0.1:5000/clustering/dbscan/export?filepath=dbscan.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/dbscan/summary"
r = requests.get(url=url)
print(r.text)

#Perform Agglomerative clustering
url = "http://127.0.0.1:5000/clustering/agglomerative?filepath=prep.xlsx&k=5"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
print(img)
img.show()

url = "http://127.0.0.1:5000/clustering/agglomerative"
r = requests.get(url=url)
print(r.text)


#Export clustered data
url = "http://127.0.0.1:5000/clustering/agglomerative/export?filepath=agglomerative.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/agglomerative/summary"
r = requests.get(url=url)
print(r.text)

#Perform Birch clustering
url = "http://127.0.0.1:5000/clustering/birch?filepath=prep.xlsx&k=5"
r = requests.post(url=url)
print(type(r.content))
img = Image.open(io.BytesIO(r.content))
print(img)
img.show()

url = "http://127.0.0.1:5000/clustering/birch"
r = requests.get(url=url)
print(r.text)

#Export clustered data
url = "http://127.0.0.1:5000/clustering/birch/export?filepath=birch.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/birch/summary"
r = requests.get(url=url)
print(r.text)
