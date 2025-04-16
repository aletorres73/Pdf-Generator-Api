from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import requests
from io import BytesIO
from reportlab.platypus import Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from datetime import datetime
import os
import requests
from PIL import Image
import tempfile


def generate_pdf(items):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Reporte de Stock - {datetime.now().strftime('%d/%m/%Y')}", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [["Modelo", "Color", "Stock", "Imagen"]]
    temp_files = []

    for item in items:
        try:
            # Intentar descargar la imagen original
            response = requests.get(item['image'], stream=True, timeout=10)
            img = Image.open(response.raw).convert("RGB")
        except Exception as e:
            print(f"Error con la imagen original: {e}")
            try:
                # Cargar imagen por defecto
                fallback_url = "https://firebasestorage.googleapis.com/v0/b/atypicaltracker.appspot.com/o/Common%2FempyImage_general.png?alt=media&token=43bdbfd5-4ff0-43f5-9873-da084f5c17be"
                response = requests.get(fallback_url, stream=True, timeout=10)
                img = Image.open(response.raw).convert("RGB")
            except Exception as fallback_error:
                print(f"Error cargando la imagen fallback: {fallback_error}")
                img = None

        if img:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webp") as tmp:
                img.save(tmp.name, format="WEBP")
                rl_img = RLImage(tmp.name, width=40, height=40)
                data.append([item['name'], item['color'], str(item['stock']), rl_img])
                temp_files.append(tmp.name)
        else:
            data.append([item['name'], item['color'], str(item['stock']), ""])
        print(f"Item {item['name']}: {item['color']} agregada")

    table = Table(data, colWidths=[160, 160, 60, 140], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)

    for path in temp_files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"No se pudo borrar {path}: {e}")

    buffer.seek(0)
    return buffer