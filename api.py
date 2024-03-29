'''
The main flask REST API which uses all the other created modules and performs clustering, pre-processing
'''

# Modules imported
from flask import Flask, request, make_response, send_file, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask_restful import Api, Resource, reqparse
from urllib.request import urlopen
from threading import Thread
import json
import io
import os
import shutil
import datetime
import concurrent.futures
import matplotlib as plt
plt.rcParams.update({'figure.max_open_warning': 0}) # To suppress Matplotlib warning for multiple figures

# The below two imports are for the
# programs for brute-force and non
# brute force methods
import BruteForceReportGen
import NonBruteForceReportGen
import extract as ex        # Module for web scrapping and file operations
import clean_file as cf     # Module for pre-processing
# Modules for clustering algorithms
import kmeans
import dbscan
import birch
import agglomerative as ag
import userlogs as ul       # Module for creating user-specific log files
import logging

# defining program as a flask api
app = Flask(__name__)
api = Api(app)


# Set directory for all log files
cwd = os.getcwd()
LOG_FOLDER = os.path.join(cwd,'LOGS')
# Set parameters for root log file
LOG_FORMAT = "%(levelname)s %(name)s %(asctime)s - %(message)s"
logging.basicConfig(filename=os.path.join(LOG_FOLDER, 'rootlog.log'), level=logging.DEBUG, format= LOG_FORMAT)
logger = logging.getLogger()


# Defining the Global Parameters for ReportGeneration here
tempLoc = "./Templates"
keyListLoc = "./keys.txt"
JSON_file_Location = "./JSONdumps/"


class ExtractData(Resource):
    '''
    For extracting data and getting the extracted data
    '''
    def post(self):
        '''
        POST request extracts the data and writes it into the file "extract_username_filename_date_time.json"
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('no_of_docs', type=str)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to extract data.')
            args['fname'] = args['fname'].split('.')[0]
            try:
                content = request.json
                ISINs = list(content.keys())
                URLs = list(content.values())
                logger.debug('Extracted links and ISINs from JSON object.')
            except:
                logger.error('Failed to extract links and ISINs from JSON object.')
                return {
                        'data':'',
                        'message':'Error in json object parameter',
                        'status':'error'
                        }, 400
                        
            # if 'no_of_docs' not given, ALL URLs are reqested.
            if not args['no_of_docs']:
                args['no_of_docs'] = 'all'
                logger.debug('Extracting all documents.')
            ISINs, URLs, text = ex.extract(ISINs, URLs, args['no_of_docs'])
            jsondata = ex.tojson(ISINs, URLs, text)
            ex.write_json(jsondata, ex.give_filename('extract_' + args['uname'] + '_' + args['fname'], '.json'))
            logger.info('Made entry for extracted data in datafile successfully.')

            # success message
            return {
                    'data':'',
                    'message':'Data extracted',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred:' + repr(e))
            return {
                    'data':'',
                    'message': e,
                    'status':'error'
                    }, 400

    def get(self):
        '''
        GET request returns the extracted data back to the user as a JSON object
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get extracted data.')
            args['fname'] = args['fname'].split('.')[0]
            try:
                logger.debug('Searching for requested datafile')
                data = ex.get_recent_file('extract_' + args['uname'] + '_' + args['fname'], '.json')
            
            # error message if traceback occurs
            except Exception as e:
                logger.exception('Exception occurred while reading datafile:'+repr(e))
                return {
                        'data':'', 
                        'message':'Error in reading file', 
                        'status':'error'
                        }, 400
            
            logger.info('Get request served successfully')
            return {
                    'data':ex.read_json(data),  
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred:' + repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class ExportExtractedData(Resource):
    '''
    For exporting the extracted data into excel or csv file (if the user wishes to)
    '''
    def post(self):
        '''
        POST request exports the data
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
            print(args['filepath'])
            
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to export extracted data.')

            args['fname'] = args['fname'].split('.')[0]
            try:
                jsondata = ex.read_json(ex.get_recent_file('extract_' + args['uname'] + '_' + args['fname'], '.json'))
                ISINs, URLs, text = ex.jsontolists(jsondata)
            
            # error message if traceback occurs
            except Exception as e:
                logger.exception('Exception occurred while reading datafile:'+repr(e))
                return {
                        'data':'',
                        'message':'Could not fetch data to export',
                        'status':'error'
                        }, 400

            if os.path.exists(ex.get_recent_file(args['filepath'].split('.')[0] + '_' + args['uname'] + '_' + args['fname'], '.xlsx')):
                os.remove(ex.get_recent_file(args['filepath'].split('.')[0] + '_' + args['uname'] + '_' + args['fname'], '.xlsx'))

            # if file is not of excel or csv, then return error code 400. Else, add to excel/csv as the user requires
            logger.debug('Checking if filepath has valid format')
            if ex.check(args['filepath'], '.xlsx'):
                logger.debug('Exporting data to excel file')
                ex.exportexcel(args['uname'], args['fname'], filename = args['filepath'], datalist = [ISINs, URLs, text])
            elif ex.check(args['filepath'], '.csv'):
                logger.debug('Exporting data to csv file')
                ex.exportcsv(args['uname'], args['fname'], filename=args['filepath'], field1 = ISINs, field2 = URLs, field3 = text)
            else:
                logger.error('Invalid format for export file')
                return {
                        'data':'',
                        'message':'Invalid format. Valid formats are .csv and .xlsx',
                        'status':'error'
                        }, 400
            # Return success message
            logger.info('Exported successfully')
            return send_file(ex.get_recent_file(args['filepath'].split('.')[0] + '_' + args['uname'] + '_' + args['fname'], '.xlsx')) 

        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred:' + repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400




class PreProcess(Resource):
    '''
    For performing text pre-processing on the extracted data.
    User can select any number of pre-processing techniques out of the 5 given.
    '''
    def post(self):
        '''
        POST request performs the pre-processing
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('steps', action='append')
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to pre-process data.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']
            argset = set(args)
            # if external filepath for extracted data is not given, then this means that extraction is done using this API itself and is stored in the file "extract_username_filename_date_time.json"
            if not args['filepath']:
                try:
                    logger.debug('Reading data from datafile')
                    jsondata = ex.read_json(ex.get_recent_file('extract_' + args['uname'] + '_' + fname, '.json'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    logger.exception('Failed to read datafile')
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                logger.debug('Reading dataset file')
                ISINs, URLs, text = ex.readdataset(args['filepath'])
            
            # text pre-processing function call
            logger.debug('Pre-processing text data')
            data = cf.preprocessing(text, args['steps'])
            jsondata = ex.tojson(ISINs, URLs, data)
            logger.debug('Pre-processed data')
            
            # writes the pre-processed text into the file "preprocess.json"
            logger.debug('Writting pre-processed data to datafile')
            ex.write_json(jsondata, ex.give_filename('preprocess_' + args['uname'] + '_' + fname, '.json'))
            logger.debug('Made entry of pre-processed data in datafile successfully')

            return {
                    'data':'',
                    'message':'Pre-processed!',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':repr(e),
                    'status':'error'
                    }, 400

    def get(self):
        '''
        GET request returns the extracted data back to the user as a JSON object
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get pre-processed data.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']
            # Read json file to get pre-processed data
            try:
                logger.debug('Reading pre-processed datafile')
                data = ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json')
            except Exception as e:
                logger.error('Error in reading pre-processed data file'+repr(e))
                return {
                        'data':'', 
                        'message':'Error in reading file', 
                        'status':'error'
                        }, 400
            logger.info('Get request for pre-processed data served successfully')
            return {
                    'data':ex.read_json(data),  
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400



class ExportPrepData(Resource):
    '''
    For exporting pre-processed data into excel or csv file (if the user wishes to)
    '''
    
    def post(self):
        '''
        POST request exports the data
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to export pre-processed data.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']
            # Read json file to get pre-processed data
            try:
                logger.debug('Reading pre-processed datafile.')
                jsondata = ex.read_json(ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json'))
                ISINs, URLs, text = ex.jsontolists(jsondata)
            except:
                logger.error('Error while reading pre-processed datafile.')
                return {
                        'data':'',
                        'message':'Could not fetch data to export',
                        'status':'error'
                        }, 400
                
            if os.path.exists(ex.get_recent_file(args['filepath'].split('.')[0] + '_' + args['uname'] + '_' + args['fname'], '.xlsx')):
                os.remove(ex.get_recent_file(args['filepath'].split('.')[0] + '_' + args['uname'] + '_' + args['fname'], '.xlsx'))

            # if file is not of excel or csv, then return error code 400. Else, add to excel/csv as the user requires
            if ex.check(args['filepath'], '.xlsx'):
                logger.debug('Exporting pre-processed data to excel file.')
                ex.exportexcel(args['uname'], args['fname'], filename = args['filepath'], datalist = [ISINs, URLs, text])
            elif ex.check(args['filepath'], '.csv'):
                logger.debug('Exporting pre-processed data to csv file.')
                ex.exportcsv(args['uname'], args['fname'], filename=args['filepath'], field1 = ISINs, field2 = URLs, field3 = text)
            else:
                logger.error('Invalid file format.')
                return {
                        'data':'',
                        'message':'Invalid format. Valid formats are .csv and .xlsx',
                        'status':'error'
                        }, 400
            logger.info('Exported pre-processed data successfully.')
            return send_file(ex.get_recent_file(args['filepath'].split('.')[0] + '_' + args['uname'] + '_' + args['fname'], '.xlsx')) 

        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400
    


class Kmeans(Resource):
    '''
    Performs k means clustering to group all the documents into various clusters.
    '''
    def post(self):
        '''
        POST request will perform clustering and return a scatter plot providing a visual comprehension of how clustering is done
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('k', type=int)
            parser.add_argument('thresh', type=float)
            parser.add_argument('pca_comp', type=float)
            parser.add_argument('format', type=str)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            # Check for username and filename in the URL
            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400

            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to cluster documents.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    logger.debug('Reading datafile..')
                    jsondata = ex.read_json(ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except Exception as e:
                    logger.exception('Failed to read datafile'+repr(e))
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                logger.debug('Reading dataset')
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                logger.debug('Setting default value of threshold for Variance Threshold to 0.0001')
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                logger.debug('Setting default value of number of components for PCA to 0.8')
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            logger.debug('Calculating tf-idf')
            df = cf.tfidf(text)
            logger.debug('Calculating variance threshold')
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            logger.debug('Applying PCA')
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            logger.debug('Applying K-Means algorithm')
            frame, scores, clust = kmeans.kmeans_clustering(args['k'],ratio,ISINs, URLs)
            logger.debug('Sorting clusters')
            frame = frame.sort_values(by=['Cluster'])
            logger.debug('Converting to JSON format')
            datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
            clusts = frame['Cluster'].to_list()
            clusts.sort()
            clusters = {}
            i = 0
            for c in clusts:
                try:
                    clusters['Cluster '+str(c)].add(i)
                except:
                    clusters['Cluster '+str(c)] = {i}
                i += 1
            for c in clusters:
                clusters[c] = len(clusters[c])
            
            
            clusterData = dict()
            clusterData['clust'] = clust
            clusterData['summary'] = clusters

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            logger.debug('Writting summary')
            ex.write_json(clusterData, ex.give_filename('summary_' + args['uname'], '.json'))
            logger.debug('Writting clustering information to datafile')
            ex.write_json(datajson, ex.give_filename('cluster_' + args['uname'], '.json'))
            
            # getting coordinates of all points in scatter plot (every point represents a document)
            x_coords = list(ratio[:, 0])
            y_coords = list(ratio[:, 1])
            data = list()
            
            # returning all coordinates as a list of dictionaries
            for i in range(len(x_coords)):
                data.append({'x':x_coords[i], 'y':y_coords[i]})

            return {
                'data':data,
                'message':'',
                'status':'success'
            }, 200
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400

    def get(self):
        '''
        GET request returns the extracted data back to the user as a JSON object
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get clustering details.')
            
            # Read JSON file to get clustered data
            try:
                logger.debug('Reading datafile for clustered data')
                data = ex.get_recent_file('cluster_' + args['uname'], '.json')
            except:
                logger.exception('Error in reading datafile')
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            logger.info('Get request for clustered data served successfully')
            return {
                    'data':ex.read_json(data),  
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400



class DBSCAN(Resource):
    '''
    Performs DBSCAN clustering to group all the documents into various clusters.
    '''
    def post(self):
        '''
        POST request will perform clustering and return a scatter plot providing a visual comprehension of how clustering is done
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('eps', type=float)
            parser.add_argument('min', type=int)
            parser.add_argument('thresh', type=float)
            parser.add_argument('pca_comp', type=float)
            parser.add_argument('format', type=str)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            # Check for username and filename in the URL
            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400

            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to cluster documents.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    logger.debug('Reading datafile..')
                    jsondata = ex.read_json(ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    logger.exception('Failed to read datafile')
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                logger.debug('Reading dataset')
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                logger.debug('Setting default value of threshold for Variance Threshold to 0.0001')
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                logger.debug('Setting default value of number of components for PCA to 0.8')
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            logger.debug('Calculating tf-idf')
            df = cf.tfidf(text)
            logger.debug('Calculating variance threshold')
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            logger.debug('Applying PCA')
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            logger.debug('Applying DBSCAN algorithm')
            frame, scores, clust = dbscan.dbscan_clustering(args['eps'], args['min'], ratio, ISINs, URLs)
            logger.debug('Sorting clusters')
            frame = frame.sort_values(by=['Cluster'])
            logger.debug('Converting to JSON format')
            datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
            clusts = frame['Cluster'].to_list()
            clusts.sort()
            clusters = {}
            i = 0
            for c in clusts:
                try:
                    clusters['Cluster '+str(c)].add(i)
                except:
                    clusters['Cluster '+str(c)] = {i}
                i += 1
            for c in clusters:
                clusters[c] = len(clusters[c])
            
            clusterData = dict()
            clusterData['clust'] = clust
            clusterData['summary'] = clusters

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            logger.debug('Writting summary')
            ex.write_json(clusterData, ex.give_filename('summary_' + args['uname'], '.json'))
            logger.debug('Writting clustering information to datafile')
            ex.write_json(datajson, ex.give_filename('cluster_' + args['uname'], '.json'))

            # getting coordinates of all points in scatter plot (every point represents a document)
            x_coords = list(ratio[:, 0])
            y_coords = list(ratio[:, 1])
            data = list()
            
            # returning all coordinates as a list of dictionaries
            for i in range(len(x_coords)):
                data.append({'x':x_coords[i], 'y':y_coords[i]})

            return {
                'data':data,
                'message':'',
                'status':'success'
            }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400
    
    
    def get(self):
        '''
        GET request returns the extracted data back to the user as a JSON object
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get clustering details.')
            
            try:
                logger.debug('Reading datafile for clustered data')
                data = ex.get_recent_file('cluster_' + args['uname'], '.json')
            except:
                logger.exception('Error in reading datafile')
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            logger.info('Get request for clustered data served successfully')
            return {
                    'data':ex.read_json(data),  
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class Agglomerative(Resource):
    '''
    Performs Agglomerative clustering to group all the documents into various clusters.
    '''
    
    def post(self):
        '''
        POST request will perform clustering and return a scatter plot providing a visual comprehension of how clustering is done
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('k', type=int)
            parser.add_argument('thresh', type=float)
            parser.add_argument('pca_comp', type=float)
            parser.add_argument('format', type=str)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to cluster documents.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    logger.debug('Reading datafile..')
                    jsondata = ex.read_json(ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    logger.exception('Failed to read datafile')
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                logger.debug('Reading dataset')
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                logger.debug('Setting default value of threshold for Variance Threshold to 0.0001')
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                logger.debug('Setting default value of number of components for PCA to 0.8')
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            logger.debug('Calculating tf-idf')
            df = cf.tfidf(text)
            logger.debug('Calculating variance threshold')
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            logger.debug('Applying PCA')
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            logger.debug('Applying Agglomerative algorithm')
            frame, scores, clust = ag.agglomerative_clustering(args['k'],ratio,ISINs, URLs)
            logger.debug('Sorting clusters')
            frame = frame.sort_values(by=['Cluster'])
            logger.debug('Converting to JSON format')
            datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
            clusts = frame['Cluster'].to_list()
            clusts.sort()
            clusters = {}
            i = 0
            for c in clusts:
                try:
                    clusters['Cluster '+str(c)].add(i)
                except:
                    clusters['Cluster '+str(c)] = {i}
                i += 1
            for c in clusters:
                clusters[c] = len(clusters[c])
            
            clusterData = dict()
            clusterData['clust'] = clust
            clusterData['summary'] = clusters

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            logger.debug('Writting summary')
            ex.write_json(clusterData, ex.give_filename('summary_' + args['uname'], '.json'))
            logger.debug('Writting clustering information to datafile')
            ex.write_json(datajson, ex.give_filename('cluster_' + args['uname'], '.json'))

            # getting coordinates of all points in scatter plot (every point represents a document)
            x_coords = list(ratio[:, 0])
            y_coords = list(ratio[:, 1])
            data = list()
            
            # returning all coordinates as a list of dictionaries
            for i in range(len(x_coords)):
                data.append({'x':x_coords[i], 'y':y_coords[i]})

            return {
                'data':data,
                'message':'',
                'status':'success'
            }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400
    
    def get(self):
        '''
        GET request returns the extracted data back to the user as a JSON object
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get clustering details.')
            
            try:
                logger.debug('Reading datafile for clustered data')
                data = ex.get_recent_file('cluster_' + args['uname'], '.json')
            except:
                logger.exception('Error in reading datafile')
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            logger.info('Get request for clustered data served successfully')
            return {
                    'data':ex.read_json(data), 
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class Birch(Resource):
    '''
    Performs Birch clustering to group all the documents into various clusters.
    '''
    
    def post(self):
        '''
        POST request will perform clustering and return a scatter plot providing a visual comprehension of how clustering is done
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('k', type=int)
            parser.add_argument('thresh', type=float)
            parser.add_argument('pca_comp', type=float)
            parser.add_argument('format', type=str)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to cluster documents.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    logger.debug('Reading datafile..')
                    jsondata = ex.read_json(ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    logger.exception('Failed to read datafile')
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                logger.debug('Reading dataset')
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                logger.debug('Setting default value of threshold for Variance Threshold to 0.0001')
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                logger.debug('Setting default value of number of components for PCA to 0.8')
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            logger.debug('Calculating tf-idf')
            df = cf.tfidf(text)
            logger.debug('Calculating variance threshold')
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            logger.debug('Applying PCA')
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            logger.debug('Applying Birch algorithm')
            frame, scores, clust = birch.birch_clustering(args['k'],ratio,ISINs, URLs)
            logger.debug('Sorting clusters')
            frame = frame.sort_values(by=['Cluster'])
            logger.debug('Converting to JSON format')
            datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
            clusts = frame['Cluster'].to_list()
            clusts.sort()
            clusters = {}
            i = 0
            for c in clusts:
                try:
                    clusters['Cluster '+str(c)].add(i)
                except:
                    clusters['Cluster '+str(c)] = {i}
                i += 1
            for c in clusters:
                clusters[c] = len(clusters[c])
            
            clusterData = dict()
            clusterData['clust'] = clust
            clusterData['summary'] = clusters

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            logger.debug('Writting summary')
            ex.write_json(clusterData, ex.give_filename('summary_' + args['uname'], '.json'))
            logger.debug('Writting clustering information to datafile')
            ex.write_json(datajson, ex.give_filename('cluster_' + args['uname'], '.json'))

            # getting coordinates of all points in scatter plot (every point represents a document)
            x_coords = list(ratio[:, 0])
            y_coords = list(ratio[:, 1])
            data = list()
            
            # returning all coordinates as a list of dictionaries
            for i in range(len(x_coords)):
                data.append({'x':x_coords[i], 'y':y_coords[i]})

            return {
                'data':data,
                'message':'',
                'status':'success'
            }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400

    def get(self):
        '''
        GET request returns the extracted data back to the user as a JSON object
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get clustering details.')
            
            try:
                logger.debug('Reading datafile for clustered data')
                data = ex.get_recent_file('cluster_' + args['uname'], '.json')
            except:
                logger.exception('Error in reading datafile')
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            logger.info('Get request for clustered data served successfully')
            return {
                    'data':ex.read_json(data), 
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class ClusterSummary(Resource):
    '''
    GET request returns a summary of clustering done to the user
    '''
    def get(self):
        '''
        GET request returns the extracted data back to the user as a JSON object
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            parser.add_argument('content_type', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['content_type']:
                args['content_type'] = 'summary'
                
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get clustering summary.')            
            
            try:
                logger.debug('Reading datafile for clustering summary')
                data = ex.get_recent_file('summary_' + args['uname'], '.json')
            except:
                logger.exception('Error in reading datafile')
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            logger.info('Get request for clustering summary served successfully')

            # returns summary of clustering
            if args['content_type'] == 'summary':
                logger.debug('Returning summary')
                return {
                        'data':ex.read_json(data)['summary'], 
                        'status':'success'
                        }, 200
            
            # returns cluster number of every document
            else:
                logger.debug('Returning clustering details')
                return {
                        'data':ex.read_json(data)['clust'],
                        'status':'success'
                        }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400



class Elbow(Resource):
    '''
    Plots elbow curve and return optimal k value
    '''
    def post(self):
        '''
        POST request will return a elbow curve of different k values for Kmeans clustering
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('thresh', type=float)
            parser.add_argument('pca_comp', type=float)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to plot elbow curve.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    logger.debug('Reading datafile..')
                    jsondata = ex.read_json(ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    logger.exception('Failed to read datafile')
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                logger.debug('Reading dataset')
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                logger.debug('Setting default value of threshold for Variance Threshold to 0.0001')
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                logger.debug('Setting default value of number of components for PCA to 0.8')
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            logger.debug('Calculating tf-idf')
            df = cf.tfidf(text)
            logger.debug('Calculating variance threshold')
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            logger.debug('Applying PCA')
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])

            # plots elbow curve ad returns it
            logger.debug('Plotting elbow curve')
            dict_elbow, K = kmeans.visualize_elbow(len(ISINs),ratio)
            # writes optimal k value into "optK.json" 
            logger.debug('Writing optimal k value')
            ex.write_json(int(K), ex.give_filename('elbow_k_' + args['uname'], '.json'))
            logger.info('Obtained optimal value of K using Elbow curve successfully')

            return {
                'data':dict_elbow,
                'message':'',
                'status':'success'
            }, 200
                        
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400

    def get(self):
        '''
        GET request returns the optimal k value
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get optimal k value')
            
            try:
                logger.debug('Reading datafile for optimal k value after elbow method')
                data = ex.get_recent_file('elbow_k_' + args['uname'], '.json')
            except:
                logger.exception('Error in reading datafile')
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            logger.info('Get request for optimal k value served successfully')
            return {
                    'data':ex.read_json(data), 
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class Silhouette(Resource):
    '''
    Performs k means clustering to group all the documents into various clusters.
    '''
    def post(self):
        '''
        POST request will perform clustering and return a scatter plot providing a visual comprehension of how clustering is done
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('filepath', type=str)
            parser.add_argument('thresh', type=float)
            parser.add_argument('pca_comp', type=float)
            parser.add_argument('uname', type=str)
            parser.add_argument('fname', type=str)
            args = parser.parse_args()

            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            if not args['fname']:
                return {
                        'data':'',
                        'message':'Give file name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested for optimal value of K using Silhouette.')
            try:
                strrep = args['fname'].split('.', 1)[1]
                fname = args['fname'].replace('.' + strrep, '')
            except:
                fname = args['fname']

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    logger.debug('Reading datafile..')
                    jsondata = ex.read_json(ex.get_recent_file('preprocess_' + args['uname'] + '_' + fname, '.json'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    logger.exception('Failed to read datafile')
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                logger.debug('Reading dataset')
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                logger.debug('Setting default value of threshold for Variance Threshold to 0.0001')
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                logger.debug('Setting default value of number of components for PCA to 0.8')
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            logger.debug('Calculating tf-idf')
            df = cf.tfidf(text)
            logger.debug('Calculating variance threshold')
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            logger.debug('Applying PCA')
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            jsonk = ex.read_json(ex.get_recent_file('elbow_k_' + args['uname'], '.json'))
            kn_knee = int(jsonk)
            logger.debug('Applying silhouette coefficient')
            dict_sil, optimal_k = kmeans.silhouetteScore(len(ISINs), ratio, kn_knee)

            # writes optimal k value into "optK.json" 
            logger.debug('Writting optimal k')
            ex.write_json(int(optimal_k), ex.give_filename('optimal_k_' + args['uname'], '.json'))
            logger.info('Obtained optimal value of k using Silhouette score successfully')

            return {
                'data':dict_sil,
                'message':'',
                'status':'success'
            }, 200
                        
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400

    
    def get(self):
        '''
        GET request returns the optimal k value
        '''
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()
            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get optimal k value')
            
            try:
                logger.debug('Reading datafile for optimal k value after silhouette')
                data = ex.get_recent_file('optimal_k_' + args['uname'], '.json')
            except:
                logger.exception('Error in reading datafile')
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            logger.info('Get request for optimal k value served successfully')
            return {
                    'data':ex.read_json(data), 
                    'message':'',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class Clear(Resource):
    '''
    Removes all generated files when the user logs out
    '''
    def delete(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()
            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Logging off...deleting all cached files')
            
            names = [x for x in os.listdir() if args['uname'] in x and '.json' in x and 'extract_' not in x and 'preprocess_' not in x]

            for fname in names:
                os.remove(fname)
            
            # removing cache directory
            path = os.path.join(os.getcwd(), '__pycache__')
            shutil.rmtree(path)

            logger.info('Cleared cache')
            return {
                    'data': '', 
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class SendLogs(Resource):
    '''
    Send log file of requesting user
    '''
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()
            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to get log file..')
            logger.info('Sending log file')
            return send_file(os.path.join(LOG_FOLDER, args['uname']+'.log')) 
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class ClearLogs(Resource):
    '''
    Removes log file of requesting user
    '''
    def delete(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str)
            args = parser.parse_args()
            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
                        
            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(LOG_FOLDER ,args['uname']+'.log'), level= logging.DEBUG)
            logger.info('Requested to clear log file..')
            f = open(os.path.join(LOG_FOLDER ,args['uname']+'.log'), "r+")
            f.seek(0)
            f.truncate()

            logger.info('Cleared log file')
            return {
                    'data': '', 
                    'message': '',
                    'status':'success'
                    }, 200
        
        # error message if traceback occurs
        except Exception as e:
            logger.exception('Exception occurred: '+repr(e))
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400


class ReportGeneration(Resource):
    '''
    This the component of the API that is
    used to handle what the report generation
    for the template - termsheet matching
    '''

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uname', type=str,
                            help="Enter the name of the user",
                            required=True)
        parser.add_argument('kind', type=int)
        args = parser.parse_args()
        user = args['uname']

        # by default, kind = 1 , i.e. Brute force method used
        if not args['kind']:
            args['kind'] = 1
        
        report_method = args['kind']

        if report_method != 1 and report_method != 2:
            return {
                'data':'', 
                'message':'Invalid value for argument "kind". Valid values are 1 or 2', 
                'status':'error'
            }, 400

        # exception handling and adding entry into the log file
        logger = ul.setup_logger(args['uname'], os.path.join(
            LOG_FOLDER, args['uname'] + '.log'), level=logging.DEBUG)
        logger.info('Requested for report generation.')

        if os.path.isfile(os.path.join(JSON_file_Location, f"{user}.json")):
            os.remove(os.path.join(JSON_file_Location, f"{user}.json"))
            logger.info(f'Older JSON Dump for {user} has been deleted')

        try:
            logger.debug('Checking for json input')
            content = request.json
        except Exception as e:
            logger.debug('Could not extract URLs' + repr(e))
            return {
                "data": "",
                "message": "Could not extract URLs",
                "status": "error"
            }, 400

        sheetLocs = {}
        logger.debug('Fetching URLs')
        for url in content.values():
            try:
                logger.debug(f"Fetching {url} URL")
                html = urlopen(url).read()
                x = url.split('/')[-1]
                sheetLocs[x] = html
            except Exception:
                logger.exception(f"The url: {url} could not be fetched")
                print(f"The url: {url} could not be fetched")
                continue

        tempLocs = []
        for root, _, tempNames in os.walk(tempLoc):
            for tempName in tempNames:
                tempLocs.append(os.path.join(root, tempName))

        def myfunc(report_method, sheetLocs, tempLocs, keyListLoc, user):
            if report_method == 1:
                logger.debug(
                    "Using bruteforce method for report generation")
                data = BruteForceReportGen.main(
                    sheetLocs, tempLocs, keyListLoc)
            elif report_method == 2:
                logger.debug(
                    "Using non-bruteforce method for report generation")
                data = NonBruteForceReportGen.main(
                    sheetLocs, tempLocs, keyListLoc)

            user_excel = open(f"{JSON_file_Location}{user}.json", "w")
            json.dump(data, user_excel)
            logger.info("Report generated successfully")

        dataThread = Thread(target=myfunc, kwargs={
            "report_method": report_method,
            "sheetLocs": sheetLocs,
            "tempLocs": tempLocs,
            "keyListLoc": keyListLoc,
            "user": user
        })
            
        logger.info("Report generation has started.")
        dataThread.start()
            # success message
        return {
            'data': '',
            'message': 'Report generation started.',
            'status': 'success'
        }, 200

        

    def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('uname', type=str,
                                help="Enter the name of the user",
                                required=True)
            args = parser.parse_args()
            user = args['uname']

            # exception handling and adding entry into the log file
            logger = ul.setup_logger(args['uname'], os.path.join(
                LOG_FOLDER, args['uname'] + '.log'), level=logging.DEBUG)
            logger.info('Requested for report generation.')

            flag = 0
            logger.debug('Searching for JSON Dump')
            for root, _, jsonDumps in os.walk(JSON_file_Location):
                for jsonDump in jsonDumps:
                    if jsonDump == user + ".json":
                        flag = 1
                        logger.debug('Found JSON Dump')
                        reqJSON = os.path.join(root, jsonDump)
                        break

            if flag == 0:
                logger.error(
                    'Could not find the JSON Dump, the file is not prepared yet')
                return {
                    "data": "",
                    "message": "Could not find the JSON Dump, the file is not prepared yet",
                    "status": "error"
                }, 400

            fileContents = open(reqJSON, "r").readline()
            logger.debug('Get request served successfully')
            return fileContents


class Test(Resource):
    '''
    Test class to check if API is responding
    '''
    def get(self):
        return {
            'message': 'API for preprocessing and clustering!'
        }



# Adding all URL paths
api.add_resource(ReportGeneration, "/report")
api.add_resource(ExtractData, '/extract')
api.add_resource(ExportExtractedData, '/extract/export')
api.add_resource(PreProcess, '/preprocess')
api.add_resource(ExportPrepData, '/preprocess/export')
api.add_resource(Kmeans, '/clustering/kmeans')
api.add_resource(DBSCAN, '/clustering/dbscan')
api.add_resource(Agglomerative, '/clustering/agglomerative')
api.add_resource(Birch, '/clustering/birch')
api.add_resource(ClusterSummary, '/clustering/summary')
api.add_resource(Elbow, '/clustering/elbow')
api.add_resource(Silhouette, '/clustering/silhouette')
api.add_resource(Clear, '/clear')
api.add_resource(SendLogs, '/getlog')
api.add_resource(ClearLogs, '/clearlog')
api.add_resource(Test, '/')


# main function
if __name__ == '__main__':
    app.run(debug=True, threaded=True)