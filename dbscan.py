'''
Performs DBSCAN clustering
'''

# Modules imported
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import metrics
from sklearn.cluster import DBSCAN
import extract as ex


def dbscan_clustering(db_eps, min_points, tfidf, isin_list, urllist):
    '''
    Performs DBSCAN clustering
    '''
    db = DBSCAN(eps=db_eps , min_samples=min_points, metric='cosine')
    dbscan = db.fit(tfidf)
    clusters = dbscan.labels_.tolist()
    y_dbscan = db.fit_predict(tfidf)
    clustered_data={'ISIN':isin_list, 'URL':urllist,'Cluster':clusters} #Creating dict having url with the corresponding cluster number.
    frame=pd.DataFrame(clustered_data, columns=['ISIN','URL','Cluster']) # Converting it into a dataframe.

    sil = metrics.silhouette_score(tfidf, dbscan.labels_)
    cal= metrics.calinski_harabasz_score(tfidf, dbscan.labels_)
    db = metrics.davies_bouldin_score(tfidf, dbscan.labels_)
    scores = [sil, cal, db]
    '''
    print(f"Silhouette score: {sil}")
    print(f"Calinski Harabasz score: {cal}")
    print(f"Davies Bouldin score: {db}")
    print("\n")
    '''
    return frame, scores


def visualize_scatter(db_eps, min_points, tfidf):
    '''
    Plots scatter plot for clustering
    '''
    db = DBSCAN(eps=db_eps , min_samples=min_points, metric='cosine')
    y_dbscan = db.fit_predict(tfidf)
    fig = plt.figure()
    plt.scatter(tfidf[:, 0], tfidf[:, 1], c=y_dbscan, s=50, cmap='viridis')
    plt.title("DBSCAN", figure=fig)

    return fig
