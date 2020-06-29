import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import VarianceThreshold
from sklearn.cluster import DBSCAN
from sklearn import metrics
import xlwt
from xlwt import Workbook


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

def sort_by_key(x):
    return x[0]


def sort(results):
    '''
    Sort the dictionary by cluster number
    '''
    results = list(results.items())
    results.sort(key=sort_by_key)
    return dict(results)


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
    
    # function to sort results by cluster number
    results = sort(results)
    return results


def export_to_excel(results):
    '''
    Writes all the doc URLs along with the cluster to which they belong
    '''
    fhand = Workbook()
    count = 1
    sheet = fhand.add_sheet('Sheet 1')
    style = xlwt.easyxf('font: bold 1')
    sheet.write(0, 0, 'Cluster Group Number', style)
    sheet.write(0, 1, 'Termsheet URL', style)
    for x, y in results.items():
        count += 2
        for url in y:
            sheet.write(count, 0, x)
            sheet.write(count, 1, url)
            count += 1
    fhand.save('Clustering Results.xls')


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

    # write results to excel sheet
    export_to_excel(results)