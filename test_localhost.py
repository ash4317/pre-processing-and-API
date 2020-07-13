import requests
#python -m pip install --upgrade pillow
from PIL import Image
import io
import extract as ex
import json
import pandas as pd


def readlinks(path):
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

'''
Arguments: no_of_docs, uname (Username)*, fname (Filename)*
json *: json object of ISINs and URLs
return: JSON response, status 
'''
#Extract data
url = "http://127.0.0.1:5000/extract?no_of_docs=10&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url, json=datajson)
print(r.text)


'''
Arguments: filepath *, uname (Username)*, fname (Filename)*
return: Excel file of extracted data
'''
#Export extracted data
url = "http://127.0.0.1:5000/extract/export?filepath=extract.xlsx&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
open('admin_'+'extract.xlsx', 'wb').write(r.content)


'''
Arguments: steps (Pre-processing techniques), uname (Username)*, fname (Filename)*
data: extracted binary data
return: JSON response, status 
'''
#Pre-process data
url = "http://127.0.0.1:5000/preprocess?steps=url&steps=stemming&steps=lemmatization&steps=stopwords&steps=unusual&uname=admin&fname=ISINS_v3.xlsx" 
r = requests.post(url=url)
print(r.text)


'''
Arguments: filepath *, uname (Username)*, fname (Filename)*
return: Excel file of extracted data
'''
#Export pre-processed data
url = "http://127.0.0.1:5000/preprocess/export?filepath=prep.xlsx&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
open('prep.xlsx', 'wb').write(r.content)


'''
Arguments: thresh(variance threshold, by default 0.0001), pca_comp(No. of components for applying PCA, by default 0.8), uname (Username)*, fname (Filename)*
data: pre-processed binary data
return: stream of bytes for plot
'''
#Returns elbow curve plot
data = open('prep.xlsx', 'rb').read()
url = "http://127.0.0.1:5000/clustering/elbow?uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url, data=data, headers={'Content-Type': 'application/octet-stream'})
img = Image.open(io.BytesIO(r.content))
#img.save('elbow.png')
img.show()


'''
Arguments: uname (Username)*
return: optimal value of k
'''
#Returns optimal value of K using elbow curve
url = "http://127.0.0.1:5000/clustering/elbow?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: thresh(variance threshold, by default 0.0001), pca_comp(No. of components for applying PCA, by default 0.8), uname (Username)*, fname (Filename)*
data: pre-processed binary data
return: stream of bytes for plot
'''
#Returns Silhouette score plot
url = "http://127.0.0.1:5000/clustering/silhouette?uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
#img.save('silhouette.png')
img.show()


'''
Arguments: uname (Username)*
return: optimal value of k
'''
#Returns optimal value of K using silhouette score
url = "http://127.0.0.1:5000/clustering/silhouette?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: K, thresh(variance threshold, by default 0.0001), pca_comp(No. of components for applying PCA, by default 0.8), uname (Username)*, fname (Filename)*
data: pre-processed binary data
return: co-ordinates for scatter plot
'''
#Perform K-Means clustering 
url = "http://127.0.0.1:5000/clustering/kmeans?k=4&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)


'''
Arguments: uname (Username)*
return: JSON response, list of clusters
'''
url = "http://127.0.0.1:5000/clustering/kmeans?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: content_type (summary or details, by default summary), uname (Username)*
return: JSON response, summary / details of clustering
'''
# Get clustered data
url = "http://127.0.0.1:5000/clustering/summary?uname=admin"
r = requests.get(url=url)
print(r.text)


'''
Arguments: eps (Epsilon value), min (Minimum points), thresh(variance threshold, by default 0.0001), pca_comp(No. of components for applying PCA, by default 0.8), uname (Username)*, fname (Filename)*
data: pre-processed binary data
return: co-ordinates for scatter plot
'''
#Perform DBSCAN clustering
url = "http://127.0.0.1:5000/clustering/dbscan?eps=0.3&min=1&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)


'''
Arguments: uname (Username)*
return: JSON response, list of clusters
'''
url = "http://127.0.0.1:5000/clustering/dbscan?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: content_type (summary or details, by default summary), uname (Username)*
return: JSON response, summary / details of clustering
'''
url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: K, thresh(variance threshold, by default 0.0001), pca_comp(No. of components for applying PCA, by default 0.8), uname (Username)*, fname (Filename)*
data: pre-processed binary data
return: co-ordinates for scatter plot
'''
#Perform Agglomerative clustering
url = "http://127.0.0.1:5000/clustering/agglomerative?k=5&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)


'''
Arguments: uname (Username)*
return: JSON response, list of clusters
'''
url = "http://127.0.0.1:5000/clustering/agglomerative?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: content_type (summary or details, by default summary), uname (Username)*
return: JSON response, summary / details of clustering
'''
url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: K, thresh(variance threshold, by default 0.0001), pca_comp(No. of components for applying PCA, by default 0.8), uname (Username)*, fname (Filename)*
data: pre-processed binary data
return: co-ordinates for scatter plot
'''
#Perform Birch clustering
url = "http://127.0.0.1:5000/clustering/birch?k=5&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)


'''
Arguments: uname (Username)*
return: JSON response, list of clusters
'''
url = "http://127.0.0.1:5000/clustering/birch?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: content_type (summary or details, by default summary), uname (Username)*
return: JSON response, summary / details of clustering
'''
url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


'''
Arguments: uname (Username)*
return: JSON response, status
'''

# Clear summary and cluster files at the time of log out
url = "http://127.0.0.1:5000/clear?uname=admin"
r = requests.delete(url=url)
print(r.text)



# Tests for Report Generation code
datajson = {
    'US17326YZV19': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007930/dp108304_424b2-us1972721.htm',
    'US17326YJJ64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319008018/dp108385_424b2-us1972668.htm',
    'US17326YU388': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319008084/dp108463_424b2-us1972667.htm',
    'US17326YNL64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009058/dp109430_424b2-us1972617.htm',
    'US17326YUM64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007911/dp108280_424b2-us1972550.htm',
    'US17326YRV01': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009050/dp109447_424b2-us1972547.htm',
    'US17326YPB64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007828/dp108206_424b2-us1972545.htm',
    'US17326Y4M50': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009060/dp109497_424b2-us1972484.htm',
    'US17326YC873': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007527/dp107872_fwp-us1972482.htm',
    'US17326YDX13': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007524/dp107870_fwp-us1972480.htm',
    'US17326YFJ01': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319008572/dp109026_424b2-us1972369.htm',
    'US17326YTD84': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007525/dp107868_fwp-us1972350.htm',
    'US17326YAH99': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009080/dp109492_424b2-us1972281.htm',
    'US17326YMQ60': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007870/dp108232_424b2-us1972280.htm',
    'US17326YBP07': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007155/dp107611_424b2-us1972269.htm',
    'US17326Y2L95': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009048/dp109444_424b2-us1972158.htm',
}
print(len(datajson))



'''
Arguments: no_of_docs, uname (Username)*, kind (1 = brute force method or 2 = non-brute force method)*
return: JSON object, status
'''
# Extract data
url = "http://127.0.0.1:5000/report?username=admin&kind=1"
r = requests.post(url=url, json=datajson)
print(r.text)



'''
Arguments: uname (Username)*
return: JSON object, results
'''
url = "http://127.0.0.1:5000/report?username=admin"
r = requests.get(url=url)
print(r.text)
