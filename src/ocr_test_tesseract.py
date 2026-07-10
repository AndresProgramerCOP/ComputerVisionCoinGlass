"""Prueba OCR con Tesseract — comparación con EasyOCR"""
import cv2
import sys
import re
import pytesseract

# Configurar ruta de Tesseract (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Cargar imagen
img_path = sys.argv[1] if len(sys.argv) > 1 else "data/input/imagen coinglass 2026-07-09 15 28 44.png"
img = cv2.imread(img_path)

if img is None:
    print("❌ No se pudo cargar la imagen")
    sys.exit(1)

print(f"✅ Imagen: {img.shape[1]}x{img.shape[0]} px")

# Extraer texto con Tesseract
print("🔍 Extrayendo texto con Tesseract...\n")

# Obtener datos detallados con posiciones
data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

# Procesar resultados
precios = []
otros = []
n = len(data['text'])

for i in range(n):
    text = data['text'][i].strip()
    conf = int(data['conf'][i])

    if text and conf > 0:  # Solo textos con confianza > 0
        x = data['left'][i]
        y = data['top'][i]
        w = data['width'][i]
        h = data['height'][i]
        x2 = x + w
        y2 = y + h

        if re.match(r'^6[1-4]\d{3}$', text):
            precios.append((text, conf, x, y, x2, y2, w, h))
        elif len(text) > 2:  # Ignorar textos muy cortos
            otros.append((text, conf, x, y, x2, y2, w, h))

# Ordenar precios por posición X
precios.sort(key=lambda x: x[2])

# Mostrar resultados
print("=" * 60)
print("[Tesseract] PRECIOS DEL EJE X (ordenados de izq a der)")
print("=" * 60)
print(f"\nTotal encontrados: {len(precios)}\n")

for i, (text, conf, x1, y1, x2, y2, w, h) in enumerate(precios, 1):
    print(f"  {i:2d}. [{conf:3d}%] ${text:>6}  |  x={x1}-{x2}  y={y1}-{y2}  ({w}x{h}px)")

print("\n" + "=" * 60)
print("[Tesseract] OTROS TEXTOS")
print("=" * 60)

for i, (text, conf, x1, y1, x2, y2, w, h) in enumerate(otros[:20], 1):
    print(f"  {i:2d}. [{conf:3d}%] {text}")

# Guardar resultados en Markdown con YAML frontmatter
from datetime import datetime
fecha = datetime.now().strftime("%Y-%m-%d")

with open("data/output/ocr_results_tesseract.md", "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write(f"titulo: \"Resultados OCR — Tesseract\"\n")
    f.write(f"fecha: {fecha}\n")
    f.write(f"imagen: \"{img_path}\"\n")
    f.write(f"resolucion: \"{img.shape[1]}x{img.shape[0]}\"\n")
    f.write(f"libreria: \"Tesseract OCR 5.4.0\"\n")
    f.write(f"total_textos: {len(precios) + len(otros)}\n")
    f.write(f"total_precios: {len(precios)}\n")
    f.write(f"formato_salida: \"markdown\"\n")
    f.write("---\n\n")
    f.write("# Resultados OCR — Tesseract\n\n")

    # Precios del eje X
    f.write("## Precios del Eje X\n\n")
    f.write("| # | Precio | Confianza | X1 | Y1 | X2 | Y2 | Ancho | Alto |\n")
    f.write("|---|--------|-----------|----|----|----|----|-------|------|\n")
    for i, (text, conf, x1, y1, x2, y2, w, h) in enumerate(precios, 1):
        f.write(f"| {i} | ${text} | {conf}% | {x1} | {y1} | {x2} | {y2} | {w} | {h} |\n")

    # Otros textos
    f.write("\n## Otros Textos\n\n")
    f.write("| # | Texto | Confianza | X1 | Y1 | X2 | Y2 |\n")
    f.write("|---|-------|-----------|----|----|----|----|\n")
    for i, (text, conf, x1, y1, x2, y2, w, h) in enumerate(otros[:30], 1):
        f.write(f"| {i} | {text} | {conf}% | {x1} | {y1} | {x2} | {y2} |\n")

print("\n✅ Resultados guardados en data/output/ocr_results_tesseract.md")
