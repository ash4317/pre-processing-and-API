import clean_file
import os
from bs4 import BeautifulSoup as bs
from urllib import request, parse, error
import xlrd


def get_files(links):
    '''
    Function that will return list of URLs of all the .htm files in a list
    '''

    # defining path of the excel sheet
    file_path = os.getcwd().replace('\\', '/') + '/ISINS_Dataset/ISINS.xlsx'

    # wb = excel workbook object. Row starts from index 0
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)

    for i in range(1, 500):
        links.append(sheet.cell_value(i, 1))
    return links


def get_words(text, words_in_docs, fhand):
    all_words = dict()
    text = text.split()
    for word in text:
        fhand.write(word + " ")
        all_words[word] = all_words.get(word, 0) + 1
    
    for word in all_words.keys():
        words_in_docs[word] = words_in_docs.get(word, 0) + 1
    return words_in_docs



def clean_all_files(links, words_in_docs):
    '''
    This function will return a list consisting of all the words in all the cleaned files.
    '''
    count = 0
    try:
        os.remove("preprocessed.txt")
    except:
        pass

    f = open("preprocessed.txt", 'a')

    for url in links:

        # using beautiful soup to parse the .htm files
        try:
            data = request.urlopen(url).read().decode()
        except:
            continue
            
        soup = bs(data, "html.parser")
        text = soup.text
        text = clean_file.text_cleaning(text)
        words_in_docs = get_words(text, words_in_docs, f)
        count += 1
        print(f"URLs checked: {count}")
    
    f.close()
    return words_in_docs


if __name__ == "__main__":
    '''
    Main function
    '''

    # get all the links
    links = list()
    words_in_docs = dict()
    links = get_files(links)

    # get all the text
    words_in_docs = clean_all_files(links, words_in_docs)

    f = open("docs where word appear.txt", 'w')
    for i, j in words_in_docs.items():
        f.write(i + " : " + str(j) + "\n")
    f.close()

    f = open("common_words.txt", 'w')
    for i in words_in_docs.keys():
        if words_in_docs[i] > 40:
            f.write(i + "\n")
    f.close()
