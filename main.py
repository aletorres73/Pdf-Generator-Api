from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import List
from models import ItemPdf
from pdf_generator import generate_pdf
import io
import time

app = FastAPI()


@app.post("/generate-pdf")
def create_pdf(items: List[ItemPdf]):
    print(f"Recibidos {len(items)} ítems")
    start = time.time()

    pdf_buffer = generate_pdf([item.model_dump() for item in items])

    print("PDF generado en", time.time() - start, "segundos")
    print("Tamaño del pdf: ",pdf_buffer.__sizeof__()/(1024*1024), "MB")

    return StreamingResponse(
        io.BytesIO(pdf_buffer.getvalue()),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=stock_report.pdf"}
    )
