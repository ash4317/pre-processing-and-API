import clean_file
import sys
import math
import os
from bs4 import BeautifulSoup as bs
from urllib import request, parse, error



# function to get all the .htm file paths from the three folders
def file_names_paths(paths, names, extension):
    path = 'file:///' + os.getcwd().replace('\\', '/') + '/ISIN_HTML/'
    for i in range(len(names)):
        paths.append(path + extension + names[i] + '.htm')
    return paths



# writes the cleaned text into csv format in the respective directories with respective names as in the termsheet names
def writing_and_TFIDF(text, docname, idf, doc_tf_vector, count, unique_words):
    cleaned_words = text.split()

    # TF of all words in a single doc
    tf = dict()

    # open the file with the file_name same as in the termsheet .htm file name and write into it in csv format
    f = open('pre_processed.csv', 'a')
    print("Writing to file ...")
    for word in cleaned_words:
        f.write(word + " ")
        unique_words[word] = unique_words.get(word, 0) + 1
        tf[word] = tf.get(word, 0) + 1 # number of times word appears in the document

    print("Calculating idf and tf for words in one doc ...")
    for word in tf.keys():
        idf[word] = idf.get(word, 0) + 1 # number of docs in which word appears
        tf[word] = tf[word]/len(cleaned_words) # tf(word) calculated
    
    doc_tf_vector[docname] = tf
    f.close()
    count = count + 1
    print("File written:", count)
    return doc_tf_vector, idf, count, unique_words



# extract the .htm file, clean the text, write it into the directory in csv format
def extract_and_write(paths, names, doc_tf_vector, idf, count, unique_words):
    for i in range(len(names)):

        # using beautiful soup to parse the .htm files
        data = request.urlopen(paths[i]).read().decode()
        soup = bs(data, "html.parser")
        text = soup.text

        # text cleaning function written in the 'clean_file.py' file
        print("Cleaning file ...")
        text = clean_file.text_cleaning(text)

        # writes the cleaned text into a file
        doc_tf_vector, idf, count, unique_words = writing_and_TFIDF(text, names[i], idf, doc_tf_vector, count, unique_words)

    return doc_tf_vector, idf, count, unique_words



def write_to_file(content, file_name):
    f = open(file_name, 'w')
    for i, j in content.items():
        f.write(i + " : " + str(j) + "\n")
    f.close()
#------------------------------------------------------------------------MAIN FUNCTION-------------------------------------------------------------------------------


# these lists will contain all the file paths
bullet_participation_files = list()
interest_rates_files = list()
snowball_files = list()


# these lists will contain all the .htm file names
print("Getting file names from Bullet_Participation ...")
bullet_participation = [y.replace('.htm', '') for y in [x for x in os.walk(os.getcwd() + '/ISIN_HTML/Bullet_Participation/')][0][2]]
print("Getting file names from Interest_Rates ...")
interest_rates = [y.replace('.htm', '') for y in [x for x in os.walk(os.getcwd() + '/ISIN_HTML/Interest_Rates/')][0][2]]
print("Getting file names from Snowball ...")
snowball = [y.replace('.htm', '') for y in [x for x in os.walk(os.getcwd() + '/ISIN_HTML/Snowball/')][0][2]]


# these lists contain all the .htm file paths which is used to parse the files
print("Getting file paths from Bullet_Participation ...")
bullet_participation_files = file_names_paths(bullet_participation_files, bullet_participation, 'Bullet_Participation/')
print("Getting file paths from Interest_Rates ...")
snowball_files = file_names_paths(snowball_files, snowball, 'Snowball/')
print("Getting file paths from Snowball ...")
interest_rates_files = file_names_paths(interest_rates_files, interest_rates, 'Interest_Rates/')


# Inverse Document Frequency dictionary: number of docs in which every word appears {word: no. of docs in which word appears}
idf = dict()

# Contains True Frequency for all words in every doc {docname: tf vector for all words}
doc_tf_vector = dict()

# total number of docs
no_of_docs = len(bullet_participation) + len(interest_rates) + len(snowball)
print("Total docs:", no_of_docs)

try:
    os.remove("pre_processed.csv")
except:
    pass

count = 0
unique_words = dict()

# our main function call which will perform the data cleaning and writing to files
doc_tf_vector, idf, count, unique_words = extract_and_write(bullet_participation_files, bullet_participation, doc_tf_vector, idf, count, unique_words)
doc_tf_vector, idf, count, unique_words = extract_and_write(interest_rates_files, interest_rates, doc_tf_vector, idf, count, unique_words)
doc_tf_vector, idf, count, unique_words = extract_and_write(snowball_files, snowball, doc_tf_vector, idf, count, unique_words)


# calculating IDF
final_idf = dict()
print("Calculating IDF ...")
for key in idf.keys():
    final_idf[key] = math.log(no_of_docs/idf[key])



# tfidf dictionary
tfidf_vector = dict()



print("Calculating TFIDF ...")
for name in doc_tf_vector.keys():
    tfidf_singledoc = dict()
    tf = dict()
    tf = doc_tf_vector[name]
    for key in tf.keys():
        tfidf_singledoc[key] = tf[key]*final_idf[key]
    def sorting(x):
        return x[1]
    tfidf_singledoc = list(tfidf_singledoc.items())
    tfidf_singledoc.sort(reverse=True, key=sorting)
    tfidf_vector[name] = dict(tfidf_singledoc)


# This will show number of docs where all the individual words appear
write_to_file(idf, "number of docs where words appear.txt")

# This will show all the words and their counts
write_to_file(unique_words, "all words and counts.txt")


# tfidf values for all the words in all the docs
f = open("tfidf.txt", 'w')
c = '-'
for key, dictionary in tfidf_vector.items():
    f.write(key + ".htm" + "\n")
    for k, l in dictionary.items():
        f.write(k + " : " + str(l) + "\n")
    f.write(c * 30 + "\n")
f.close()
