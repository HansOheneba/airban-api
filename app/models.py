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
        "SELECT id, name, price, type, image_url FROM doors WHERE is_deleted = 0 ORDER BY created_at DESC"
    )
    doors = cursor.fetchall()

    cursor.close()
    conn.close()
    return doors


def get_door_by_id(door_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM doors WHERE id = %s AND is_deleted = 0", (door_id,))
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


def delete_door(door_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE doors SET is_deleted = 1 WHERE id = %s", (door_id,))
        conn.commit()
        affected_rows = cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return affected_rows > 0


def update_door(door_id, update_data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Build the update query for door fields
        set_clauses = []
        values = []
        allowed_fields = ['name', 'description', 'price', 'type', 'stock', 'image_url']
        
        for field in allowed_fields:
            if field in update_data:
                set_clauses.append(f"{field} = %s")
                values.append(update_data[field])
        
        # Update door fields if any
        if set_clauses:
            query = f"UPDATE doors SET {', '.join(set_clauses)} WHERE id = %s AND is_deleted = 0"
            cursor.execute(query, values + [door_id])
        
        # Handle sub images operations
        if 'sub_images_operations' in update_data:
            operations = update_data['sub_images_operations']
            
            # Delete specified images
            if 'delete' in operations:
                for image_url in operations['delete']:
                    cursor.execute(
                        "DELETE FROM door_images WHERE door_id = %s AND image_url = %s",
                        (door_id, image_url))
            
            # Add new images
            if 'add' in operations:
                for image_url in operations['add']:
                    image_id = str(uuid.uuid4())
                    cursor.execute(
                        "INSERT INTO door_images (id, door_id, image_url) VALUES (%s, %s, %s)",
                        (image_id, door_id, image_url))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
