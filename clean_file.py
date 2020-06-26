'''
Module which is imported in 'main.py' which cleans the text
'''

from nltk.corpus import stopwords, words
from nltk.stem import PorterStemmer, WordNetLemmatizer
import re
from unidecode import unidecode


def rmv_URL(text):
    '''
    removes URL links (if any) from the files
    '''
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)


def rmv_newline_char(text):
    '''
    removes newline character '\n' and non-breaking space '\xa0' from the doc
    '''
    text = text.replace("\n", " ")
    text = text.replace("\xa0", " ")
    return text


def rmv_stopWords(words):
    '''
    removes stopwords like has, and, the etc.
    '''
    del_words = stopwords.words('english')
    extra = ["inc", "citigroup", "markets", "price", "would", "without", "follow"]
    del_words += extra
    cleaned_text = str()
    for i in words:
        if i in del_words or len(i) <= 3:
            continue
        cleaned_text = cleaned_text + " " + i
    return cleaned_text


def unusual_words(text):
    '''
    Remove words that are not in the english vocab (meaningless words)
    '''
    text_vocab = set(w.lower() for w in text.split() if w.isalpha())
    english_vocab = set(w.lower() for w in words.words())
    unusual = text_vocab - english_vocab
    data = " ".join(w for w in sorted(text_vocab - unusual))
    return data



def rmv_punctAndNos(text):
    '''
    remove punctuation marks and numbers
    '''
    punctuations = '[.+()\-=_,;:0-9$#\[\]%"&*' + "'" + ']'
    text = re.sub(punctuations, "", text)
    return text



def rmv_unknown_char(text):
    '''
    function to remove special characters that cannot be removed by RegEx
    '''
    # unknown_chars_ascii contains ascii values of some special characters that are present in the doc but cannot be removed using regex
    unknown_chars_ascii = [9642, 9618, 8212, 8220, 8221, 8217, 174, 167, 168, 183, 47, 8211, 8226]

    # unknown_chars is a list containing these special characters
    unknown_chars = [chr(x) for x in unknown_chars_ascii]

    for i in unknown_chars:
        # for character with ascii 8212 and 47 should be replaced by a whitespace

        if i == chr(8212) or i == chr(47):
            text = text.replace(i, " ")
        else:
            text = text.replace(i, "")
    return text



def stemming(text):
    '''
    Apply stemming to the text to reduce all words to their root
    '''
    ps = PorterStemmer()
    return " ".join(ps.stem(word) for word in text.split())



def lemmatize(text):
    '''
    lemmatize and stem every word and then concatenate into a string separated by whitespaces
    '''
    wnl = WordNetLemmatizer()
    words = text.split()
    words = [wnl.lemmatize(w) for w in words]
    words = [wnl.lemmatize(w, pos = "a") for w in words]
    words = [wnl.lemmatize(w, pos = "v") for w in words]
    return " ".join(word for word in words)




def rmv_URLs(text):
    '''
    remove all URLs
    '''
    txt = ""
    words = text.split()
    for word in words:
        if re.search('^www.*', word) or re.search('^us.*', word):
            continue
        txt += word + " "
    txt = txt.strip()
    return txt



def text_cleaning(text):
    '''
    function for cleaning the text which will be given later to the preprocessing algorithm
    '''
    # will be able to process all characters
    text = unidecode(text)
    text = rmv_newline_char(text)

    # convert all text to lowercase
    text = text.lower()

    text = rmv_punctAndNos(text)
    text = rmv_unknown_char(text)
    text = unusual_words(text)
    text = lemmatize(text)
    text = stemming(text)
    text = rmv_stopWords(text.split())
    text = rmv_URLs(text)
    return text
