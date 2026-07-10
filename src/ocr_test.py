"""Prueba OCR — extracción de precios del eje X"""
import easyocr
import cv2
import sys
import re
import os
from pathlib import Path
from datetime import datetime

# Configuración
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")

def get_image_list(arg_path=None):
    """Obtener lista de imágenes a procesar"""
    extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}

    if arg_path:
        path = Path(arg_path)
        if path.is_file():
            return [path]
        elif path.is_dir():
            return sorted([f for f in path.iterdir() if f.suffix.lower() in extensions])
        else:
            print(f"❌ No se encontró: {arg_path}")
            sys.exit(1)
    else:
        # Procesar todas las imágenes de data/input
        images = sorted([f for f in INPUT_DIR.iterdir() if f.suffix.lower() in extensions])
        if not images:
            print("❌ No hay imágenes en data/input/")
            sys.exit(1)
        return images

def process_image(img_path, reader):
    """Procesar una imagen y retornar resultados"""
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"❌ No se pudo cargar: {img_path}")
        return None

    # Extraer texto
    results = reader.readtext(str(img_path))

    # Separar por tipo
    precios = []
    otros = []
    exchange_par = "unknown"
    timeframe = "unknown"

    for bbox, text, conf in results:
        text_clean = text.strip()
        # Detectar exchange y par
        if "Perpetuo" in text_clean or "Perpetual" in text_clean:
            parts = text_clean.split()
            if len(parts) >= 2:
                exchange = parts[0]
                par = parts[1].replace("/", "_")
                exchange_par = f"{exchange}_{par}"
        # Detectar timeframe
        elif text_clean.lower() in ["día", "dia", "day", "días", "dias", "days"]:
            timeframe = "1d"
        elif text_clean.lower() in ["semana", "week", "weeks"]:
            timeframe = "7d"
        elif text_clean.lower() in ["mes", "month", "months"]:
            timeframe = "30d"
        elif text_clean.lower() in ["hora", "hour", "hours"]:
            timeframe = "1h"
        elif re.match(r'^(\d+)\s*d[ií]a', text_clean.lower()):
            match = re.match(r'^(\d+)\s*d[ií]a', text_clean.lower())
            timeframe = f"{match.group(1)}d"
        # Detectar precios del eje X
        elif re.match(r'^6\d{4}$', text_clean):
            precios.append((bbox, text_clean, conf))
        else:
            otros.append((bbox, text_clean, conf))

    # Ordenar precios por posición X
    precios.sort(key=lambda x: x[0][0][0])

    return {
        "img": img,
        "results": results,
        "precios": precios,
        "otros": otros,
        "exchange_par": exchange_par,
        "timeframe": timeframe,
    }

def save_results(data, img_path):
    """Guardar resultados en Markdown con YAML frontmatter"""
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H.%M")
    output_filename = OUTPUT_DIR / f"ocr_{data['exchange_par']}_{data['timeframe']}_{fecha}_{hora}.md"

    metadata = {
        "titulo": "Resultados OCR — CoinGlass",
        "fecha": fecha,
        "hora": now.strftime("%H:%M:%S"),
        "imagen": str(img_path),
        "resolucion": f"{data['img'].shape[1]}x{data['img'].shape[0]}",
        "libreria": "EasyOCR",
        "exchange": data['exchange_par'].split("_")[0] if "_" in data['exchange_par'] else data['exchange_par'],
        "par": "_".join(data['exchange_par'].split("_")[1:]) if "_" in data['exchange_par'] else "",
        "timeframe": data['timeframe'],
        "total_textos": len(data['results']),
        "total_precios": len(data['precios']),
        "formato_salida": "markdown",
    }

    with open(output_filename, "w", encoding="utf-8") as f:
        # YAML frontmatter
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
        for i, (bbox, text, conf) in enumerate(data['precios'], 1):
            x1, y1 = int(bbox[0][0]), int(bbox[0][1])
            x2, y2 = int(bbox[2][0]), int(bbox[2][1])
            ancho = x2 - x1
            alto = y2 - y1
            f.write(f"| {i} | {text} | {conf:.2f} | {x1} | {y1} | {x2} | {y2} | {ancho} | {alto} |\n")

        # Otros textos
        f.write("\n## Otros Textos\n\n")
        f.write("| # | Texto | Confianza | X1 | Y1 | X2 | Y2 |\n")
        f.write("|---|-------|-----------|----|----|----|----|\n")
        for i, (bbox, text, conf) in enumerate(data['otros'], 1):
            x1, y1 = int(bbox[0][0]), int(bbox[0][1])
            x2, y2 = int(bbox[2][0]), int(bbox[2][1])
            f.write(f"| {i} | {text} | {conf:.2f} | {x1} | {y1} | {x2} | {y2} |\n")

    return output_filename

def main():
    # Obtener imágenes
    arg_path = sys.argv[1] if len(sys.argv) > 1 else None
    images = get_image_list(arg_path)

    print(f"📁 Imágenes a procesar: {len(images)}\n")

    # Inicializar EasyOCR (una sola vez)
    print("⏳ Cargando modelo OCR...")
    reader = easyocr.Reader(['es', 'en'], gpu=False)

    # Procesar cada imagen
    for i, img_path in enumerate(images, 1):
        print(f"\n{'='*60}")
        print(f"🖼️  [{i}/{len(images)}] {img_path.name}")
        print(f"{'='*60}")

        data = process_image(img_path, reader)
        if data is None:
            continue

        # Mostrar resultados
        print(f"\n📊 Precios encontrados: {len(data['precios'])}")
        for j, (bbox, text, conf) in enumerate(data['precios'][:5], 1):
            print(f"  {j}. [{conf:.2f}] {text}")
        if len(data['precios']) > 5:
            print(f"  ... y {len(data['precios']) - 5} más")

        # Guardar
        output_file = save_results(data, img_path)
        print(f"\n✅ Guardado: {output_file.name}")

    print(f"\n{'='*60}")
    print(f"🎉 Proceso completado: {len(images)} imágenes")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
