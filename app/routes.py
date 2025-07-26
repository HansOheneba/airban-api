from flask import Blueprint, jsonify, request, current_app
from .models import get_db_connection, get_door_by_id, get_all_doors
import uuid
import json

main = Blueprint("main", __name__)


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
        doors = get_all_doors()
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
        # Get JSON data from request
        data = request.get_json()

        # Extract fields
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        door_type = data.get("type")
        stock = data.get("stock", 0)
        main_image_url = data.get("image_url")  # Frontend will upload and provide URL
        sub_images = data.get("sub_images", [])  # Array of URLs

        # Validate required fields
        if not all([name, description, price, door_type, main_image_url]):
            return (
                jsonify(
                    {
                        "error": "Missing required fields (name, description, price, type, image_url)"
                    }
                ),
                400,
            )

        # Validate door type
        valid_types = ["Single", "Single Wide", "One and Half", "Double"]
        if door_type not in valid_types:
            return (
                jsonify({"error": f"Invalid door type. Must be one of: {valid_types}"}),
                400,
            )

        # Generate UUID for door
        door_id = str(uuid.uuid4())

        # Save main door entry
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO doors (id, name, description, price, image_url, type, stock) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (door_id, name, description, price, main_image_url, door_type, stock),
        )

        # Save sub images
        for image_url in sub_images:
            image_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO door_images (id, door_id, image_url) VALUES (%s, %s, %s)",
                (image_id, door_id, image_url),
            )

        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify({"message": "Door created successfully", "door_id": door_id}),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
