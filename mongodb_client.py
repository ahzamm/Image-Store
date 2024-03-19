from email.mime import image
from gridfs import GridFS
from pymongo import MongoClient

from db_client import DatabaseClient


class StringParser:
    @staticmethod
    def str_to_lst(input_str):
        try:
            numbers_str = input_str.strip("[]").replace(" ", "")
            numbers_list = [int(num) for num in numbers_str.split(",")]
            return numbers_list
        except ValueError as e:
            print(f"Error: {e}")
            return None


class MongoDBClient(DatabaseClient):
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.fs = GridFS(self.db, collection_name)

    def store_file(self, file, user_id, vector_id, filename):
        self.fs.put(file, user_id=user_id, vector_id=vector_id, filename=filename)

    def get_files(self, vector_ids):
        for vector_id in vector_ids:
            image = self.fs.find_one({"vector_id": str(vector_id)})
            yield {"image": image, "vector_id": image.vector_id}

    def get_user_images(self, user_id):
        images = self.fs.find({"user_id": user_id}).sort("timestamp", -1)
        images_vector_ids = [
            {"image": image, "vector_id": image.vector_id} for image in images
        ]
        return images_vector_ids

    def delete_one(self, vector_id):
        file = self.fs.find_one({"vector_id": str(vector_id)})
        if file:
            self.fs.delete(file._id)

    def close(self):
        self.client.close()
