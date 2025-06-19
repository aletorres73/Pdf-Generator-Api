from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from models import StockModel
from weasyprint import HTML
from pathlib import Path
import os
from utils.image_utils import resize_and_encode_image, get_default_image_base64

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
PDF_OUTPUT_PATH = BASE_DIR / "pdf/preview.pdf"
templates = Jinja2Templates(directory="templates")

default_image_b64 = get_default_image_base64(BASE_DIR)

# --- Endpoint ---
@app.post("/preview-html-pdf")
async def preview_pdf(items: List[StockModel], request: Request):
    try:
        print("🔧 Iniciando generación de PDF...")

        for item in items:
            for color_group in item.stockByColors:
                if color_group.imageUrl and color_group.imageUrl.strip().lower() not in ["", "null", "none"]:
                    color_group.imageBase64 = resize_and_encode_image(color_group.imageUrl)
                else:
                    color_group.imageBase64 = default_image_b64

        print("🕒 Renderizando plantilla HTML...")
        html_str = templates.get_template("stock_preview.html").render({"items": items})
        print("✅ Plantilla HTML renderizada correctamente.")
        print("📄 Fragmento del HTML:", html_str[:300])

        os.makedirs(PDF_OUTPUT_PATH.parent, exist_ok=True)
        HTML(string=html_str, base_url=BASE_DIR.as_uri()).write_pdf(str(PDF_OUTPUT_PATH))
        print(f"✅ PDF generado en {PDF_OUTPUT_PATH}")

        return FileResponse(
            path=str(PDF_OUTPUT_PATH),
            media_type="application/pdf",
            filename="reporte_stock.pdf"
        )

    except Exception as e:
        print(f"🔥 Error general: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Ocurrió un error al generar el PDF", "detail": str(e)}
        )
