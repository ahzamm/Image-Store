import zipfile
from io import BytesIO

from flask import Flask, Response, request

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
                or "vector_id" not in request.form
                or "filename" not in request.form
            ):
                return {"success": "false", "message": "Invalid request format"}, 400

            file = request.files["image"]
            vector_id = request.form["vector_id"]
            filename = request.form["filename"]

            if file.filename == "" or vector_id == "" or filename == "":
                return {
                    "success": "false",
                    "message": "Incomplete data in the request",
                }, 400

            self.db_client.store_file(file, vector_id, filename)
            return {
                "success": "true",
                "message": "Image successfully stored in MongoDB",
            }, 200

        @self.app.route("/retrieve-photos/", methods=["GET"])
        def get_images():
            vector_ids = request.args.get("vector_ids")
            images = self.db_client.get_files(vector_ids)
            if images:
                memory_file = BytesIO()

                with zipfile.ZipFile(memory_file, "w") as zf:
                    for i, image in enumerate(images):
                        data = zipfile.ZipInfo(
                            f"image{i+1}.jpeg"
                        )  # assuming the image is in JPEG format
                        data.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(data, image.read())

                memory_file.seek(0)
                response = Response(memory_file, mimetype="application/zip")
                response.headers["Content-Disposition"] = (
                    "attachment; filename=images.zip"
                )
                return response
            else:
                return "No images found", 404

        @self.app.route("/delete-photo/", methods=["GET"])
        def delete_image():
            vector_id = request.args.get("vector_id")
            if not vector_id:
                return "No vector_id provided", 400
            self.db_client.delete_one(vector_id)
            return "Image deleted successfully", 200

    def run(self, debug=False):
        self.app.run(debug=debug)


if __name__ == "__main__":
    db_client = MongoDBClient(
        "mongodb://dev_user:dev_password@localhost:27017/", "image_store", "files"
    )
    app = ImageStoreApp(db_client)
    app.run(debug=True)
    db_client.close()
