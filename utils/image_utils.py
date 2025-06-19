# utils/image_utils.py

from PIL import Image
from io import BytesIO
import requests
import base64

def resize_and_encode_image(url: str, size=(300, 300)) -> str:
    try:
        print(f"🖼️ Descargando imagen desde: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.thumbnail(size)
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=70)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"❌ Error procesando imagen desde {url}: {e}")
        return ""
    
def get_default_image_base64(BASE_DIR) -> str:
    try:
        default_path = BASE_DIR / "static/images/sin_foto.png"
        with open(default_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        print(f"⚠️ No se pudo cargar imagen por defecto: {e}")
        return ""

