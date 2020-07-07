from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.cluster import Birch
import extract as ex

def birch_clustering(k, tfidf, isin_list, urllist):

    birch = Birch(n_clusters=k)
    bi = birch.fit(tfidf)
    clusters = bi.labels_.tolist()

    clustered_data={'ISIN':isin_list, 'URL':urllist,'Cluster':clusters} #Creating dict having url with the corresponding cluster number.
    frame=pd.DataFrame(clustered_data, columns=['ISIN','URL','Cluster']) # Converting it into a dataframe.

    #Print the counts of doc belonging to each cluster.
    '''
    print("\n")
    print('Clustering Algorithm: Birch')
    print("\n")
    print(frame['Cluster'].value_counts())
    
    #to print clustered urls/docs grouped by cluster id
    grouped=frame.groupby('Cluster')
    for name,group in grouped:
        print(name)
        print(group)
    '''

    #calculate silheoutte score, etc
    sil = metrics.silhouette_score(tfidf, bi.labels_)
    cal= metrics.calinski_harabasz_score(tfidf, bi.labels_)
    db = metrics.davies_bouldin_score(tfidf, bi.labels_)
    scores = [sil, cal, db]
    '''
    print(f"Silhouette score: {sil}")
    print(f"Calinski Harabasz score: {cal}")
    print(f"Davies Bouldin score: {db}")
    print("\n")
    '''
    return frame, scores

def visualize_scatter(k, tfidf):
    birch = Birch(n_clusters=k)
    y_birch = birch.fit_predict(tfidf)
    fig = plt.figure()
    plt.scatter(tfidf[:, 0], tfidf[:, 1], c=y_birch, s=50, cmap='viridis')
    plt.title("Birch", figure=fig)

    return fig

   

    