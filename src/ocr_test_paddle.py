"""Prueba OCR con PaddleOCR — comparación con EasyOCR"""
import cv2
import sys
import re
from paddleocr import PaddleOCR

# Cargar imagen
img_path = sys.argv[1] if len(sys.argv) > 1 else "data/input/imagen coinglass 2026-07-09 15 28 44.png"
img = cv2.imread(img_path)

if img is None:
    print("❌ No se pudo cargar la imagen")
    sys.exit(1)

print(f"✅ Imagen: {img.shape[1]}x{img.shape[0]} px")

# Inicializar PaddleOCR
print("⏳ Cargando PaddleOCR...")
ocr = PaddleOCR(use_angle_cls=True, lang='es', show_log=False)

# Extraer texto
print("🔍 Extrayendo texto con PaddleOCR...\n")
results = ocr.ocr(img_path, cls=True)

# PaddleOCR devuelve [[bbox, (text, conf)], ...]
raw_results = []
if results and results[0]:
    for line in results[0]:
        bbox = line[0]  # 4 puntos
        text = line[1][0]
        conf = line[1][1]
        raw_results.append((bbox, text, conf))

# Separar por tipo
precios = []
otros = []

for bbox, text, conf in raw_results:
    if re.match(r'^6[1-4]\d{3}$', text.strip()):
        precios.append((bbox, text.strip(), conf))
    else:
        otros.append((bbox, text.strip(), conf))

# Ordenar precios por posición X
precios.sort(key=lambda x: x[0][0][0])

# Mostrar resultados
print("=" * 60)
print("[PaddleOCR] PRECIOS DEL EJE X (ordenados de izq a der)")
print("=" * 60)
print(f"\nTotal encontrados: {len(precios)}\n")

for i, (bbox, text, conf) in enumerate(precios, 1):
    x1, y1 = int(bbox[0][0]), int(bbox[0][1])
    x2, y2 = int(bbox[2][0]), int(bbox[2][1])
    ancho = x2 - x1
    alto = y2 - y1
    print(f"  {i:2d}. [{conf:.2f}] ${text:>6}  |  x={x1}-{x2}  y={y1}-{y2}  ({ancho}x{alto}px)")

print("\n" + "=" * 60)
print("[PaddleOCR] OTROS TEXTOS")
print("=" * 60)

for i, (bbox, text, conf) in enumerate(otros, 1):
    print(f"  {i:2d}. [{conf:.2f}] {text}")

# Guardar resultados en Markdown
with open("data/output/ocr_results_paddle.md", "w", encoding="utf-8") as f:
    f.write("# Resultados OCR — PaddleOCR\n\n")
    f.write(f"**Librería:** PaddleOCR\n")
    f.write(f"**Imagen:** `{img_path}`\n")
    f.write(f"**Resolución:** {img.shape[1]}x{img.shape[0]} px\n")
    f.write(f"**Textos encontrados:** {len(raw_results)}\n\n")

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

print("\n✅ Resultados guardados en data/output/ocr_results_paddle.md")
