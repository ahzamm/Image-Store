import zipfile
from io import BytesIO

from flask import Flask, request, send_file
from gridfs import GridFS
from pymongo import MongoClient
from flask import Response


class MongoDBClient:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.fs = GridFS(self.db, collection_name)

    def store_file(self, file, vector_id, filename):
        self.fs.put(file, vector_id=vector_id, filename=filename)

    def str_to_lst(self, input_str):
        try:
            numbers_str = input_str.strip('[]').replace(' ', '')
            numbers_list = [int(num) for num in numbers_str.split(',')]
            return numbers_list
        except ValueError as e:
            print(f"Error: {e}")
            return None

    def get_files(self, vector_ids):
        vector_ids = self.str_to_lst(vector_ids)
        images = []
        for vector_id in vector_ids:
            image = self.fs.find_one({'vector_id': str(vector_id)})
            if image:
                images.append(image)
        return images

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

        @self.app.route('/retrieve-photos/', methods=['GET'])
        def get_images():
            vector_ids = request.args.get('vector_ids')
            images = self.db_client.get_files(vector_ids)
            if images:
                memory_file = BytesIO()
                with zipfile.ZipFile(memory_file, 'w') as zf:
                    for i, image in enumerate(images):
                        data = zipfile.ZipInfo(f'image{i+1}.jpeg')  # assuming the image is in JPEG format
                        data.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(data, image.read())
                memory_file.seek(0)
                response = Response(memory_file, mimetype='application/zip')
                response.headers['Content-Disposition'] = 'attachment; filename=images.zip'
                return response
            else:
                return "No images found", 404

    def run(self, debug=False):
        self.app.run(debug=debug)

if __name__ == '__main__':
    db_client = MongoDBClient('mongodb://dev_user:dev_password@localhost:27017/', 'image_store', 'files')
    app = ImageStoreApp(db_client)
    app.run(debug=True)
    db_client.close()
