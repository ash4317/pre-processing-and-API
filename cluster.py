import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import VarianceThreshold
from sklearn.cluster import DBSCAN
from sklearn import metrics


def calc_TFIDF(word_list, threshold):

    # object to transform words into vectors
    vectorizer = CountVectorizer()

    # for applying variance thrshold to reduce features
    selector = VarianceThreshold(threshold=threshold)

    '''
    Transform into TFIDF matrix, apply variance threshold to reduce features,
    print the order of TFIDF matrix and return the TFIDF matrix
    '''
    X = vectorizer.fit_transform(word_list)
    X = selector.fit_transform(X)
    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(X)
    print("\n")
    print(f"TFIDF matrix order: {tfidf.shape}")
    return tfidf


def show_results(links, clusters, results):
    '''
    This function will return a dictionary which stores all files in respective clusters
    '''
    for i in range(len(clusters)):
        if clusters[i] in results.keys():

            # if list is already made
            results[clusters[i]].append(links[i])
        else:

            # initialize value of the key to a list
            results[clusters[i]] = list()
            results[clusters[i]].append(links[i])
    return results


def eval_clusters(tfidf, word_list, links, epsilon, minSamples):
    '''
    This function applies DBSCAN clustering algorithm and prints clusters, number of features and Silhouette coefficient
    '''

    # stores all docs in different clusters
    results = dict()
    db = DBSCAN(eps=epsilon, min_samples=minSamples, metric='cosine').fit(tfidf)

    # get all clusters and clusters labels
    clusters = db.labels_.tolist()
    labels = db.labels_

    #Creating dictionary having doc with the corresponding cluster number.
    idea_3={'Idea':word_list, 'Cluster':clusters}

    # Converting it into a dataframe.
    frame_3=pd.DataFrame(idea_3,index=[clusters], columns=['Idea','Cluster'])

    print("\n")
    print(f"For epsilon:{epsilon}, minSamples:{minSamples}")

    #Print the counts of doc belonging to each cluster.
    print(frame_3['Cluster'].value_counts())
    print("\n")

    # Print the Silhouette Coefficient
    print(f"Silhouette Coefficient: {metrics.silhouette_score(tfidf, labels)}")

    # get docs in different clusters
    results = show_results(links, labels.tolist(), results)
    return results