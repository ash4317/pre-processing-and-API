import clean_file
import sys
import math
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

    for i in range(1, sheet.nrows):
        links.append(sheet.cell_value(i, 1))

    return links


def get_words(text, all_words):
    text = text.split()
    for word in text:
        all_words[word] = all_words.get(word, 0) + 1
    return all_words



def clean_all_files(links, all_words):
    '''
    This function will return a list consisting of all the words in all the cleaned files.
    '''

    # list that will contain cleaned text
    cleaned_text = list()

    count = 0

    for url in links:

        # using beautiful soup to parse the .htm files
        try:
            data = request.urlopen(url).read().decode()
        except:
            
        soup = bs(data, "html.parser")
        text = soup.text
        text = clean_file.text_cleaning(text)
        cleaned_text.append(text)
        count += 1
        print(f"URLs checked: {count}")
    
    all_words = get_words(cleaned_text, all_words)
    return cleaned_text, all_words





if __name__ == "__main__":

    # get all the links
    links = list()
    all_words = dict()
    links = get_files(links)

    # get all the text
    cleaned_text = list()
    cleaned_text, all_words = clean_all_files(links, all_words)

    f = open("all words and counts.txt", 'w')
    for i, j in all_words.items():
        f.write(i + " : " + str(j) + "\n")
    f.close()