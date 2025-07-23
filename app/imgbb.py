import requests
import base64
from flask import current_app


def upload_image_to_imgbb(image_data):
    """
    Uploads an image to imgbb and returns the image URL.
    image_data: bytes or base64 string
    """
    api_key = current_app.config["IMGBB_API_KEY"]
    url = "https://api.imgbb.com/1/upload"
    if isinstance(image_data, bytes):
        image_b64 = base64.b64encode(image_data).decode("utf-8")
    else:
        image_b64 = image_data
    payload = {"key": api_key, "image": image_b64}
    response = requests.post(url, data=payload)
    if response.status_code == 200 and response.json().get("success"):
        return response.json()["data"]["url"]
    else:
        raise Exception(f"Imgbb upload failed: {response.text}")
