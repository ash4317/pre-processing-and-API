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
url = "http://127.0.0.1:5000/extract?no_of_docs=50&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url, json=datajson)
print(r.text)


#Export extracted data
url = "http://127.0.0.1:5000/extract/export?filepath=extract.xlsx&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
open('admin_'+'extract.xlsx', 'wb').write(r.content)


#Pre-process data
url = "http://127.0.0.1:5000/preprocess?steps=url&steps=stemming&steps=lemmatization&steps=stopwords&steps=unusual&uname=admin&fname=ISINS_v3.xlsx" 
r = requests.post(url=url)
print(r.text)


#Export pre-processed data
url = "http://127.0.0.1:5000/preprocess/export?filepath=prep.xlsx&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)
open('prep.xlsx', 'wb').write(r.content)


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

url = "http://127.0.0.1:5000/clustering/dbscan?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)



#Perform Agglomerative clustering
url = "http://127.0.0.1:5000/clustering/agglomerative?k=5&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)

url = "http://127.0.0.1:5000/clustering/agglomerative?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)



#Perform Birch clustering
url = "http://127.0.0.1:5000/clustering/birch?k=5&format=csv&uname=admin&fname=ISINS_v3.xlsx"
r = requests.post(url=url)

url = "http://127.0.0.1:5000/clustering/birch?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)

url = "http://127.0.0.1:5000/clustering/summary?uname=admin&fname=ISINS_v3.xlsx"
r = requests.get(url=url)
print(r.text)


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

# Extract data
url = "http://127.0.0.1:5000/report?uname=admin&kind=1"
r = requests.post(url=url, json=datajson)
print(r.text)


url = "http://127.0.0.1:5000/report?uname=admin"
r = requests.get(url=url)
print(r.text)
