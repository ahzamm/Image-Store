from bson import ObjectId
from flask import Flask, request
from gridfs import GridFS
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient('mongodb://dev_user:dev_password@localhost:27017/')
db = client['image_store']
fs = GridFS(db, collection="files")


def store_image_in_db(file):
    file_id = fs.put(file, filename='file.jpg')
    print(f"File stored with id: {file_id}")




@app.route('/photos', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No file part in the request", 400
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
    store_image_in_db(file)
    return "Image successfully stored in MongoDB"

if __name__ == '__main__':
    app.run(debug=True)
    client.close()






def retrieve_image_from_db():
    image_id = '6566512c3c8c69c1ccabc131'
    file = fs.get(ObjectId(image_id))
    output_path = './test_images/test_output_image1.jpg'
    with open(output_path, 'wb') as output_file:
        output_file.write(file.read())

    print(f"Image retrieved and saved to: {output_path}")