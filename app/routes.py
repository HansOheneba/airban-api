from flask import Blueprint, jsonify, request, current_app
from .models import get_door_by_id, get_all_doors, delete_door, update_door, get_db_cursor, get_db_connection 
import uuid

main = Blueprint("main", __name__)


@main.route("/test-db")
def test_db():
    try:
        with get_db_cursor() as cursor: 
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
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
    try:
        door = get_door_by_id(door_id)
        if not door:
            return jsonify({"error": "Door not found"}), 404
        return jsonify(door), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/doors", methods=["POST"])
def create_door():
    try:
        data = request.get_json()

        # Extract fields
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        door_type = data.get("type")
        stock = data.get("stock", 0)
        main_image_url = data.get("image_url")
        sub_images = data.get("sub_images", [])

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

        # Use the connection pool via context manager
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Save main door entry
                cursor.execute(
                    """INSERT INTO doors 
                    (id, name, description, price, image_url, type, stock) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        door_id,
                        name,
                        description,
                        price,
                        main_image_url,
                        door_type,
                        stock,
                    ),
                )

                # Save sub images
                for image_url in sub_images:
                    cursor.execute(
                        """INSERT INTO door_images 
                        (id, door_id, image_url) 
                        VALUES (%s, %s, %s)""",
                        (str(uuid.uuid4()), door_id, image_url),
                    )

                conn.commit()

        return (
            jsonify({"message": "Door created successfully", "door_id": door_id}),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/doors/<door_id>", methods=["DELETE"])
def delete_door_route(door_id):
    try:
        # First check if door exists
        door = get_door_by_id(door_id)
        if not door:
            return jsonify({"error": "Door not found"}), 404

        # Perform soft delete
        if delete_door(door_id):
            return jsonify({"message": "Door deleted successfully"}), 200
        return jsonify({"error": "Delete operation failed"}), 400

    except Exception as e:
        current_app.logger.error(f"Error deleting door: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/doors/<door_id>", methods=["PATCH"])
def update_door_route(door_id):
    try:
        door = get_door_by_id(door_id)
        if not door:
            return jsonify({"error": "Door not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        if "type" in data:
            valid_types = ["Single", "Single Wide", "One and Half", "Double"]
            if data["type"] not in valid_types:
                return (
                    jsonify(
                        {"error": f"Invalid door type. Must be one of: {valid_types}"}
                    ),
                    400,
                )

        if update_door(door_id, data):
            updated_door = get_door_by_id(door_id)
            return (
                jsonify({"message": "Door updated successfully", "door": updated_door}),
                200,
            )
        return jsonify({"error": "No changes were made"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
