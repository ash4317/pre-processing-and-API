'''
Performs k means clustering
'''

# Modules imported
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import metrics
import extract as ex
import time
import pandas as pd
import seaborn as sns
import numpy as np
from scipy.spatial.distance import cdist
from kneed import KneeLocator


def kmeans_clustering(k,tfidf,isin_list, urllist): #isin_list is the list of ISIN files numbers in the order of the preprocessed data.
    '''
    Performs k means clustering
    '''
    num_clusters = k
    kmeans = KMeans(n_clusters=num_clusters)
    km = kmeans.fit(tfidf)
    clusters = km.labels_.tolist()
    clustered_data={'ISIN':isin_list, 'URL':urllist, 'Cluster':clusters} #Creating dict having url with the corresponding cluster number.
    frame=pd.DataFrame(clustered_data, columns=['ISIN','URL','Cluster']) # Converting it into a dataframe.

    sil = metrics.silhouette_score(tfidf, km.labels_)
    cal= metrics.calinski_harabasz_score(tfidf, km.labels_)
    db = metrics.davies_bouldin_score(tfidf, km.labels_)
    scores = [sil, cal, db]
    '''
    print(f"Silhouette score: {sil}")
    print(f"Calinski Harabasz score: {cal}")
    print(f"Davies Bouldin score: {db}")
    print("\n")
    '''
    return frame, scores, clusters


def visualize_scatter(k, tfidf):
    '''
    Plots scatter plot for clustering
    '''
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(tfidf)
    y_kmeans = kmeans.predict(tfidf)
    fig = plt.figure()
    plt.scatter(tfidf[:, 0], tfidf[:, 1], c=y_kmeans, s=50, cmap='viridis')
    plt.title("K-means", figure=fig)
    return fig

def visualize_elbow(number_of_termsheets, score):
    #Number of termsheets vs range to be specified
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
        kmeans_pca = KMeans(n_clusters=i)
        kmeans_pca.fit(score)
        wcss.append(kmeans_pca.inertia_)

    #implementation kneedle algorithm

    K = range(start, end, jump)
    from kneed import KneeLocator
    kn = KneeLocator(list(K), wcss, S=1.0, curve='convex', direction='decreasing')

    #plotting elbow curve graph 

    fig = plt.figure(figsize =(10, 8))
    plt.plot(range(start, end, jump), wcss, marker = 'o', linestyle = '--')
    plt.xlabel("No.of Clusters")
    plt.ylabel("WCSS")
    plt.vlines(kn.knee, plt.ylim()[0], plt.ylim()[1], linestyles='dashed')
    plt.title("K-means with PCA clustering", figure=fig)
    #plt.show()
    return fig, kn.knee

    
def silhouetteScore(number_of_termsheets, score, kn_knee):
    X = score
    sil_avg_score = []
    maximum = 0
    optimal_k = kn_knee
    
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

    if start == 1 :
        start_pt = max(2, kn_knee- 10)
        end_pt = min(number_of_termsheets, kn_knee+ 10) 
    else :
        start_pt = kn_knee - 10
        end_pt = kn_knee + 10

    for i in range(start_pt, end_pt) :
        kmeans_model = KMeans(n_clusters= i, random_state=1).fit(X)
        labels = kmeans_model.labels_
        silhouette_avg = metrics.silhouette_score(X, labels, metric='cosine')
        sil_avg_score.append(silhouette_avg)
        if(silhouette_avg > maximum) :
            maximum = silhouette_avg
            optimal_k = i
        
    # plotting silhouette score graphs

    fig = plt.figure(figsize =(10, 8))
    plt.plot(range(start_pt,end_pt,1), sil_avg_score, marker = 'o', linestyle = '--')
    plt.xlabel("No.of Clusters")
    plt.ylabel("Silhouette Scores")
    plt.title("Silhouette score variation", figure=fig)

    return fig, optimal_k