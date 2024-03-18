import base64
import io
import zipfile
from ast import literal_eval
from io import BytesIO

from flask import Flask, Response, jsonify, request

from mongodb_client import MongoDBClient


class ImageStoreApp:
    def __init__(self, db_client):
        self.app = Flask(__name__)
        self.db_client = db_client
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/photos", methods=["POST"])
        def upload_image():
            if (
                "image" not in request.files
                or "user_id" not in request.form
                or "vector_id" not in request.form
                or "filename" not in request.form
            ):
                return {"success": "false", "message": "Invalid request format"}, 400

            file = request.files["image"]
            vector_id = request.form["vector_id"]
            filename = request.form["filename"]
            user_id = request.form["user_id"]

            if (
                file.filename == ""
                or user_id == ""
                or vector_id == ""
                or filename == ""
            ):
                return {
                    "success": "false",
                    "message": "Incomplete data in the request",
                }, 400

            self.db_client.store_file(file, user_id, vector_id, filename)
            return {
                "success": "true",
                "message": "Image successfully stored in MongoDB",
            }, 200

        @self.app.route("/retrieve-all-photos/", methods=["GET"])
        def get_all_images():
            user_id = request.args.get("user_id")
            images_vector_ids = self.db_client.get_user_images(user_id)
            images_base64 = []
            for image_dict in images_vector_ids:
                image_bytes = image_dict["image"].read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                images_base64.append(
                    {"image": image_base64, "vector_id": image_dict["vector_id"]}
                )
            return jsonify(images_base64)

        @self.app.route("/retrieve-photos/", methods=["GET"])
        def get_images():
            vector_ids = request.args.get("vector_ids")
            images = self.db_client.get_files(literal_eval(vector_ids))
            images_base64 = []
            for image in images:
                image_bytes = image.read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                images_base64.append(image_base64)
            return jsonify(images_base64)

        @self.app.route("/delete-photo/", methods=["DELETE"])
        def delete_image():
            vector_id = request.args.get("vector_id")
            if not vector_id:
                return {"success": "false", "message": "No vector_id provided"}, 400

            self.db_client.delete_one(vector_id)
            return {"success": "false", "message": "Image deleted successfully"}, 200

    def run(self, port=5002, debug=False):
        self.app.run(port=port, debug=debug)


if __name__ == "__main__":
    db_client = MongoDBClient(
        "mongodb://dev_user:dev_password@localhost:27017/", "image_store", "files"
    )
    app = ImageStoreApp(db_client)
    app.run(debug=True)
    db_client.close()
