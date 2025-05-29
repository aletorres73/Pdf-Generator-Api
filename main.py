from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import List
from models import ItemPdf
from pdf_generator import generate_pdf
import io
import time

app = FastAPI()

MAX_ITEMS = 20  # Límite máximo de ítems permitidos


@app.post("/generate-pdf")
def create_pdf(items: List[ItemPdf]):
    total_received = len(items)
    print(f"📥 Recibidos {total_received} ítems")

    if total_received > MAX_ITEMS:
        print(f"⚠ Se procesarán solo los primeros {MAX_ITEMS} ítems (de {total_received})")
        items = items[:MAX_ITEMS]

    start = time.time()
    pdf_buffer = generate_pdf([item.model_dump() for item in items])
    duration = time.time() - start

    pdf_size_mb = round(pdf_buffer.getbuffer().nbytes / (1024 * 1024), 4)
    print(f"✅ PDF generado en {duration:.2f} segundos")
    print(f"📄 Tamaño del PDF: {pdf_size_mb} MB")

    return StreamingResponse(
        io.BytesIO(pdf_buffer.getvalue()),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=stock_report.pdf"}
    )
