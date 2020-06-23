from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import re


def remove_newline_char(text):
    text = text.replace("\n", " ")
    text = text.replace("\xa0", " ")
    return text


# remove commonly used words
def remove_stop_words(words, stop_words):
    cleaned_text = str()
    for i in words:
        if i in stop_words or len(i) <= 3:
            continue
        cleaned_text = cleaned_text + " " + i
    return cleaned_text


# remove punctuation marks
def remove_punctuations(text):
    punctuations = '[.+()\-=_,;:0-9$%"&*' + "'" + ']'
    text = re.sub(punctuations, "", text)
    return text


# function to remove special characters that cannot be removed by RegEx
def remove_unknown_char(text):
    # unknown_chars_ascii contains ascii values of some special characters that are present in the doc but cannot be removed using regex
    unknown_chars_ascii = [9642, 9618, 8212, 8220, 8221, 8217, 174, 167, 168, 183, 47, 8211]

    # unknown_chars is a list containing these special characters
    unknown_chars = [chr(x) for x in unknown_chars_ascii]

    for i in unknown_chars:
        # for character with ascii 8212 and 47 should be replaced by a whitespace
        if i == chr(8212) or i == chr(47):
            text = text.replace(i, " ")
        else:
            text = text.replace(i, "")
    return text


# lemmatize and stem every word and then concatenate into a string separated by whitespaces
def lemmatize_and_stem(text):
    wnl = WordNetLemmatizer()
    ps = PorterStemmer()
    txt = ""
    words = text.split()
    for i in range(len(words)):
        txt = txt + ps.stem(wnl.lemmatize(words[i])) + " "
    txt = txt.strip()
    return txt


# function for cleaning the text which will be given later to the preprocessing algorithm
def text_cleaning(text):
    # removes newline character '\n' and non-breaking space '\xa0' from the doc
    text = remove_newline_char(text)

    # convert all text to lowercase
    text = text.lower()

    # removes punctuation marks (!, ., ;, :, = etc) that are not useful for the preprocessing algorithm
    text = remove_punctuations(text)

    # removes unknown special characters which can't be removed from RegEx
    text = remove_unknown_char(text)

    # lemmatize the text to convert words into meaningful words
    text = lemmatize_and_stem(text)

    # removes stopwords that are commonly used words like has, is, not, yes, were etc.
    text = remove_stop_words(text.split(), stopwords.words('english'))
    return text
