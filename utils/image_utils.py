# utils/image_utils.py

from PIL import Image
from io import BytesIO
import requests
import base64

def resize_and_encode_image(url: str, size=(100, 100)) -> str:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.thumbnail(size)
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=10)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"⚠️ Error al procesar la imagen desde {url}: {e}")
        # Devolver imagen base64 vacía o una por defecto si falla
        return ""
