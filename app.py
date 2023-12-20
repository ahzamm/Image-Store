from flask import Flask, request
from gridfs import GridFS
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://dev_user:dev_password@localhost:27017/')
db = client['image_store']
fs = GridFS(db, collection="files")

def store_image_in_db(file, vector_id, filename):
    fs.put(file, vector_id=vector_id, filename=filename)
    print(f"File stored with vector_id: {vector_id} and filename: {filename}")

@app.route('/photos', methods=['POST'])
def upload_image():
    if 'image' not in request.files or 'vector_id' not in request.form or 'filename' not in request.form:
        return "Invalid request format", 400

    file = request.files['image']
    vector_id = request.form['vector_id']
    filename = request.form['filename']

    if file.filename == '' or vector_id == '' or filename == '':
        return "Incomplete data in the request", 400

    store_image_in_db(file, vector_id, filename)
    return "Image successfully stored in MongoDB"

if __name__ == '__main__':
    app.run(debug=True)
    client.close()
