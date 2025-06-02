from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from typing import List
from models import StockModel
import os
from weasyprint import HTML

app = FastAPI()
templates = Jinja2Templates(directory="templates")

PDF_OUTPUT_PATH = "pdf/preview.pdf"

@app.post("/preview-html-pdf")
async def preview_pdf(items: List[StockModel], request: Request):
    try:
        print("🔧 Iniciando generación de PDF...")

        # Renderizado de plantilla HTML
        print("🕒 Renderizando plantilla HTML para PDF...")
        template_response = templates.TemplateResponse("stock_preview.html", {"request": request, "items": items})
        # await template_response.render()  # Necesario para forzar el render del contenido
        html_str = template_response.body.decode("utf-8")

        print("✅ Plantilla HTML renderizada correctamente.")
        print("📄 Fragmento del HTML generado:")
        print(html_str[:300])

        # Crear directorio para PDF si no existe
        os.makedirs(os.path.dirname(PDF_OUTPUT_PATH), exist_ok=True)

        # Generar PDF con WeasyPrint
        print("🖨️ Generando archivo PDF con WeasyPrint...")
        HTML(string=html_str, base_url=".").write_pdf(PDF_OUTPUT_PATH)

        print(f"✅ PDF guardado exitosamente en {PDF_OUTPUT_PATH}")

        return FileResponse(
            path=PDF_OUTPUT_PATH,
            media_type="application/pdf",
            filename="reporte_stock.pdf"
        )

    except Exception as e:
        print(f"🔥 Excepción durante la generación del PDF: {e}")
        return {"error": str(e)}
