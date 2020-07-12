from bs4 import BeautifulSoup
import os
import pandas as pd
import codecs
from urllib.request import urlopen


def generateReport(scoreDfs, allUsefulSheetAttr, allTemplateAttr, allSheetAttr, reportPath):
    '''
    The helper function which prepares the excelsheet
    by combining the two rows obtained from the two
    dictionaries.
    '''
    if os.path.isfile(reportPath):
        writer = pd.ExcelWriter(reportPath, engine='openpyxl', mode="a")
    else:
        writer = pd.ExcelWriter(reportPath, engine='openpyxl')

    frames = []
    for name, df in scoreDfs.items():
        frames.append(df)
    result1 = pd.concat(frames, sort=False)
    result1.index.name = "Termsheet Name"
    result1.to_excel(writer, sheet_name="Match & Miss-match Matrix")

    index = []
    attrs = []
    for sheetName, attr in allUsefulSheetAttr.items():
        index.append(sheetName)
        attrs.append(attr)

    result2 = pd.DataFrame(data=attrs, index=index)
    result2.to_excel(writer, sheet_name="Attributes from Sheet")

    index = []
    attrs = []
    for tempName, attr in allTemplateAttr.items():
        index.append(tempName)
        attrs.append(attr)

    result3 = pd.DataFrame(data=attrs, index=index)
    result3.to_excel(writer, sheet_name="Attributes from Template")

    index = []
    attrs = []
    for tempName, attr in allSheetAttr.items():
        index.append(tempName)
        attrs.append(attr)

    result4 = pd.DataFrame(data=attrs, index=index)
    result4.to_excel(writer, sheet_name="All Attributes from Sheet")

    writer.close()


def generateDataFrames(scoreDfs, allUsefulSheetAttr, allTemplateAttr, allSheetAttr):

    allDfs = {}
    frames = []
    for name, df in scoreDfs.items():
        frames.append(df)
    result1 = pd.concat(frames, sort=False)
    result1.index.name = "Termsheet Name"
    allDfs["Match & Miss-match Matrix"] = pd.DataFrame.to_dict(result1)

    index = []
    attrs = []
    for sheetName, attr in allUsefulSheetAttr.items():
        index.append(sheetName)
        attrs.append(attr)

    result2 = pd.DataFrame(data=attrs, index=index)
    allDfs["Attributes from Sheet"] = pd.DataFrame.to_dict(result2)

    index = []
    attrs = []
    for tempName, attr in allTemplateAttr.items():
        index.append(tempName)
        attrs.append(attr)

    result3 = pd.DataFrame(data=attrs, index=index)
    allDfs["Attributes from Template"] = pd.DataFrame.to_dict(result3)

    index = []
    attrs = []
    for tempName, attr in allSheetAttr.items():
        index.append(tempName)
        attrs.append(attr)

    result4 = pd.DataFrame(data=attrs, index=index)
    allDfs["All Attributes from Sheet"] = pd.DataFrame.to_dict(result4)

    return allDfs


def display_result(scores, sheetName):
    '''
    It sorts the scores in descending order. The scores are
    then written in an Excelsheet and save in root
    '''
    data = {}
    columns = []
    for key, value in scores.items():
        columns.append(key + f' ({value[1]})')
        data[key + f' ({value[1]})'] = [str(value[0]) + ' |'
                                        + str(value[1] - value[0]) + ' |'
                                        + str(value[2] - value[0])]
    df = pd.DataFrame(data, columns=columns, index=[sheetName])
    return df


def match(tempAttr, sheetAttr):
    '''
    It is a utility function which returns the total
    number of attributes common to both and the total
    number of attributes in the template
    '''
    count = 0
    for attr in tempAttr:
        if attr in sheetAttr:
            count += 1

    return count, len(tempAttr), len(sheetAttr)


def getAttributes(doc, isSheet, keyTerms, debug=False):
    '''
    The function is responsible for extracting the attributes
    from the template or termsheet. It returns a list of
    attributes for matching.
    '''
    availableAttributes = set()
    for td in doc.find_all("td"):
        x = td.text.lower()
        heading = "".join([letter for letter in x if letter.isalpha()]).lower()
        if heading in keyTerms:
            availableAttributes.add(heading)

    return availableAttributes


def main(sheetContents, tempLocs, keyListLoc, reportPath=""):
    '''
    The main driver function for the application. It accepts the
    folder containing the application and the location of the
    termsheet as input. It generates the locations of all the
    templates and matches them with the termsheet

    It accepts 4 arguments:
    sheetContents: A dictionary of ISINs and the URL
    tempLocs: A directory containing the templates
    keyListLoc: The location of the file containing the key terms
    reportPath: An optional argument, if specified will generate an
    excelsheet at the entered path otherwise will return a dictionary
    of dataFrames which are also in the form a dictionary
    '''
    keys = open(keyListLoc).readlines()
    keyTerms = set()
    for element in keys:
        keyTerms.add(element.strip("\n"))

    scores = {}
    excelData = {}
    allUsefulSheetAttr = {}
    allTemplateAttr = {}
    allSheetAttr = {}

    for key, value in sheetContents.items():
        ext = key.split(".")[-1]
        if ext != "htm" and ext != "html":
            continue

        # This was the best codec to give the least UnicodeEncodeError
        fileSheet = value
        sheetName = key

        try:
            sheetSoup = BeautifulSoup(fileSheet, "lxml")
            allUsefulSheetAttr[sheetName] = getAttributes(
                sheetSoup, True, keyTerms, False)
            allSheetAttr[sheetName] = getAttributes(
                sheetSoup, True, keyTerms, True)

            # Accessing one template recursively
            # in the templates Location folder
            for tempLoc in tempLocs:
                fileTemp = codecs.open(os.path.join(
                    tempLoc), "r", encoding="latin-1")
                tempName = os.path.basename(tempLoc)

                try:
                    tempSoup = BeautifulSoup(fileTemp, "lxml")
                    allTemplateAttr[tempName] = getAttributes(
                        tempSoup, False, keyTerms, False)

                    # Getting the common attributes in the
                    # termsheet and the template
                    numMatches, tempTotal, sheetTotal = match(
                        allTemplateAttr[tempName],
                        allUsefulSheetAttr[sheetName])

                    scores[tempName] = [
                        numMatches, tempTotal, sheetTotal]

                except UnicodeDecodeError:
                    print(f"{tempName} could not decoded")

            # To prepare the dictionary for the Sheet1
            # i.e. the first Matrix containing the the
            # matches and mis-matches for a pair of template
            # and termsheet
            excelData[sheetName] = display_result(scores, sheetName)

        except UnicodeEncodeError:
            print(f"{sheetName} could not be decoded")

        except Exception as e:
            print(repr(e))
            print(f"{sheetName}: Something went wrong for this termsheet")

        # To debug for a single sheet, uncomment the "break" below
        # break

    if reportPath == "":
        return generateDataFrames(excelData, allUsefulSheetAttr,
                                  allTemplateAttr, allSheetAttr)
    else:
        generateReport(excelData, allUsefulSheetAttr,
                       allTemplateAttr, allSheetAttr, reportPath)


if __name__ == '__main__':
    tempLoc = "./Templates"
    tempLocs = []
    sheetLocs = []

    for root, _, tempNames in os.walk(tempLoc):
        for tempName in tempNames:
            tempLocs.append(os.path.join(root, tempName))

    keyListLoc = "./keys.txt"
    reportPath = "./test.xlsx"
    urls = {'US17326YZV19': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007930/dp108304_424b2-us1972721.htm',
            'US17326YJJ64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319008018/dp108385_424b2-us1972668.htm',
            'US17326YU388': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319008084/dp108463_424b2-us1972667.htm',
            'US17326YNL64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009058/dp109430_424b2-us1972617.htm',
            'US17326YUM64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007911/dp108280_424b2-us1972550.htm',
            'US17326YRV01': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009050/dp109447_424b2-us1972547.htm',
            'US17326YPB64': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319007828/dp108206_424b2-us1972545.htm',
            'US17326Y4M50': 'https://www.sec.gov/Archives/edgar/data/831001/000095010319009060/dp109497_424b2-us1972484.htm'}
    sheetContents = {}
    for key, value in urls.items():
        html = urlopen(value).read()
        x = value.split('/')[-1]
        sheetContents[x] = html

    allDfs = main(sheetContents, tempLocs, keyListLoc)

    writer = pd.ExcelWriter(reportPath, engine='xlsxwriter')
    for key, value in allDfs.items():
        pd.DataFrame(value).to_excel(writer, sheet_name=key)

    writer.close()
