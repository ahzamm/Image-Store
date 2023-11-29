from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId


client = MongoClient('mongodb://your_username:your_password@localhost:27017/')
db = client['your_database_name']


fs = GridFS(db, collection="files")


def store_image_in_db():
    file_path = './test_images/test_image1.jpg'
    with open(file_path, 'rb') as file:
        file_id = fs.put(file, filename='file.jpg')

    print(f"File stored with id: {file_id}")


def retrieve_image_from_db():
    image_id = '6566512c3c8c69c1ccabc131'
    file = fs.get(ObjectId(image_id))
    output_path = './test_images/test_output_image1.jpg'
    with open(output_path, 'wb') as output_file:
        output_file.write(file.read())

    print(f"Image retrieved and saved to: {output_path}")


retrieve_image_from_db()

client.close()
