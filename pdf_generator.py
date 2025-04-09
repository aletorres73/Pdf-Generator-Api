from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from datetime import datetime
import requests
from PIL import Image
import tempfile
import os

def generate_pdf(items):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Reporte de Stock - {datetime.now().strftime('%d/%m/%Y')}")

    y_position = height - 100

    data = [["Modelo", "Color", "Stock", "Imagen"]]
    temp_files = []

    for item in items:
        try:
            # Descargar imagen
            response = requests.get(item['image'], stream=True)
            img = Image.open(response.raw)
            img = img.convert("RGB")

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img.save(tmp.name, format="PNG")
                rl_img = RLImage(tmp.name, width=65, height=65)
                data.append([item['name'], item['color'], str(item['stock']), rl_img])
                temp_files.append(tmp.name)

        except Exception as e:
            print(f"Error con la imagen: {e}")
            data.append([item['name'], item['color'], str(item['stock']), ""])

    # Crear tabla
    table = Table(data, colWidths=[150, 150, 60, 120], repeatRows=1)
    table.setStyle(TableStyle([
    # Encabezado: TODAS las columnas
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),          # aplica desde columna 0 a la última (-1)
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),       # fuente en negrita
    ('FONTSIZE', (0, 0), (-1, 0), 10),                     # tamaño fuente
    # Contenido: centrado y con bordes
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                  
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))


    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y_position - len(data) * 60)

    c.save()
    buffer.seek(0)

    # Borrar archivos temporales
    for path in temp_files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"No se pudo borrar {path}: {e}")

    return buffer
