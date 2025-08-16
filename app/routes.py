from flask import Blueprint, jsonify, request, current_app
from .models import (
    get_door_by_id,
    get_all_doors,
    delete_door,
    update_door,
    get_db_cursor,
    get_db_connection,
    create_order,
    get_order_by_id,
    get_all_orders,
    mark_order_as_completed,
    delete_order,
    create_property_enquiry,
    get_all_property_enquiries,
    get_property_enquiry_by_id,
    mark_enquiry_as_resolved,
    mark_enquiry_as_unresolved,
    delete_property_enquiry,
    create_contact_enquiry,
    get_all_contact_enquiries,
    get_contact_enquiry_by_id,
    mark_contact_enquiry_as_resolved,
    mark_contact_enquiry_as_unresolved,
    delete_contact_enquiry,
)

from .email import (
    send_order_confirmation,
    send_property_enquiry_emails,
    send_contact_enquiry_emails,
    send_newsletter_welcome_email,
)
import uuid

import resend

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


@main.route("/orders", methods=["POST"])
def create_order_route():
    try:
        data = request.get_json()

        if not all(
            [
                data.get("name"),
                data.get("email"),
                data.get("phone"),
                data.get("address"),
                data.get("items"),
            ]
        ):
            return (
                jsonify(
                    {
                        "error": "Missing required fields (name, email, phone, address, items)"
                    }
                ),
                400,
            )

        if not isinstance(data["items"], list) or len(data["items"]) == 0:
            return jsonify({"error": "Items must be a non-empty array"}), 400

        for item in data["items"]:
            if not all(k in item for k in ["door_id", "quantity"]):
                return (
                    jsonify({"error": "Each item must have door_id and quantity"}),
                    400,
                )
            if item["quantity"] <= 0:
                return jsonify({"error": "Quantity must be positive"}), 400

            if "orientation" in item and item["orientation"] not in ["left", "right"]:
                return (
                    jsonify({"error": "Orientation must be either 'left' or 'right'"}),
                    400,
                )

        # Create the order
        order_id = create_order(data)
        order = get_order_by_id(order_id)

        send_order_confirmation(order)

        return jsonify({"message": "Order created successfully", "order": order}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/orders", methods=["GET"])
def get_orders():
    try:
        orders = get_all_orders()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    try:
        order = get_order_by_id(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        return jsonify(order), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to mark an order as completed
@main.route("/orders/complete/<order_id>", methods=["POST"])
def complete_order(order_id):
    try:
        success = mark_order_as_completed(order_id)
        if not success:
            return (
                jsonify({"error": "Order not found or already completed/deleted"}),
                404,
            )
        return jsonify({"message": "Order marked as completed."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete (soft-delete) an order
@main.route("/orders/<order_id>", methods=["DELETE"])
def delete_order_route(order_id):
    try:
        success = delete_order(order_id)
        if not success:
            return jsonify({"error": "Order not found or already deleted"}), 404
        return jsonify({"message": "Order deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    verified_domain = current_app.config["VERIFIED_DOMAIN"]
    admin_email = current_app.config["ADMIN_EMAIL"]
    print(f"Using verified domain: {verified_domain}, admin email: {admin_email}")


@main.route("/test-email")
def test_email():
    try:
        resend.api_key = current_app.config["RESEND_API_KEY"]

        verified_domain = current_app.config["RESEND_VERIFIED_DOMAIN"]
        admin_email = current_app.config["ADMIN_EMAIL"]
        print(f"Using verified domain: {verified_domain}, admin email: {admin_email}")

        params = {
            "from": f"Airban Doors <{verified_domain}>",
            "to": [f"Hans Oheneba <{admin_email}>"],
            "subject": "Test Email from Airban Doors",
            "html": "<strong>This is a test email from Airban Doors!</strong>",
        }

        response = resend.Emails.send(params)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Property Enquiry Routes
@main.route("/property", methods=["POST"])
def create_property_enquiry_route():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "selected_property",
        ]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        enquiry_id = create_property_enquiry(data)

        # Get the full enquiry data to send email
        enquiry = get_property_enquiry_by_id(enquiry_id)
        if enquiry:
            send_property_enquiry_emails(enquiry)

        return (
            jsonify(
                {
                    "message": "Property enquiry submitted successfully",
                    "enquiry_id": enquiry_id,
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/property", methods=["GET"])
def get_property_enquiries():
    try:
        enquiries = get_all_property_enquiries()
        return jsonify(enquiries), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/property/<enquiry_id>", methods=["GET"])
def get_single_property_enquiry(enquiry_id):
    try:
        enquiry = get_property_enquiry_by_id(enquiry_id)
        if not enquiry:
            return jsonify({"error": "Property enquiry not found"}), 404
        return jsonify(enquiry), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/property/<enquiry_id>/resolve", methods=["POST"])
def resolve_property_enquiry(enquiry_id):
    try:
        success = mark_enquiry_as_resolved(enquiry_id)
        if not success:
            return jsonify({"error": "Property enquiry not found"}), 404
        return jsonify({"message": "Property enquiry marked as resolved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/property/<enquiry_id>/unresolve", methods=["POST"])
def unresolve_property_enquiry(enquiry_id):
    try:
        success = mark_enquiry_as_unresolved(enquiry_id)
        if not success:
            return jsonify({"error": "Property enquiry not found"}), 404
        return jsonify({"message": "Property enquiry marked as unresolved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/property/<enquiry_id>", methods=["DELETE"])
def delete_property_enquiry_route(enquiry_id):
    try:
        success = delete_property_enquiry(enquiry_id)
        if not success:
            return jsonify({"error": "Property enquiry not found"}), 404
        return jsonify({"message": "Property enquiry deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/contact", methods=["POST"])
def create_contact_enquiry_route():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "phone", "enquiry_type"]
        if not all(field in data for field in required_fields):
            return (
                jsonify(
                    {
                        "error": "Missing required fields (first_name, last_name, email, phone, enquiry_type)"
                    }
                ),
                400,
            )

        enquiry_id = create_contact_enquiry(data)

        # Get the full enquiry data to send email
        enquiry = get_contact_enquiry_by_id(enquiry_id)
        if enquiry:
            send_contact_enquiry_emails(enquiry)

        return (
            jsonify(
                {
                    "message": "Contact enquiry submitted successfully",
                    "enquiry_id": enquiry_id,
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/contact", methods=["GET"])
def get_contact_enquiries():
    try:
        enquiries = get_all_contact_enquiries()
        return jsonify(enquiries), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/contact/<enquiry_id>", methods=["GET"])
def get_contact_enquiry(enquiry_id):
    try:
        enquiry = get_contact_enquiry_by_id(enquiry_id)
        if not enquiry:
            return jsonify({"error": "Contact enquiry not found"}), 404
        return jsonify(enquiry), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/contact/<enquiry_id>/resolve", methods=["POST"])
def resolve_contact_enquiry(enquiry_id):
    try:
        success = mark_contact_enquiry_as_resolved(enquiry_id)
        if not success:
            return jsonify({"error": "Contact enquiry not found"}), 404
        return jsonify({"message": "Contact enquiry marked as resolved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/contact/<enquiry_id>/unresolve", methods=["POST"])
def unresolve_contact_enquiry(enquiry_id):
    try:
        success = mark_contact_enquiry_as_unresolved(enquiry_id)
        if not success:
            return jsonify({"error": "Contact enquiry not found"}), 404
        return jsonify({"message": "Contact enquiry marked as unresolved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/contact/<enquiry_id>", methods=["DELETE"])
def delete_contact_enquiry_route(enquiry_id):
    try:
        success = delete_contact_enquiry(enquiry_id)
        if not success:
            return jsonify({"error": "Contact enquiry not found"}), 404
        return jsonify({"message": "Contact enquiry deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Newsletter subscription route
from .models import add_newsletter_subscriber


@main.route("/subscribe", methods=["POST"])
def subscribe_newsletter():
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400

        subscriber_id = add_newsletter_subscriber(email)
        if subscriber_id:
            send_newsletter_welcome_email({"email": email, "id": subscriber_id})
            return (
                jsonify({"message": "Subscribed successfully", "id": subscriber_id}),
                201,
            )
        else:
            return jsonify({"error": "Email already subscribed or invalid"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500
