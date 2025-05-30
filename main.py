from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from typing import List
from models import StockModel
from pdf_generator import generate_pdf
from xhtml2pdf import pisa
from weasyprint import HTML
import io
import time
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Carpeta donde van las plantillas

MAX_ITEMS = 20  # Límite máximo de ítems permitidos

from fastapi.responses import FileResponse

@app.post("/preview-html")
async def preview_html(items: List[StockModel], request: Request):
    try:
        print("🔧 Iniciando generación de HTML...")

        # Renderizado de plantilla
        print("🕒 Renderizando plantilla...")
        template_response = templates.TemplateResponse("stock_preview.html", {"request": request, "items": items})
        html_str = template_response.body.decode("utf-8")

        # Guardamos el HTML como archivo
        html_output_path = "html/preview.html"
        os.makedirs(os.path.dirname(html_output_path), exist_ok=True)
        with open(html_output_path, "w", encoding="utf-8") as f:
            f.write(html_str)

        print(f"✅ HTML guardado en {html_output_path}")
        print("📄 Fragmento del HTML generado:")
        print(html_str[:300])

        return FileResponse(
            path=html_output_path,
            media_type="text/html",
            filename="preview.html"
        )

    except Exception as e:
        print(f"🔥 Excepción durante la generación del HTML: {e}")
        return {"error": str(e)}