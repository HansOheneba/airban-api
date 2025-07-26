from flask import current_app
import mysql.connector
import uuid


def get_db_connection():
    return mysql.connector.connect(
        host=current_app.config["MYSQL_HOST"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DB"],
    )


def get_all_doors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, name, price, type, image_url FROM doors ORDER BY created_at DESC"
    )
    doors = cursor.fetchall()

    cursor.close()
    conn.close()
    return doors


def get_door_by_id(door_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM doors WHERE id = %s", (door_id,))
    door = cursor.fetchone()

    if door:
        # Sub images
        cursor.execute(
            "SELECT image_url FROM door_images WHERE door_id = %s", (door_id,)
        )
        door["sub_images"] = [img["image_url"] for img in cursor.fetchall()]

    cursor.close()
    conn.close()
    return door
