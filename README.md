# Documentation for Pre-processing and Clustering API

Created by: Ashwin Kulkarni, Vaishnavi Patil

==========================================================================================================================================================================

Introduction


This API is created for extracting data from only ".htm" files present on some URL, pre-processing the data and using clustering algorithms to group them into various clusters on the basis of any similarity present between the documents.

==========================================================================================================================================================================

How to run this API locally


For Windows users: Open command prompt and go to the directory where this API along with the modules that it imports is located. Then, set the environment variables "FLASK_APP" and "FLASK_ENV" and run the flask API as follows-
set FLASK_APP=api.py
set FLASK_ENV=development
flask run

For MAC/Linux users: Open terminal window and go to the directory where this API along with the modules that it imports is located. Then, set the environment variables "FLASK_APP" and "FLASK_ENV" and run the flask API as follows-
export FLASK_APP=api.py
export FLASK_ENV=development
flask run

==========================================================================================================================================================================

API functions


1) Extracting and Exporting data present at URLs given in an excel sheet

Extracting data example:
url = "http://127.0.0.1:5000/extract?filepath=ISINS_v3.xlsx&no_of_docs=30"
r = requests.post(url=url)
print(r.text)
Input arguments- a) filepath- The path of the excel sheet where all the URLs where the htm files are located. Format of the excel sheet should be- (ISIN, URL)
                 b) no_of_docs (optional)- Number of URLs from which data is to be extracted. By default, it will extract from ALL the URLs.
Writes the extracted data into the file "extract.json".
To get extracted data,
url = "http://127.0.0.1:5000/extract"
r = requests.get(url=url)
print(r.text)

Exporting data example:
url = "http://127.0.0.1:5000/extract/export?filepath=extract.xlsx"
r = requests.post(url=url)
print(r.text)
Input arguments- a) filepath- Path of the file to which data is to be exported. The output file can be of formats ".csv" & ".xlsx"
The format of the exported file is- (ISIN, URL, text) for every htm file
__________________________________________________________________________________________________________________________________________________________________________
2) Pre-processing the extracted data and exporting it

Pre-processing data example:
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
url = "http://127.0.0.1:5000/preprocess"
r = requests.get(url=url)
print(r.text)

Exporting pre-processed data example:
url = "http://127.0.0.1:5000/preprocess/export?filepath=prep.xlsx"
r = requests.post(url=url)
print(r.text)
Input arguments- a) filepath- Path of the file to which pre-processed data is to be exported. The output file can be of formats ".csv" & ".xlsx"
The format of the exported file is- (ISIN, URL, text) for every htm file
__________________________________________________________________________________________________________________________________________________________________________
3) Performing k-means clustering on pre-processed data and exporting it

Clustering example:
url = "http://127.0.0.1:5000/clustering/kmeans?filepath=prep.xlsx&k=4"
r = requests.post(url=url)
img = Image.open(io.BytesIO(r.content))
img.show()
Performs k-means clustering on the pre-processed data and plots a scatter plot showing different clusters generated by the algorithm.
Input arguments- a) filepath (optional)- Path of excel sheet or csv file where the pre-processed data is stored. If argument is not given, the API will assume that the
                                         pre-processed data is present in the file "preprocess.json" in the form of a list containing a dictionary like {ISIN, URL, Data} as individual elements.
                 b) k- Value of k in k-means algorithm which is the number of clusters to be made
                 c) thresh (optional) - The threshold value of variance in the variance threshold algorithm for reducing number of features. Default value is 0.001
                 d) pca_comp (optional) - The number of components in the Principal Component Analysis algorithm to again, reduce the features. Default value is 0.8
To get the output of k-means clustering,
url = "http://127.0.0.1:5000/clustering/kmeans"
r = requests.get(url=url)
print(r.text)
This will return all the documents with their cluster number.