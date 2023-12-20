from flask import Flask, request
from gridfs import GridFS
from pymongo import MongoClient

class MongoDBClient:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.fs = GridFS(self.db, collection_name)

    def store_file(self, file, vector_id, filename):
        self.fs.put(file, vector_id=vector_id, filename=filename)

    def close(self):
        self.client.close()

class ImageStoreApp:
    def __init__(self, db_client):
        self.app = Flask(__name__)
        self.db_client = db_client
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/photos', methods=['POST'])
        def upload_image():
            if 'image' not in request.files or 'vector_id' not in request.form or 'filename' not in request.form:
                return "Invalid request format", 400

            file = request.files['image']
            vector_id = request.form['vector_id']
            filename = request.form['filename']

            if file.filename == '' or vector_id == '' or filename == '':
                return "Incomplete data in the request", 400

            self.db_client.store_file(file, vector_id, filename)
            return "Image successfully stored in MongoDB"

    def run(self, debug=False):
        self.app.run(debug=debug)

if __name__ == '__main__':
    db_client = MongoDBClient('mongodb://dev_user:dev_password@localhost:27017/', 'image_store', 'files')
    app = ImageStoreApp(db_client)
    app.run(debug=True)
    db_client.close()
