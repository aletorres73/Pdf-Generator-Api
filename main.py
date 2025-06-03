from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from models import StockModel
from weasyprint import HTML
from pathlib import Path
import os

app = FastAPI()

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent
PDF_OUTPUT_PATH = BASE_DIR / "pdf/preview.pdf"

# Configurar Jinja2 y filtros
templates = Jinja2Templates(directory="templates")

# Filtro para usar imagen por defecto si la ruta viene vacía
# def default_image(image_url: str) -> str:
#     if not image_url or image_url.strip().lower() in ["", "null", "none"]:
#         return "/static/images/sin_foto.png"
#     return image_url

# Registrar el filtro en Jinja2
# templates.env.filters["default_image"] = default_image

# Montar la carpeta de archivos estáticos
# app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.post("/preview-html-pdf")
async def preview_pdf(items: List[StockModel], request: Request):
    try:
        print("🔧 Iniciando generación de PDF...")

        # Reemplazar imágenes vacías por defecto
        # DEFAULT_IMAGE_PATH = "/static/images/sin_foto.png"
        for item in items:
            print(item,'\n')
            for color_group in item.stockByColors:
                if not color_group.imageUrl or color_group.image.strip().lower() in ['', "null", "none"]:
                    color_group.imageUrl = (BASE_DIR / "static/images/sin_foto.png").as_uri()

            print(item,'\n')

        # Renderizar plantilla HTML
        print("🕒 Renderizando plantilla HTML para PDF...")
        template_response = templates.TemplateResponse(
            "stock_preview.html",
            {"request": request, "items": items}
        )

        html_str = template_response.body.decode("utf-8")
        
        # # Guardar el HTML generado en un archivo para revisión temporal
        # html_preview_path = PDF_OUTPUT_PATH.parent / "preview_stock.html"
        # with open(html_preview_path, "w", encoding="utf-8") as f:
        #     f.write(html_str)
        # print(f"📝 HTML guardado para vista previa en {html_preview_path}")


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
