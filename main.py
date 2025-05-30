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

@app.post("/preview-html-pdf")
async def preview_html_pdf(items: List[StockModel], request: Request):
    try:
        start_total = time.time()
        print("🔧 Iniciando generación de PDF...")

        # Renderizado de plantilla
        print("🕒 Renderizando plantilla...")
        start_render = time.time()
        template_response = templates.TemplateResponse("stock_preview.html", {"request": request, "items": items})
        html_str = template_response.body.decode("utf-8")
        duration_render = time.time() - start_render

        # Guardamos el HTML como archivo
        html_output_path = "html/preview.html"
        os.makedirs(os.path.dirname(html_output_path), exist_ok=True)
        with open(html_output_path, "w", encoding="utf-8") as f:
            f.write(html_str)

        print(f"[LOG] HTML guardado en {html_output_path}")
        print(f"✅ Plantilla renderizada en {duration_render:.2f} segundos")

        # Verificamos contenido HTML
        print("📄 Fragmento del HTML generado:")
        print(html_str[:300])

        # Generación de PDF con WeasyPrint
        print("🕒 Generando PDF con WeasyPrint...")
        start_pdf = time.time()
        pdf_output = io.BytesIO()
        HTML(string=html_str, base_url=".").write_pdf(pdf_output)
        duration_pdf = time.time() - start_pdf

        pdf_size_bytes = len(pdf_output.getvalue())
        print(f"✅ PDF generado en {duration_pdf:.2f} segundos, tamaño: {pdf_size_bytes} bytes ({pdf_size_bytes / 1024:.2f} KB)")

        # Guardar PDF
        output_path = "pdfs/preview.pdf"
        print(f"💾 Guardando PDF en: {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_output.getvalue())
        print("✅ PDF guardado correctamente")

        # Reiniciar el buffer para enviar
        pdf_output.seek(0)

        total_duration = time.time() - start_total
        print(f"📤 Respuesta lista. Tiempo total de ejecución: {total_duration:.2f} segundos")

        return StreamingResponse(
            pdf_output,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=preview.pdf"}
        )

    except Exception as e:
        print(f"🔥 Excepción durante la generación del PDF: {e}")
        return {"error": str(e)}