'''
This module is responsible for the preprocessing. It uses the 'clean_file' module which will clean the text and return it.
'''

# user written modules
import clean_file as cf

# in-built modules
from urllib import request, error, parse
from bs4 import BeautifulSoup as bs
from unidecode import unidecode
import json


def get_words(text, words_in_docs):
    '''
    Returns all the distinct words present along with number of docs in which they appear.
    '''
    all_words = dict()
    text = text.split()
    for word in text:
        all_words[word] = all_words.get(word, 0) + 1
    
    # This loop checks for all the distinct words stored in the dictionary 'all_words' and will increment count by 1 which will measure the number of docs where word appears.
    for word in all_words.keys():
        words_in_docs[word] = words_in_docs.get(word, 0) + 1
    return words_in_docs


def clean_all_files(links, words_in_docs, word_list):
    '''
    This function will return a list consisting of all the words in all the cleaned files.
    '''
    # keeps count of number of URLs processed.
    count = 0

    for url in links:

        # using beautiful soup to parse the .htm files
        # using error check because all files may not be able to get parsed
        try:
            data = request.urlopen(url).read().decode()
        except:
            continue
            
        soup = bs(data, "html.parser")
        text = soup.text

        # returns preprocessed text.
        text = unidecode(text)
        text = cf.rmv_newline_char(text)
        text = text.lower()
        text = cf.rmv_punctAndNos(text)
        text = cf.rmv_unknown_char(text)
        text = cf.rmv_unusual_words(text)
        text = cf.lemmatize(text)
        text = cf.stemming(text)
        text = cf.rmv_stopWords(text.split())
        text = cf.rmv_URLs(text)

        # Preprocessed text in every .htm file is added to the list 'word_list'
        word_list.append(text)

        # returns the number of docs in which words appear
        words_in_docs = get_words(text, words_in_docs)
        count += 1
        print(f"URLs checked: {count}")
    
    return words_in_docs, word_list


def write_preprocessed(word_list):
    '''
    Writes the preprocessed data into the file 'preprocessed.json'
    '''
    f = open("preprocessed-1.json", 'w')
    js = json.dumps(word_list)
    f.write(js)
    f.close()
    


def get_commonWords(words_in_docs, no_of_docs):
    '''
    Returns all words which are present in more than 80% of total docs and less than 3 docs
    '''
    return [word for word, count in words_in_docs.items() if count > (0.7 * no_of_docs) or count <= 2]