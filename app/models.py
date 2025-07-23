# Table schemas for reference:
# doors(id INT, name VARCHAR(100), description TEXT, price DECIMAL(10,2), image_url VARCHAR(255), created_at TIMESTAMP)
# door_images(id INT, door_id INT, image_url VARCHAR(255))
# door_variants(id INT, door_id INT, color VARCHAR(50), orientation ENUM('left','right'), stock INT)

# app/models.py


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

    cursor.execute("SELECT * FROM doors")
    doors = cursor.fetchall()

    for door in doors:
        # Get sub images
        cursor.execute(
            "SELECT image_url FROM door_images WHERE door_id = %s", (door["id"],)
        )
        door["sub_images"] = [img["image_url"] for img in cursor.fetchall()]

        # Get variants
        cursor.execute(
            "SELECT color, orientation, stock FROM door_variants WHERE door_id = %s",
            (door["id"],),
        )
        door["variants"] = cursor.fetchall()

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

        # Variants
        cursor.execute(
            "SELECT color, orientation, stock FROM door_variants WHERE door_id = %s",
            (door_id,),
        )
        door["variants"] = cursor.fetchall()

    cursor.close()
    conn.close()
    return door
