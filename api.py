from flask import Flask, request, jsonify, make_response, send_file
import kmeans
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask_restful import Api, Resource, reqparse
from tinydb import TinyDB, Query
import extract as ex
import clean_file as cf
import json
import io
import os
import dbscan
import birch
import agglomerative as ag
import matplotlib.pyplot as plt


app = Flask(__name__)
api = Api(app)


class ExtractData(Resource):
    #curl http://127.0.0.1:5000/extract?filepath=ISINS_v3.xlsx -X POST 
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        parser.add_argument('no_of_docs', type=str)
        args = parser.parse_args()
        ISINs, URLs, text = ex.extract(args['filepath'], args['no_of_docs'])
        jsondata = ex.tojson(ISINs, URLs, text)
        ex.write_json(jsondata, 'extract.json')
        return 200

    #curl http://127.0.0.1:5000/extract -X GET 
    def get(self):
        db = TinyDB('db.json')
        return db.all(), 200

class ExportExtractedData(Resource):
    #curl http://127.0.0.1:5000/export?prep.xlsx -X GET 
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        args = parser.parse_args()
        jsondata = ex.read_json('extract.json')
        ISINs, URLs, text = ex.jsontolists(jsondata)
        if os.path.exists(args['filepath']):
            os.remove(args['filepath'])
        if ex.check(args['filepath'], '.xlsx'):
            ex.exportexcel(filename = args['filepath'], datalist = [ISINs, URLs, text])
        elif ex.check(args['filepath'], '.csv'):
            ex.exportcsv(filename=args['filepath'], field1 = ISINs, field2 = URLs, field3 = text)
        else:
            print("Invalid file format. Valid file formats are .xlsx and .csv")
            return 400
        return 200
        
class ExportPrepData(Resource):
    #curl http://127.0.0.1:5000/export?prep.xlsx -X GET 
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        args = parser.parse_args()
        jsondata = ex.read_json('preprocess.json')
        ISINs, URLs, text = ex.jsontolists(jsondata)
        if os.path.exists(args['filepath']):
            os.remove(args['filepath'])
        if ex.check(args['filepath'], '.xlsx'):
            ex.exportexcel(filename = args['filepath'], datalist = [ISINs, URLs, text])
        elif ex.check(args['filepath'], '.csv'):
            ex.exportcsv(filename=args['filepath'], field1 = ISINs, field2 = URLs, field3 = text)
        else:
            print("Invalid file format. Valid file formats are .xlsx and .csv")
            return 400
        return 200
                

class ExportClusterData(Resource):
    #curl http://127.0.0.1:5000/export?prep.xlsx -X GET 
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        args = parser.parse_args()
        db = TinyDB('cluster.json')
        jsondata = db.all()
        cluster, ISINs, URLs = ex.jsontolistsC(jsondata)
        if os.path.exists(args['filepath']):
            os.remove(args['filepath'])
        if ex.check(args['filepath'], '.xlsx'):
            ex.exportexcel(filename = args['filepath'], datalist = [cluster, ISINs, URLs], fields=['Cluster', 'ISIN', 'Termsheet Link'])
        elif ex.check(args['filepath'], '.csv'):
            ex.exportcsv(filename=args['filepath'], field1 = cluster, field2 = ISINs, field3 = URLs, fields=['Cluster', 'ISIN', 'Termsheet Link'])
        else:
            print("Invalid file format. Valid file formats are .xlsx and .csv")
            return 400
        db.close()
        return 200

class PreProcess(Resource):
    #curl http://127.0.0.1:5000/preprocess -d "filepath=extract.xlsx" -d "steps=numbers" -d "steps=url" -d "steps=stemming" -d "steps=lemmatization" -d "steps=punctuations" -d "steps=stopwords" -d "steps=case" -d "steps=words" -X POST
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        parser.add_argument('steps', action='append')
        args = parser.parse_args()
        argset = set(args)
        if not args['filepath']:
            jsondata = ex.read_json('extract.json')
            ISINs, URLs, text = ex.jsontolists(jsondata)
        else:
            ISINs, URLs, text = ex.readdataset(args['filepath'])
        
        data = cf.preprocessing(text, args['steps'])
        jsondata = ex.tojson(ISINs, URLs, data)
        ex.write_json(jsondata, 'preprocess.json')
        return 200

    #curl http://127.0.0.1:5000/preprocess -X GET 
    def get(self):
        data = ex.read_json('preprocess.json')
        return data, 200


class Kmeans(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        parser.add_argument('k', type=int)
        parser.add_argument('thresh', type=float)
        parser.add_argument('pca_comp', type=float)
        args = parser.parse_args()
        if not args['filepath']:
            jsondata = ex.read_json('preprocess.json')
            ISINs, URLs, text = ex.jsontolists(jsondata)
        else:
            ISINs, URLs, text = ex.readdataset(args['filepath'])
        if not args['thresh']:
            args['thresh'] = 0.0001
        if not args['pca_comp']:
            args['pca_comp'] = 0.8
        db = TinyDB('summary.json')
        db.truncate()
        cdb = TinyDB('cluster.json')
        cdb.truncate()
        df = cf.tfidf(text)
        tfidf = cf.varThresh_tfidf(df, args['thresh'])
        score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
        frame, scores = kmeans.kmeans_clustering(args['k'],ratio,ISINs, URLs)
        
        frame = frame.sort_values(by=['Cluster'])
        datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
        #ex.write_json(datajson, 'clusters.json')
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

        for data in datajson:
            cdb.insert(data)
        db.insert(clusters)
        db.close()
        cdb.close()
        fig = kmeans.visualize_scatter(args['k'], ratio)
        canvas = FigureCanvas(fig)
        output = io.BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'
        return response

    def get(self):
        db = TinyDB('cluster.json')
        data = db.all()
        return data, 200

class DBSCAN(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        parser.add_argument('eps', type=float)
        parser.add_argument('min', type=int)
        parser.add_argument('thresh', type=float)
        parser.add_argument('pca_comp', type=float)
        args = parser.parse_args()
        if not args['filepath']:
            jsondata = ex.read_json('preprocess.json')
            ISINs, URLs, text = ex.jsontolists(jsondata)
        else:
            ISINs, URLs, text = ex.readdataset(args['filepath'])
        if not args['thresh']:
            args['thresh'] = 0.0001
        if not args['pca_comp']:
            args['pca_comp'] = 0.8
        db = TinyDB('summary.json')
        db.truncate()
        cdb = TinyDB('cluster.json')
        cdb.truncate()
        df = cf.tfidf(text)
        tfidf = cf.varThresh_tfidf(df, args['thresh'])
        score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
        frame, scores = dbscan.dbscan_clustering(args['eps'], args['min'], ratio, ISINs, URLs)

        frame = frame.sort_values(by=['Cluster'])
        datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
        #ex.write_json(datajson, 'clusters.json')
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

        for data in datajson:
            cdb.insert(data)
        db.insert(clusters)
        db.close()
        cdb.close()
        fig = dbscan.visualize_scatter(args['eps'], args['min'], ratio)
        canvas = FigureCanvas(fig)
        output = io.BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'
        
        return response
        
    def get(self):
        db = TinyDB('cluster.json')
        data = db.all()
        return data, 200

class Agglomerative(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        parser.add_argument('k', type=int)
        parser.add_argument('thresh', type=float)
        parser.add_argument('pca_comp', type=float)
        args = parser.parse_args()
        if not args['filepath']:
            jsondata = ex.read_json('preprocess.json')
            ISINs, URLs, text = ex.jsontolists(jsondata)
        else:
            ISINs, URLs, text = ex.readdataset(args['filepath'])
        if not args['thresh']:
            args['thresh'] = 0.0001
        if not args['pca_comp']:
            args['pca_comp'] = 0.8
        db = TinyDB('summary.json')
        db.truncate()
        cdb = TinyDB('cluster.json')
        cdb.truncate()
        df = cf.tfidf(text)
        tfidf = cf.varThresh_tfidf(df, args['thresh'])
        score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
        frame, scores = ag.agglomerative_clustering(args['k'],ratio,ISINs, URLs)
        
        frame = frame.sort_values(by=['Cluster'])
        datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
        #ex.write_json(datajson, 'clusters.json')
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

        for data in datajson:
            cdb.insert(data)
        db.insert(clusters)
        db.close()
        cdb.close()
        fig = ag.visualize_scatter(args['k'], ratio)
        canvas = FigureCanvas(fig)
        output = io.BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'
        return response
        
    def get(self):
        db = TinyDB('cluster.json')
        data = db.all()
        return data, 200

class Birch(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('filepath', type=str)
        parser.add_argument('k', type=int)
        parser.add_argument('thresh', type=float)
        parser.add_argument('pca_comp', type=float)
        args = parser.parse_args()
        if not args['filepath']:
            jsondata = ex.read_json('preprocess.json')
            ISINs, URLs, text = ex.jsontolists(jsondata)
        else:
            ISINs, URLs, text = ex.readdataset(args['filepath'])
        if not args['thresh']:
            args['thresh'] = 0.0001
        if not args['pca_comp']:
            args['pca_comp'] = 0.8
        db = TinyDB('summary.json')
        db.truncate()
        cdb = TinyDB('cluster.json')
        cdb.truncate()
        df = cf.tfidf(text)
        tfidf = cf.varThresh_tfidf(df, args['thresh'])
        score, ratio, pcadf = cf.pca_tfidf(df, args['pca_comp'])
        frame, scores = birch.birch_clustering(args['k'],ratio,ISINs, URLs)

        frame = frame.sort_values(by=['Cluster'])
        datajson = ex.tojsondf(frame['ISIN'], frame['URL'], frame['Cluster'])
        #ex.write_json(datajson, 'clusters.json')
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

        for data in datajson:
            cdb.insert(data)
        db.insert(clusters)
        db.close()
        cdb.close()
        fig = birch.visualize_scatter(args['k'], ratio)
        canvas = FigureCanvas(fig)
        output = io.BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'
        return response
        
    def get(self):
        db = TinyDB('cluster.json')
        data = db.all()
        return data, 200

class ClusterSummary(Resource):
    def get(self):
        db = TinyDB('summary.json')
        data = db.all()
        return data, 200


api.add_resource(ExtractData, '/extract')
api.add_resource(ExportExtractedData, '/extract/export')
api.add_resource(PreProcess, '/preprocess')
api.add_resource(ExportPrepData, '/preprocess/export')
#api.add_resource(ExportClusterData, '/clustering/export')
api.add_resource(ExportClusterData, '/clustering/kmeans/export', endpoint="kmeans-export")
api.add_resource(ExportClusterData, '/clustering/dbscan/export', endpoint="dbscan-export")
api.add_resource(ExportClusterData, '/clustering/agglomerative/export', endpoint="agglomerative-export")
api.add_resource(ExportClusterData, '/clustering/birch/export', endpoint="birch-export")
#api.add_resource(ClusterSummary, '/clustering/summary')
api.add_resource(ClusterSummary, '/clustering/kmeans/summary', endpoint="kmeans-summary")
api.add_resource(ClusterSummary, '/clustering/dbscan/summary', endpoint="dbscan-summary")
api.add_resource(ClusterSummary, '/clustering/agglomerative/summary', endpoint="agglomerative-summary")
api.add_resource(ClusterSummary, '/clustering/birch/summary', endpoint="birch-summary")
api.add_resource(Kmeans, '/clustering/kmeans')
api.add_resource(DBSCAN, '/clustering/dbscan')
api.add_resource(Agglomerative, '/clustering/agglomerative')
api.add_resource(Birch, '/clustering/birch')

if __name__ == '__main__':
    app.run(debug=True)