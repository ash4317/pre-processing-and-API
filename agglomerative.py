from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram
import extract as ex

def agglomerative_clustering(k, tfidf, isin_list, urllist):

    agg = AgglomerativeClustering(n_clusters=k)
    agglo = agg.fit(tfidf)
    clusters = agglo.labels_.tolist()

    clustered_data={'ISIN':isin_list, 'URL':urllist,'Cluster':clusters} #Creating dict having url with the corresponding cluster number.
    frame=pd.DataFrame(clustered_data, columns=['ISIN','URL','Cluster']) # Converting it into a dataframe.

    #Print the counts of doc belonging to each cluster.
    #print("\n")
    #print('Clustering Algorithm: Agglomerative')
    #print("\n")
    #print(frame['Cluster'].value_counts())

    #to print clustered urls/docs grouped by cluster id
    '''
    grouped=frame.groupby('Cluster')
    for name,group in grouped:
        print(name)
        print(group)
    '''

    #calculate silheoutte score, etc
    sil = metrics.silhouette_score(tfidf, agglo.labels_)
    cal= metrics.calinski_harabasz_score(tfidf, agglo.labels_)
    db = metrics.davies_bouldin_score(tfidf, agglo.labels_)

    scores = [sil, cal, db]
    '''
    print(f"Silhouette score: {sil}")
    print(f"Calinski Harabasz score: {cal}")
    print(f"Davies Bouldin score: {db}")
    print("\n")
    '''

    return frame, scores


def visualize_scatter(k, tfidf):
    agg = AgglomerativeClustering(n_clusters=k)    
    y_agglo = agg.fit_predict(tfidf)
    fig = plt.figure()
    plt.scatter(tfidf[:, 0], tfidf[:, 1], c=y_agglo, s=50, cmap='viridis')
    plt.title("Agglomerative", figure=fig)

    return fig


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack([model.children_, counts]).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)

def dendro_plot(k, tfidf):
    agg = AgglomerativeClustering(n_clusters=k)    
    agglo = agg.fit(tfidf)
    plt.title('Hierarchical Clustering Dendrogram')
    # plot the top three levels of the dendrogram
    plot_dendrogram(agglo, truncate_mode='level', p=k)
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    plt.show()