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
    return frame, scores


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
