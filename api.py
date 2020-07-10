'''
The main flask REST API which uses all the other created modules and performs clustering, pre-processing
'''

# Modules imported
from flask import Flask, request, make_response, send_file
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask_restful import Api, Resource, reqparse
import extract as ex
import clean_file as cf
import kmeans
import dbscan
import birch
import agglomerative as ag
import json
import io
import os
import datetime

# defining program as a flask api
app = Flask(__name__)
api = Api(app)


class ExtractData(Resource):
    '''
    For extracting data and getting the extracted data
    '''
    def post(self):
        '''
        POST request extracts the data and writes it into the file "extract.json"
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']
            try:
                content = request.json
                ISINs = list(content.keys())
                URLs = list(content.values())
            except:
                return {
                        'data':'',
                        'message':'Error in json object parameter',
                        'status':'error'
                        }, 400
            if not args['no_of_docs']:
                args['no_of_docs'] = 'all'
            ISINs, URLs, text = ex.extract(ISINs, URLs, args['no_of_docs'])
            jsondata = ex.tojson(ISINs, URLs, text)
            ex.write_json(jsondata, ex.give_filename(args['uname'] + '_' + fname + '_' + 'extract', '.json'))
            return {
                    'data':'',
                    'message':'Data extracted',
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']
            try:
                data = ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'extract')
            except:
                return {
                        'data':'', 
                        'message':'Error in reading file', 
                        'status':'error'
                        }, 400
            return {
                    'data':ex.read_json(data), 
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']
            try:
                jsondata = ex.read_json(ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'extract'))
                ISINs, URLs, text = ex.jsontolists(jsondata)
            except:
                return {
                        'data':'',
                        'message':'Could not fetch data to export',
                        'status':'error'
                        }, 400
            if os.path.exists(args['filepath']):
                os.remove(args['filepath'])

            # if file is not of excel or csv, then return error code 400. Else, add to excel/csv as the user requires
            if ex.check(args['filepath'], '.xlsx'):
                ex.exportexcel(filename = args['filepath'], datalist = [ISINs, URLs, text])
            elif ex.check(args['filepath'], '.csv'):
                ex.exportcsv(filename=args['filepath'], field1 = ISINs, field2 = URLs, field3 = text)
            else:
                return {
                        'data':'',
                        'message':'Invalid format. Valid formats are .csv and .xlsx',
                        'status':'error'
                        }, 400

            return {
                    'data':'',
                    'message':'Exported!',
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']
            argset = set(args)
            # if external filepath for extracted data is not given, then this means that extraction is done using this API itself and is stored in the file "extract.json"
            if not args['filepath']:
                try:
                    jsondata = ex.read_json(ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'extract'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                ISINs, URLs, text = ex.readdataset(args['filepath'])
            
            # text pre-processing function call
            data = cf.preprocessing(text, args['steps'])
            jsondata = ex.tojson(ISINs, URLs, data)

            # writes the pre-processed text into the file "preprocess.json"
            ex.write_json(jsondata, ex.give_filename(args['uname'] + '_' + fname + '_' + 'preprocess', '.json'))
            return {
                    'data':'',
                    'message':'Pre-processed!',
                    'status':'success'
                    }, 200
        except:
            return {
                    'data':'',
                    'message':'Something went wrong!',
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']
            try:
                data = ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'preprocess')
            except:
                return {
                        'data':'', 
                        'message':'Error in reading file', 
                        'status':'error'
                        }, 400
            return {
                    'data':ex.read_json(data), 
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']
            try:
                jsondata = ex.read_json(ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'preprocess'))
                ISINs, URLs, text = ex.jsontolists(jsondata)
            except:
                return {
                        'data':'',
                        'message':'Could not fetch data to export',
                        'status':'error'
                        }, 400
            if os.path.exists(args['filepath']):
                os.remove(args['filepath'])

            # if file is not of excel or csv, then return error code 400. Else, add to excel/csv as the user requires
            if ex.check(args['filepath'], '.xlsx'):
                ex.exportexcel(filename = args['filepath'], datalist = [ISINs, URLs, text])
            elif ex.check(args['filepath'], '.csv'):
                ex.exportcsv(filename=args['filepath'], field1 = ISINs, field2 = URLs, field3 = text)
            else:
                return {
                        'data':'',
                        'message':'Invalid format. Valid formats are .csv and .xlsx',
                        'status':'error'
                        }, 400

            return {
                    'data':'',
                    'message':'Exported!',
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    jsondata = ex.read_json(ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'preprocess'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            df = cf.tfidf(text)
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            frame, scores = kmeans.kmeans_clustering(args['k'],ratio,ISINs, URLs)
            frame = frame.sort_values(by=['Cluster'])
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
            
            # export the clustered output to csv/excel file according to the user's requirement
            ex.export(datajson, args['format'], ex.give_filename(args['uname'] + '_' + fname + '_' + 'kmeans results', ''))

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            ex.write_json(clusters, ex.give_filename(args['uname'] + '_' + 'summary', '.json'))
            ex.write_json(datajson, ex.give_filename(args['uname'] + '_' + 'cluster', '.json'))

            # plots scatter plot and returns it
            fig = kmeans.visualize_scatter(args['k'], ratio)
            canvas = FigureCanvas(fig)
            output = io.BytesIO()
            canvas.print_png(output)
            response = make_response(output.getvalue())
            response.mimetype = 'image/png'
            return response
        except:
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
            
            try:
                data = ex.get_recent_file(args['uname'] + '_' + 'cluster')
            except:
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            return {
                    'data':ex.read_json(data), 
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    jsondata = ex.read_json(ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'preprocess'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                ISINs, URLs, text = ex.readdataset(args['filepath'])
            
            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                args['pca_comp'] = 0.8
            
            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs DBSCAN clustering
            df = cf.tfidf(text)
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            frame, scores = dbscan.dbscan_clustering(args['eps'], args['min'], ratio, ISINs, URLs)
            frame = frame.sort_values(by=['Cluster'])
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
            
            # export the clustered output to csv/excel file according to the user's requirement
            ex.export(datajson, args['format'], ex.give_filename('dbscan results', ''))

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            ex.write_json(clusters, ex.give_filename(args['uname'] + '_' + 'summary', '.json'))
            ex.write_json(datajson, ex.give_filename(args['uname'] + '_' + 'cluster', '.json'))

            # plots scatter plot and returns it
            fig = dbscan.visualize_scatter(args['eps'], args['min'], ratio)
            canvas = FigureCanvas(fig)
            output = io.BytesIO()
            canvas.print_png(output)
            response = make_response(output.getvalue())
            response.mimetype = 'image/png'
            return response
        except:
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
            
            try:
                data = ex.get_recent_file(args['uname'] + '_' + 'cluster')
            except:
                return {
                        'data':'', 
                        'message':'Error in reading file', 
                        'status':'error'
                        }, 400
            return {
                    'data':ex.read_json(data), 
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    jsondata = ex.read_json(ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'preprocess'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            df = cf.tfidf(text)
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            frame, scores = ag.agglomerative_clustering(args['k'],ratio,ISINs, URLs)
            frame = frame.sort_values(by=['Cluster'])
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
            
            # export the clustered output to csv/excel file according to the user's requirement
            ex.export(datajson, args['format'], ex.give_filename(args['uname'] + '_' + fname + '_' + 'agglomerative results', ''))

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            ex.write_json(clusters, ex.give_filename(args['uname'] + '_' + 'summary', '.json'))
            ex.write_json(datajson, ex.give_filename(args['uname'] + '_' + 'cluster', '.json'))

            # plots scatter plot and returns it
            fig = ag.visualize_scatter(args['k'], ratio)
            canvas = FigureCanvas(fig)
            output = io.BytesIO()
            canvas.print_png(output)
            response = make_response(output.getvalue())
            response.mimetype = 'image/png'
            return response
        except:
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
            
            try:
                data = ex.get_recent_file(args['uname'] + '_' + 'cluster')
            except:
                return {'data':'', 'message':'Error in reading file', 'status':'error'}, 400
            return {
                    'data':ex.read_json(data), 
                    'status':'success'
                    }, 200
        except:
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
            try:
                strrep = args['fname'].split(".",1)[1]
                fname = args['fname'].replace("."+strrep, "")
            except:
                fname = args['fname']

            # by default, format is excel
            if not args['format']:
                args['format'] = 'excel'

            # if filepath is not given, then pre-processed data is present in the file "preprocess.json"
            if not args['filepath']:
                try:
                    jsondata = ex.read_json(ex.get_recent_file(args['uname'] + '_' + fname + '_' + 'preprocess'))
                    ISINs, URLs, text = ex.jsontolists(jsondata)
                except:
                    return {
                            'data':'',
                            'message':'Failed to read data!',
                            'status':'error'
                            }, 400
            else:
                ISINs, URLs, text = ex.readdataset(args['filepath'])

            # sets default values of "thresh"=0.0001 and "pca_comp"=0.8
            if not args['thresh']:
                args['thresh'] = 0.0001
            if not args['pca_comp']:
                args['pca_comp'] = 0.8

            # calculates tfidf, applies PCA and Variance Threshold to reduce features and performs k means clustering
            df = cf.tfidf(text)
            tfidf = cf.varThresh_tfidf(df, args['thresh'])
            score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
            frame, scores = birch.birch_clustering(args['k'],ratio,ISINs, URLs)
            frame = frame.sort_values(by=['Cluster'])
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
            
            # export the clustered output to csv/excel file according to the user's requirement
            ex.export(datajson, args['format'], ex.give_filename(args['uname'] + '_' + fname + '_' + 'birch results', ''))

            # writes a summary of clustering into "cluster.json" and docs in different clusters into "summary.json"
            ex.write_json(clusters, ex.give_filename(args['uname'] + '_' + 'summary', '.json'))
            ex.write_json(datajson, ex.give_filename(args['uname'] + '_' + 'cluster', '.json'))

            # plots scatter plot and returns it
            fig = birch.visualize_scatter(args['k'], ratio)
            canvas = FigureCanvas(fig)
            output = io.BytesIO()
            canvas.print_png(output)
            response = make_response(output.getvalue())
            response.mimetype = 'image/png'
            return response
        except:
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
            
            try:
                data = ex.get_recent_file(args['uname'] + '_' + 'cluster')
            except:
                return {
                        'data':'', 
                        'message':'Error in reading file', 
                        'status':'error'
                        }, 400
            return {
                    'data':ex.read_json(data), 
                    'status':'success'
                    }, 200
        except:
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
            args = parser.parse_args()
            if not args['uname']:
                return {
                        'data':'',
                        'message':'Give user name',
                        'status':'error'
                        }, 400
            
            try:
                data = ex.get_recent_file(args['uname'] + '_' + 'summary')
            except:
                return {
                        'data':'', 
                        'message':'Error in reading file', 
                        'status':'error'
                        }, 400
            return {
                    'data': ex.read_json(data), 
                    'status':'success'
                    }, 200
        except:
            return {
                    'data':'',
                    'message':'Something went wrong',
                    'status':'error'
                    }, 400



# Adding all URL paths
api.add_resource(ExtractData, '/extract')
api.add_resource(ExportExtractedData, '/extract/export')
api.add_resource(PreProcess, '/preprocess')
api.add_resource(ExportPrepData, '/preprocess/export')
api.add_resource(Kmeans, '/clustering/kmeans')
api.add_resource(DBSCAN, '/clustering/dbscan')
api.add_resource(Agglomerative, '/clustering/agglomerative')
api.add_resource(Birch, '/clustering/birch')
api.add_resource(ClusterSummary, '/clustering/summary')


# main function
if __name__ == '__main__':
    app.run(debug=True, threaded=True)