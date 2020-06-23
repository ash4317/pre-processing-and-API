import clean_file
from bs4 import BeautifulSoup as bs
from urllib import request, parse, error
import math


link = 'file:///C:/Users/ASHWIN/Desktop/FinIQ/Assignments_FinIQ/NLP_Citi/ISIN_HTML/Bullet_Participation/dp105555_424b2-us1969494.htm'
data = request.urlopen(link).read().decode()
soup = bs(data, "html.parser")
text = soup.text
text = clean_file.text_cleaning(text)
text = text.split()
words = dict()
for word in text:
    words[word] = words.get(word, 0) + 1
arr = [[0 for i in range(len(words))] for j in range(len(words))]
keys = list(words.keys())

for i in range(len(words)):
    for j in range(len(text) - 4):
        if keys[i] in text[j:j+5]:
            arr[i][keys.index(text[j])] += 1

for i in range(len(arr)):
    for j in range(len(arr)):
        if i == j:
            arr[i][i] = 1
        else:
            arr[i][j] /= math.sqrt(words[keys[i]]*words[keys[j]])
