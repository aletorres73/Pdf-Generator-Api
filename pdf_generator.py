from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
from PIL import Image
import requests
import tempfile
import os
import time

def generate_pdf(items):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Iniciando generación de PDF con {len(items)} ítems...")
    start_time = time.time()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Reporte de Stock - {datetime.now().strftime('%d/%m/%Y')}", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Encabezado actualizado: Imagen va primero
    data = [["Imagen", "Modelo", "Color", "Stock"]]
    temp_files = []

    fallback_url = "https://firebasestorage.googleapis.com/v0/b/atypicaltracker.appspot.com/o/Common%2FempyImage_general.png?alt=media&token=43bdbfd5-4ff0-43f5-9873-da084f5c17be"

    img_success = 0
    img_fail = 0

    for idx, item in enumerate(items):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ▶ Procesando ítem {idx+1}/{len(items)}: {item['name']} - {item['color']}")
        img = None
        for url_to_try in [item.get("image"), fallback_url]:
            try:
                if not url_to_try:
                    continue
                response = requests.get(url_to_try, stream=True, timeout=5)
                response.raise_for_status()
                img = Image.open(response.raw).convert("RGB")
                print(f"✅ Imagen cargada correctamente desde: {url_to_try}")
                break
            except Exception as e:
                print(f"❌ Error cargando imagen desde {url_to_try}: {e}")
                continue

        # Agregar fila con imagen como primera columna
        if img:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webp") as tmp:
                    img.save(tmp.name, format="WEBP", quality=0.00001)
                    rl_img = RLImage(tmp.name, width=75, height=35)
                    row = [rl_img, item['name'], item['color'], str(item['stock'])]
                    data.append(row)
                    temp_files.append(tmp.name)
                    img_success += 1
            except Exception as e:
                print(f"⚠ Error guardando imagen temporal para {item['name']}: {e}")
                data.append(["", item['name'], item['color'], str(item['stock'])])
                img_fail += 1
        else:
            data.append(["", item['name'], item['color'], str(item['stock'])])
            img_fail += 1

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⌛ Generando PDF... ")
    # Ajuste de orden de columnas y anchos
    table = Table(data, colWidths=[100, 150, 140, 60], repeatRows=1)
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
            print(f"🧹 No se pudo borrar imagen temporal {path}: {e}")

    buffer.seek(0)

    total_time = time.time() - start_time
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ PDF generado en {total_time:.2f} segundos")
    print(f"📦 Imágenes exitosas: {img_success} | 🧨 Fallidas: {img_fail}")
    print(f"📄 Tamaño final del PDF: {round(buffer.getbuffer().nbytes / 1024 / 1024, 4)} MB")

    return buffer