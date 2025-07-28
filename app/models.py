from flask import current_app
import mysql.connector.pooling
import uuid
from contextlib import contextmanager

# Connection pool setup
db_pool = None


def init_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="door_app_pool",
            pool_size=5,
            host=current_app.config["MYSQL_HOST"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DB"],
            autocommit=True,
        )


@contextmanager
def get_db_connection():
    if db_pool is None:
        init_db_pool()
    conn = db_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(dictionary=True):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
        finally:
            cursor.close()


def get_all_doors():
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT id, name, price, type, image_url FROM doors WHERE is_deleted = 0 ORDER BY created_at DESC"
        )
        return cursor.fetchall()


def get_door_by_id(door_id):
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM doors WHERE id = %s AND is_deleted = 0", (door_id,)
        )
        door = cursor.fetchone()

        if door:
            cursor.execute(
                "SELECT image_url FROM door_images WHERE door_id = %s", (door_id,)
            )
            door["sub_images"] = [img["image_url"] for img in cursor.fetchall()]
        return door


def delete_door(door_id):
    with get_db_cursor() as cursor:
        cursor.execute("UPDATE doors SET is_deleted = 1 WHERE id = %s", (door_id,))
        return cursor.rowcount > 0


def update_door(door_id, update_data):
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            # Update main door fields
            set_clauses = []
            values = []
            allowed_fields = [
                "name",
                "description",
                "price",
                "type",
                "stock",
                "image_url",
            ]

            for field in allowed_fields:
                if field in update_data:
                    set_clauses.append(f"{field} = %s")
                    values.append(update_data[field])

            if set_clauses:
                query = f"UPDATE doors SET {', '.join(set_clauses)} WHERE id = %s AND is_deleted = 0"
                cursor.execute(query, values + [door_id])

            # Handle sub images
            if "sub_images_operations" in update_data:
                ops = update_data["sub_images_operations"]

                if "delete" in ops:
                    for url in ops["delete"]:
                        cursor.execute(
                            "DELETE FROM door_images WHERE door_id = %s AND image_url = %s",
                            (door_id, url),
                        )

                if "add" in ops:
                    for url in ops["add"]:
                        cursor.execute(
                            "INSERT INTO door_images (id, door_id, image_url) VALUES (%s, %s, %s)",
                            (str(uuid.uuid4()), door_id, url),
                        )

            conn.commit()
            return True
