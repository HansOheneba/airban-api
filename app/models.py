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


def create_order(order_data):
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            # First validate all door items and calculate total price
            total_price = 0
            order_items = []

            for item in order_data["items"]:
                cursor.execute(
                    "SELECT price FROM doors WHERE id = %s AND is_deleted = 0",
                    (item["door_id"],),
                )
                door = cursor.fetchone()

                if not door:
                    raise ValueError(
                        f"Door with ID {item['door_id']} not found or deleted"
                    )

                unit_price = door["price"]
                total_price += unit_price * item["quantity"]
                order_items.append(
                    {
                        "door_id": item["door_id"],
                        "quantity": item["quantity"],
                        "unit_price": unit_price,
                        "orientation": item.get("orientation", "left")
                    }
                )

            # Create the order
            order_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO orders 
                (id, customer_name, phone_number, email, location, notes, total_price) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    order_id,
                    order_data["name"],
                    order_data["phone"],
                    order_data["email"], 
                    order_data["address"],
                    order_data.get("notes", ""),
                    total_price,
                ),
            )

            # Create order items
            for item in order_items:
                cursor.execute(
                    """INSERT INTO order_items 
                    (id, order_id, door_id, quantity, unit_price, orientation) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        str(uuid.uuid4()),
                        order_id,
                        item["door_id"],
                        item["quantity"],
                        item["unit_price"],
                        item["orientation"],
                    ),
                )

            conn.commit()
            return order_id


# Update get_order_by_id and get_all_orders to include email
def get_order_by_id(order_id):
    with get_db_cursor() as cursor:
        cursor.execute(
            """SELECT id, customer_name, phone_number, email, location, notes, 
                  total_price, created_at, is_confirmed 
               FROM orders 
               WHERE id = %s AND is_deleted = 0""",
            (order_id,),
        )
        order = cursor.fetchone()

        if not order:
            return None

        # Get order items
        cursor.execute(
            """SELECT oi.door_id, oi.quantity, oi.unit_price, oi.orientation, d.name as door_name
               FROM order_items oi
               JOIN doors d ON oi.door_id = d.id
               WHERE oi.order_id = %s""",
            (order_id,),
        )
        order["items"] = cursor.fetchall()

        return order


def get_all_orders():
    with get_db_cursor() as cursor:
        cursor.execute(
            """SELECT id, customer_name, phone_number, email, location, 
                  total_price, created_at, is_confirmed 
               FROM orders 
               WHERE is_deleted = 0 
               ORDER BY created_at DESC"""
        )
        return cursor.fetchall()
