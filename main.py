from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from models import StockModel
from weasyprint import HTML
from pathlib import Path
import os
from PIL import Image
from io import BytesIO
import requests
import base64
from utils.image_utils import resize_and_encode_image

def resize_and_encode_image(url, size=(300, 300)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img.thumbnail(size)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=70)
    return base64.b64encode(buffer.getvalue()).decode()


app = FastAPI()

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
PDF_OUTPUT_PATH = BASE_DIR / "pdf/preview.pdf"

# Configurar Jinja2 y filtros
templates = Jinja2Templates(directory="templates")

@app.post("/preview-html-pdf")
async def preview_pdf(items: List[StockModel], request: Request):
    try:
        print("🔧 Iniciando generación de PDF...")

        # DEFAULT_IMAGE_PATH = "/static/images/sin_foto.png"
        # Reemplazar imágenes por versión base64 optimizada
        for item in items:
            for color_group in item.stockByColors:
                if color_group.imageUrl and color_group.imageUrl.strip().lower() not in ["", "null", "none"]:
                    color_group.imageBase64 = resize_and_encode_image(color_group.imageUrl)
                else:
                    # Si no hay imagen, podés usar una imagen por defecto en base64 también
                    color_group.imageBase64 = ""

        # Renderizar plantilla HTML
        print("🕒 Renderizando plantilla HTML para PDF...")

        html_str = templates.get_template("stock_preview.html").render({"items": items})


        print("✅ Plantilla HTML renderizada correctamente.")
        print("📄 Fragmento del HTML generado:")
        print(html_str[:300])

        os.makedirs(PDF_OUTPUT_PATH.parent, exist_ok=True)

        print("🖨️ Generando archivo PDF con WeasyPrint...")
        HTML(string=html_str, base_url=BASE_DIR.as_uri()).write_pdf(str(PDF_OUTPUT_PATH))

        print(f"✅ PDF guardado exitosamente en {PDF_OUTPUT_PATH}")

        return FileResponse(
            path=str(PDF_OUTPUT_PATH),
            media_type="application/pdf",
            filename="reporte_stock.pdf"
        )

    except Exception as e:
        print(f"🔥 Excepción durante la generación del PDF: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Ocurrió un error al generar el PDF", "detail": str(e)}
        )
