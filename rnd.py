import clean_file as cf
import extract as ex
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
import sklearn.metrics as metrics
from scipy.spatial.distance import cdist
import sys


def readlinks(path):
    '''
    Reads exed dataset and returns ISINs, Termsheet links and Text
    '''
    if ex.check(path, '.csv'):
        df = pd.read_csv(path)
    elif ex.check(path, '.xlsx'):
        df = pd.read_excel(path)

    urlList = df['Termsheet Link'].tolist()
    isinList = df['ISIN'].tolist()
    return isinList, urlList

if __name__ == "__main__":
    '''
    Main function
    '''
    start_time = time.time()
    steps = ['url', 'stopwords', 'stemming', 'lemmatization', 'unusual']
    ISINs, URLs = readlinks('ISINS_v3.xlsx')
    ISINs, URLs, textlist = ex.extract(ISINs, URLs, 30)
    print("---%s seconds" % (time.time() - start_time))
    data = cf.preprocessing(textlist, steps)
    print("Done")
    df = cf.tfidf(data)
    print(df.shape)
    tfidf = cf.varThresh_tfidf(df, 0.0001)
    print(tfidf.shape)
    ratio, score, pcadf = cf.pca_tfidf(tfidf, 0.9)
    print(pcadf)
    tfidf.to_csv('tf-idf.csv')
    filename = 'pre-processing.xlsx'
    fields = ['ISIN', 'Termsheet Link', 'Text'] 
    datalist = [ISINs, URLs, data]
    ex.exportexcel('abcd', 'ISINS_v3', filename, datalist, fields)

    
    print("---%s seconds" % (time.time() - start_time))



sns.set()

from sklearn.preprocessing import StandardScaler

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

#Number of termsheets vs range to be specified
number_of_termsheets = len(ISINs)

if number_of_termsheets <= 50 :
    start = 1
    end = number_of_termsheets
    jump = 1
elif number_of_termsheets <= 100 :
    start = 2
    end = number_of_termsheets
    jump = 2
elif number_of_termsheets <= 500 :
    start = 5
    end = 200
    jump = 5
elif number_of_termsheets <= 1500 :
    start = 5
    end = 250
    jump = 5
else :
    start = 10
    end = 400
    jump = 10
    
wcss = []
for i in range(start, end, jump):
    kmeans_pca = KMeans(n_clusters = i, init = 'k-means++', random_state= 42)
    kmeans_pca.fit(score)
    wcss.append(kmeans_pca.inertia_)


sys.path.append('..')

K = range(start, end, jump)
from kneed import KneeLocator
kn = KneeLocator(list(K), wcss, S=1.0, curve='convex', direction='decreasing')


#plotting elbow curve graph 

plt.figure(figsize =(10, 8))
plt.plot(range(start, end, jump), wcss, marker = 'o', linestyle = '--')
plt.xlabel("No.of Clusters")
plt.ylabel("WCSS")
plt.title("K-means with PCA clustering")
plt.vlines(kn.knee, plt.ylim()[0], plt.ylim()[1], linestyles='dashed')
plt.show()
print(f"Optimal value of k from elbow curve: {kn.knee}")


#using silhoette coef scores in the neighbourhood points
#to find optimal k value



X = score
sil_avg_score = []
maximum = 0
optimal_k = kn.knee

if start == 1 :
    start_pt = max(2, kn.knee- 10)
    end_pt = min(number_of_termsheets, kn.knee+ 10) 
else :
    start_pt = kn.knee - 10
    end_pt = kn.knee + 10

for i in range(start_pt, end_pt) :
    kmeans_model = KMeans(n_clusters= i, random_state=1).fit(X)
    labels = kmeans_model.labels_
    silhouette_avg = metrics.silhouette_score(X, labels, metric='cosine')
    sil_avg_score.append(silhouette_avg)
    if(silhouette_avg > maximum) :
        maximum = silhouette_avg
        optimal_k = i
    
# plotting silhouette score graphs

plt.figure(figsize =(10, 8))
plt.plot(range(start_pt,end_pt,1), sil_avg_score, marker = 'o', linestyle = '--')
plt.xlabel("No.of Clusters")
plt.ylabel("Silhouette Scores")
plt.title("Silhouette score variation")
plt.show()
print(f"Optimal value of k from silhouette scores: {optimal_k}")