from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import metrics
from sklearn.cluster import DBSCAN
import extract as ex


def dbscan_clustering(db_eps, min_points, tfidf, isin_list, urllist):

    db = DBSCAN(eps=db_eps , min_samples=min_points, metric='cosine')
    dbscan = db.fit(tfidf)
    clusters = dbscan.labels_.tolist()
    y_dbscan = db.fit_predict(tfidf)

    clustered_data={'ISIN':isin_list, 'URL':urllist,'Cluster':clusters} #Creating dict having url with the corresponding cluster number.
    frame=pd.DataFrame(clustered_data, columns=['ISIN','URL','Cluster']) # Converting it into a dataframe.

    #Print the counts of doc belonging to each cluster.
    '''
    print("\n")
    print('Clustering Algorithm: DBSCAN')
    print("\n")
    print(frame['Cluster'].value_counts())

    #to print clustered urls/docs grouped by cluster id
    grouped=frame.groupby('Cluster')
    for name,group in grouped:
        print(name)
        print(group)
    '''

    #calculate silheoutte score, etc
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

    results = ex.show_results(isin_list, urllist, clusters)
    # write results to excel sheet
    ex.export_to_excel(results, 'dbscan results.xls')

    return frame, [1,2,3]


def visualize_scatter(db_eps, min_points, tfidf):
    db = DBSCAN(eps=db_eps , min_samples=min_points, metric='cosine')
    y_dbscan = db.fit_predict(tfidf)
    fig = plt.figure()
    plt.scatter(tfidf[:, 0], tfidf[:, 1], c=y_dbscan, s=50, cmap='viridis')
    plt.title("DBSCAN", figure=fig)

    return fig


    