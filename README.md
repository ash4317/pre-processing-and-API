# Documentation for Pre-processing and Clustering API

###### Created by: Ashwin Kulkarni, Vaishnavi Patil

==========================================================================================================================================================================

### Introduction


This API is created for extracting data from only ".htm" files present on some URL, pre-processing the data and using clustering algorithms to group them into various clusters on the basis of any similarity present between the documents.

==========================================================================================================================================================================

### How to run this API locally


For Windows users: Open command prompt and go to the directory where this API along with the modules that it imports is located. Then, set the environment variables "FLASK_APP" and "FLASK_ENV" and run the flask API as follows-

 > set FLASK_APP=api.py
 
 > set FLASK_ENV=development
 
 > flask run

For MAC/Linux users: Open terminal window and go to the directory where this API along with the modules that it imports is located. Then, set the environment variables "FLASK_APP" and "FLASK_ENV" and run the flask API as follows-

  export FLASK_APP=api.py
  export FLASK_ENV=development
  flask run

==========================================================================================================================================================================

API functions


1) Extracting and Exporting data present at URLs given in an excel sheet

Extracting data example:
import requests
url = "http://127.0.0.1:5000/extract?filepath=ISINS_v3.xlsx&no_of_docs=30"
r = requests.post(url=url)
print(r.text)
Input arguments- a) filepath- The path of the excel sheet where all the URLs where the htm files are located. Format of the excel sheet should be- (ISIN, URL)
                 b) no_of_docs (optional)- Number of URLs from which data is to be extracted. By default, it will extract from ALL the URLs.
Writes the extracted data into the file "extract.json".
To get extracted data,
import requests
url = "http://127.0.0.1:5000/extract"
r = requests.get(url=url)
print(r.text)

Exporting data example:
import requests
url = "http://127.0.0.1:5000/extract/export?filepath=extract.xlsx"
r = requests.post(url=url)
print(r.text)
Input arguments- a) filepath- Path of the file to which data is to be exported. The output file can be of formats ".csv" & ".xlsx"
The format of the exported file is- (ISIN, URL, text) for every htm file
__________________________________________________________________________________________________________________________________________________________________________
2) Pre-processing the extracted data and exporting it

Pre-processing data example:
import requests
url = "http://127.0.0.1:5000/preprocess?filepath=ISINS_v3.xlsx&steps=url&steps=stemming&steps=lemmatization&steps=stopwords&steps=unusual" 
r = requests.post(url=url)
print(r.text)
Input arguments- a) filepath (optional)- The path of the excel sheet where all the URLs where the htm files are located. If filepath is given, then
                                         API will extract first from the URLs present in the excel sheet given in the filepath and then pre-process it. If filepath is not given, API will assume that data is extracted first (which is stored in the file "extract.json") and directly pre-process it.
                 b) steps (optional)- The different pre-processing techniques to be applied on the extracted text. Valid arguments are:
                                      i) url- Removes URLs from the text
                                      ii) stemming- Performs stemming on the text
                                      iii) lemmatization- Performs lemmatization on the text
                                      iv) stopwords- Removes stopwords from the text
                                      v) unusual- Removes words that don't have any meaning
                                      The API performs some basic pre-processing like removal of numbers, punctuations, unknown ASCII characters, converting text to lowercase etc. by default.
To get pre-processed data,
import requests
url = "http://127.0.0.1:5000/preprocess"
r = requests.get(url=url)
print(r.text)
Response is a JSON object of the format [{ISIN: (value), URL: (value), Preprocessed text: (value)}] for all the documents

Exporting pre-processed data example:
import requests
url = "http://127.0.0.1:5000/preprocess/export?filepath=prep.xlsx"
r = requests.post(url=url)
print(r.text)
Input arguments- a) filepath- Path of the file to which pre-processed data is to be exported. The output file can be of formats ".csv" & ".xlsx"
The format of the exported file is- (ISIN, URL, text) for every htm file
__________________________________________________________________________________________________________________________________________________________________________
3) Performing k-means clustering on pre-processed data and exporting it

Clustering example:
import requests
import io
from PIL import image
url = "http://127.0.0.1:5000/clustering/kmeans?filepath=prep.xlsx&k=4&format=csv"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()
Performs k-means clustering on the pre-processed data and plots a scatter plot showing different clusters generated by the algorithm. It also exports the output to an excel file or csv file according to the user's input.
Input arguments- a) filepath (optional)- Path of excel sheet or csv file where the pre-processed data is stored. If argument is not given, the API will assume that the
                                         pre-processed data is present in the file "preprocess.json" in the form of a list containing a dictionary like {ISIN, URL, Data} as individual elements.
                 b) k- Value of k in k-means algorithm which is the number of clusters to be made
                 c) thresh (optional)- The threshold value of variance in the variance threshold algorithm for reducing number of features. Default value is 0.001
                 d) pca_comp (optional)- The number of components in the Principal Component Analysis algorithm to again, reduce the features. Default value is 0.8
                 e) format (optional)- Output format of file where clustered data is exported. Valid values are "excel" and "csv". Default value is "excel".

To get the output of k-means clustering,
import requests
url = "http://127.0.0.1:5000/clustering/kmeans"
r = requests.get(url=url)
print(r.text)
This will return all the documents with their cluster number.
Response is a JSON object of the form [{Cluster Number:(value), ISIN: (value), URL: (value)}] for all the documents
__________________________________________________________________________________________________________________________________________________________________________
4) Performing DBSCAN clustering on pre-processed data and exporting it

Clustering example:
import requests
import io
from PIL import image
url = "http://127.0.0.1:5000/clustering/dbscan?filepath=prep.xlsx&eps=0.3&min=1&format=csv"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()
Performs DBSCAN clustering on the pre-processed data and plots a scatter plot showing different clusters generated by the algorithm. It also exports the output to an excel file or csv file according to the user's input.
Input arguments- a) filepath (optional)- Path of excel sheet or csv file where the pre-processed data is stored. If argument is not given, the API will assume that the
                                         pre-processed data is present in the file "preprocess.json" in the form of a list containing a dictionary like {ISIN, URL, Data} as individual elements.
                 b) eps- Value of epsilon in DBSCAN algorithm i.e, the maximum distance between two samples for one to be considered as in the neighborhood of the other.
                 c) min- The number of samples (or total weight) in a neighborhood for a point to be considered as a core point. This includes the point itself.
                 d) thresh (optional)- The threshold value of variance in the variance threshold algorithm for reducing number of features. Default value is 0.001
                 e) pca_comp (optional)- The number of components in the Principal Component Analysis algorithm to again, reduce the features. Default value is 0.8
                 f) format (optional)- Output format of file where clustered data is exported. Valid values are "excel" and "csv". Default value is "excel".

To get the output of DBSCAN clustering,
import requests
url = "http://127.0.0.1:5000/clustering/dbscan"
r = requests.get(url=url)
print(r.text)
This will return all the documents with their cluster number.
Response is a JSON object of the form [{Cluster Number:(value), ISIN: (value), URL: (value)}] for all the documents
__________________________________________________________________________________________________________________________________________________________________________
5) Performing Agglomerative clustering on pre-processed data and exporting it

Clustering example:
import requests
import io
from PIL import image
url = "http://127.0.0.1:5000/clustering/agglomerative?filepath=prep.xlsx&k=5&format=csv"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()
Performs Agglomerative clustering on the pre-processed data and plots a scatter plot showing different clusters generated by the algorithm. It also exports the output to an excel file or csv file according to the user's input.
Input arguments- a) filepath (optional)- Path of excel sheet or csv file where the pre-processed data is stored. If argument is not given, the API will assume that the
                                         pre-processed data is present in the file "preprocess.json" in the form of a list containing a dictionary like {ISIN, URL, Data} as individual elements.
                 b) k- Number of clusters
                 c) thresh (optional)- The threshold value of variance in the variance threshold algorithm for reducing number of features. Default value is 0.001
                 d) pca_comp (optional)- The number of components in the Principal Component Analysis algorithm to again, reduce the features. Default value is 0.8
                 e) format (optional)- Output format of file where clustered data is exported. Valid values are "excel" and "csv". Default value is "excel".

To get the output of Agglomerative clustering,
import requests
url = "http://127.0.0.1:5000/clustering/agglomerative"
r = requests.get(url=url)
print(r.text)
This will return all the documents with their cluster number.
Response is a JSON object of the form [{Cluster Number:(value), ISIN: (value), URL: (value)}] for all the documents
__________________________________________________________________________________________________________________________________________________________________________
6) Performing Birch clustering on pre-processed data and exporting it

Clustering example:
import requests
import io
from PIL import image
url = "http://127.0.0.1:5000/clustering/birch?filepath=prep.xlsx&k=5&format=csv"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()
Performs Birch clustering on the pre-processed data and plots a scatter plot showing different clusters generated by the algorithm. It also exports the output to an excel file or csv file according to the user's input.
Input arguments- a) filepath (optional)- Path of excel sheet or csv file where the pre-processed data is stored. If argument is not given, the API will assume that the
                                         pre-processed data is present in the file "preprocess.json" in the form of a list containing a dictionary like {ISIN, URL, Data} as individual elements.
                 b) k- Number of clusters
                 c) thresh (optional)- The threshold value of variance in the variance threshold algorithm for reducing number of features. Default value is 0.001
                 d) pca_comp (optional)- The number of components in the Principal Component Analysis algorithm to again, reduce the features. Default value is 0.8
                 e) format (optional)- Output format of file where clustered data is exported. Valid values are "excel" and "csv". Default value is "excel".

To get the output of Birch clustering,
import requests
url = "http://127.0.0.1:5000/clustering/birch"
r = requests.get(url=url)
print(r.text)
This will return all the documents with their cluster number.
Response is a JSON object of the form [{Cluster Number:(value), ISIN: (value), URL: (value)}] for all the documents
__________________________________________________________________________________________________________________________________________________________________________
7) Getting cluster summary (number of documents in each cluster)

Example:
url = "http://127.0.0.1:5000/clustering/birch/summary"
r = requests.get(url=url)
print(r.text)
Returns JSON object of the form [{cluster number: number of docs in the cluster}] for all clusters

==========================================================================================================================================================================

User-written modules

Modules wrtten that are used by the API are:
1) kmeans- performs kmeans clustering
2) dbscan- performs DBSCAN clustering
3) agglomerative- performs agglomerative clustering
4) birch- performs birch clustering
5) extract- contains all function related to extracting, exporting data in different formats, converting json to lists and vice versa etc.
6) clean_file- contains all functions associated with data pre-processing
