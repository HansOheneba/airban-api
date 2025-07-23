from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from .models import get_db_connection, get_door_by_id
import requests

main = Blueprint("main", __name__)


def upload_to_imgbb(image):
    imgbb_api_key = current_app.config["IMGBB_API_KEY"]
    filename = secure_filename(image.filename)
    image_data = image.read()

    res = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": imgbb_api_key},
        files={"image": (filename, image_data)},
    )

    if res.status_code == 200:
        return res.json()["data"]["url"]
    else:
        raise Exception("ImgBB upload failed: " + res.text)


@main.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()[0]
        conn.close()
        return jsonify({"connected_to": db_name})
    except Exception as e:
        return jsonify({"error": str(e)})


@main.route("/doors", methods=["GET"])
def get_doors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM doors ORDER BY created_at DESC")
        doors = cursor.fetchall()
        conn.close()
        return jsonify(doors)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/doors/<door_id>", methods=["GET"])
def single_door(door_id):
    door = get_door_by_id(door_id)
    if not door:
        return jsonify({"error": "Door not found"}), 404
    return jsonify(door), 200


@main.route("/doors", methods=["POST"])
def create_door():
    try:
        # Get form fields
        import uuid

        # Log all form fields received
        print("[DEBUG] request.form:", dict(request.form))

        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        image_url = request.form.get("image")
        category = request.form.get("category")

        if not image_url or not name or not price or not description or not category:
            return (
                jsonify(
                    {
                        "error": "Name, price, image_url, description, and category are required"
                    }
                ),
                400,
            )

        # Generate UUID for door
        door_id = str(uuid.uuid4())

        # Save main door entry
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO doors (id, name, description, price, image_url, category) VALUES (%s, %s, %s, %s, %s, %s)",
            (door_id, name, description, price, image_url, category),
        )

        # Optional: Sub images as URLs (expects a JSON array of URLs in sub_images)
        sub_images_raw = request.form.get("sub_images")
        if sub_images_raw:
            import json

            try:
                sub_images = json.loads(sub_images_raw)
                if isinstance(sub_images, list):
                    for img_url in sub_images:
                        image_id = str(uuid.uuid4())
                        cursor.execute(
                            "INSERT INTO door_images (id, door_id, image_url) VALUES (%s, %s, %s)",
                            (image_id, door_id, img_url),
                        )
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON format for sub_images"}), 400

        # Required: Variants (JSON string)
        variants_raw = request.form.get("variants")
        if not variants_raw:
            return (
                jsonify(
                    {
                        "error": "Variants are required and must be provided as a JSON array."
                    }
                ),
                400,
            )
        import json

        try:
            variants = json.loads(variants_raw)
            if not isinstance(variants, list) or len(variants) == 0:
                return jsonify({"error": "At least one variant is required."}), 400
            for v in variants:
                color = v.get("color")
                orientation = v.get("orientation")
                stock = v.get("stock", 0)
                if not color or not orientation:
                    return (
                        jsonify(
                            {"error": "Each variant must have color and orientation."}
                        ),
                        400,
                    )
                variant_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO door_variants (id, door_id, color, orientation, stock) VALUES (%s, %s, %s, %s, %s)",
                    (variant_id, door_id, color, orientation, stock),
                )
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for variants"}), 400

        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify({"message": "Door created successfully", "door_id": door_id}),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
