"""Prueba OCR — extracción de precios del eje X"""
import easyocr
import cv2
import sys
import re

# Cargar imagen
img_path = sys.argv[1] if len(sys.argv) > 1 else "data/input/imagen coinglass 2026-07-09 15 28 44.png"
img = cv2.imread(img_path)

if img is None:
    print("❌ No se pudo cargar la imagen")
    sys.exit(1)

print(f"✅ Imagen: {img.shape[1]}x{img.shape[0]} px")

# Inicializar EasyOCR
print("⏳ Cargando modelo OCR...")
reader = easyocr.Reader(['es', 'en'], gpu=False)

# Extraer texto
print("🔍 Extrayendo texto...\n")
results = reader.readtext(img_path)

# Separar por tipo
precios = []
otros = []

for bbox, text, conf in results:
    # Detectar precios del eje X (números de 5 dígitos que empiezan con 6)
    if re.match(r'^6[1-4]\d{3}$', text.strip()):
        precios.append((bbox, text.strip(), conf))
    else:
        otros.append((bbox, text.strip(), conf))

# Ordenar precios por posición X (izquierda a derecha)
precios.sort(key=lambda x: x[0][0][0])

# Mostrar resultados
print("=" * 60)
print("📊 PRECIOS DEL EJE X (ordenados de izq a der)")
print("=" * 60)
print(f"\nTotal encontrados: {len(precios)}\n")

for i, (bbox, text, conf) in enumerate(precios, 1):
    x1, y1 = int(bbox[0][0]), int(bbox[0][1])  # Esquina superior-izquierda
    x2, y2 = int(bbox[2][0]), int(bbox[2][1])  # Esquina inferior-derecha
    ancho = x2 - x1
    alto = y2 - y1
    print(f"  {i:2d}. [{conf:.2f}] ${text:>6}  |  x={x1}-{x2}  y={y1}-{y2}  ({ancho}x{alto}px)")

print("\n" + "=" * 60)
print("📋 OTROS TEXTOS")
print("=" * 60)

for i, (bbox, text, conf) in enumerate(otros, 1):
    print(f"  {i:2d}. [{conf:.2f}] {text}")

# Guardar resultados en Markdown con YAML frontmatter
from datetime import datetime

metadata = {
    "titulo": "Resultados OCR — CoinGlass",
    "fecha": datetime.now().strftime("%Y-%m-%d"),
    "imagen": img_path,
    "resolucion": f"{img.shape[1]}x{img.shape[0]}",
    "libreria": "EasyOCR",
    "total_textos": len(results),
    "total_precios": len(precios),
    "formato_salida": "markdown",
}

with open("data/output/ocr_results.md", "w", encoding="utf-8") as f:
    # YAML frontmatter desde diccionario
    f.write("---\n")
    for key, value in metadata.items():
        if isinstance(value, str):
            f.write(f'{key}: "{value}"\n')
        else:
            f.write(f"{key}: {value}\n")
    f.write("---\n\n")
    f.write("# Resultados OCR — CoinGlass\n\n")

    # Precios del eje X
    f.write("## Precios del Eje X\n\n")
    f.write("| # | Precio | Confianza | X1 | Y1 | X2 | Y2 | Ancho | Alto |\n")
    f.write("|---|--------|-----------|----|----|----|----|-------|------|\n")
    for i, (bbox, text, conf) in enumerate(precios, 1):
        x1, y1 = int(bbox[0][0]), int(bbox[0][1])
        x2, y2 = int(bbox[2][0]), int(bbox[2][1])
        ancho = x2 - x1
        alto = y2 - y1
        f.write(f"| {i} | ${text} | {conf:.2f} | {x1} | {y1} | {x2} | {y2} | {ancho} | {alto} |\n")

    # Otros textos
    f.write("\n## Otros Textos\n\n")
    f.write("| # | Texto | Confianza | X1 | Y1 | X2 | Y2 |\n")
    f.write("|---|-------|-----------|----|----|----|----|\n")
    for i, (bbox, text, conf) in enumerate(otros, 1):
        x1, y1 = int(bbox[0][0]), int(bbox[0][1])
        x2, y2 = int(bbox[2][0]), int(bbox[2][1])
        f.write(f"| {i} | {text} | {conf:.2f} | {x1} | {y1} | {x2} | {y2} |\n")

print("\n✅ Resultados guardados en data/output/ocr_results.md")
