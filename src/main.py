"""ComputerVisionCoinGlass — X-axis price extraction from CoinGlass screenshots."""
import easyocr
import cv2
import sys
import re
from pathlib import Path
from datetime import datetime

# Configuration
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")


def get_image_list(arg_path=None):
    """Return a sorted list of image files to process.

    If arg_path points to a file, return [file].
    If arg_path points to a directory, return all supported images inside.
    If arg_path is None, process all images in INPUT_DIR.
    Raises SystemExit when no images are found or the path is invalid.
    """
    extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}

    if arg_path:
        path = Path(arg_path)
        if path.is_file():
            return [path]
        elif path.is_dir():
            return sorted([f for f in path.iterdir() if f.suffix.lower() in extensions])
        else:
            print(f"Error: path not found: {arg_path}")
            sys.exit(1)
    else:
        images = sorted([f for f in INPUT_DIR.iterdir() if f.suffix.lower() in extensions])
        if not images:
            print("Error: no images found in data/input/")
            sys.exit(1)
        return images


def process_image(img_path, reader):
    """Run OCR on a single image and classify detected text into categories.

    Returns a dict with keys: img, results, prices, others, exchange_pair,
    timeframe. Returns None if the image cannot be loaded.
    """
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Error: could not load image: {img_path}")
        return None

    results = reader.readtext(str(img_path))

    prices = []
    others = []
    exchange_pair = "unknown"
    timeframe = "unknown"

    for bbox, text, conf in results:
        text_clean = text.strip()

        # Detect exchange and trading pair (e.g. "Binance Perpetual BTC/USDT")
        if "Perpetuo" in text_clean or "Perpetual" in text_clean:
            parts = text_clean.split()
            if len(parts) >= 2:
                exchange = parts[0]
                pair = parts[1].replace("/", "_")
                exchange_pair = f"{exchange}_{pair}"

        # Detect timeframe keywords
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

        # Detect X-axis price values (any numeric string)
        elif re.match(r'^\d+([.,]\d+)?$', text_clean):
            prices.append((bbox, text_clean, conf))
        else:
            others.append((bbox, text_clean, conf))

    # Sort prices by horizontal position (left to right)
    prices.sort(key=lambda x: x[0][0][0])

    return {
        "img": img,
        "results": results,
        "prices": prices,
        "others": others,
        "exchange_pair": exchange_pair,
        "timeframe": timeframe,
    }


def extract_datetime(filename):
    """Extract date and time from an image filename.

    Expects the pattern: *YYYY-MM-DD HH MM SS.ext
    Returns (date_str, time_str) e.g. ("2026-07-10", "00.40").
    Returns (None, None) if the pattern is not found.
    """
    stem = Path(filename).stem
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})', stem)
    if match:
        year, month, day, hour, minute, _second = match.groups()
        return f"{year}-{month}-{day}", f"{hour}.{minute}"
    return None, None


def save_results(data, img_path):
    """Save OCR results as a Markdown file with YAML frontmatter.

    The output filename is derived from the exchange pair, timeframe,
    and the datetime extracted from the original image filename.
    """
    date_str, time_str = extract_datetime(img_path.name)
    if date_str is None:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H.%M")

    output_filename = OUTPUT_DIR / f"ocr_{data['exchange_pair']}_{data['timeframe']}_{date_str}_{time_str}.md"

    # Build YAML metadata
    pair_parts = data["exchange_pair"].split("_")
    metadata = {
        "title": "OCR Results — CoinGlass",
        "date": date_str,
        "time": time_str.replace(".", ":") + ":00",
        "image": str(img_path).replace("\\", "/"),
        "resolution": f"{data['img'].shape[1]}x{data['img'].shape[0]}",
        "library": "EasyOCR",
        "exchange": pair_parts[0] if len(pair_parts) > 1 else data["exchange_pair"],
        "pair": "_".join(pair_parts[1:]) if len(pair_parts) > 1 else "",
        "timeframe": data["timeframe"],
        "total_texts": len(data["results"]),
        "total_prices": len(data["prices"]),
        "output_format": "markdown",
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
        f.write("# OCR Results — CoinGlass\n\n")

        # X-axis prices table
        f.write("## X-Axis Prices\n\n")
        f.write("| # | Price | Confidence | X1 | Y1 | X2 | Y2 | Width | Height |\n")
        f.write("|---|-------|-----------|----|----|----|----|-------|--------|\n")
        for i, (bbox, text, conf) in enumerate(data['prices'], 1):
            x1, y1 = int(bbox[0][0]), int(bbox[0][1])
            x2, y2 = int(bbox[2][0]), int(bbox[2][1])
            width = x2 - x1
            height = y2 - y1
            f.write(f"| {i} | {text} | {conf:.2f} | {x1} | {y1} | {x2} | {y2} | {width} | {height} |\n")

        # Other detected texts table
        f.write("\n## Other Texts\n\n")
        f.write("| # | Text | Confidence | X1 | Y1 | X2 | Y2 |\n")
        f.write("|---|------|-----------|----|----|----|----|\n")
        for i, (bbox, text, conf) in enumerate(data['others'], 1):
            x1, y1 = int(bbox[0][0]), int(bbox[0][1])
            x2, y2 = int(bbox[2][0]), int(bbox[2][1])
            f.write(f"| {i} | {text} | {conf:.2f} | {x1} | {y1} | {x2} | {y2} |\n")

    return output_filename


def draw_bboxes(data, img_path):
    """Draw bounding boxes on the image and save to output directory.

    Green boxes for prices, blue for other detected texts.
    """
    img = data['img'].copy()

    # Colors in BGR
    COLOR_PRICE = (0, 255, 0)
    COLOR_OTHER = (255, 0, 0)

    # Draw price bounding boxes
    for bbox, text, conf in data['prices']:
        x1, y1 = int(bbox[0][0]), int(bbox[0][1])
        x2, y2 = int(bbox[2][0]), int(bbox[2][1])
        cv2.rectangle(img, (x1, y1), (x2, y2), COLOR_PRICE, 2)
        label = f"{text} ({conf:.2f})"
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_PRICE, 1)

    # Draw other text bounding boxes (limit to 10 to avoid clutter)
    for bbox, text, conf in data['others'][:10]:
        x1, y1 = int(bbox[0][0]), int(bbox[0][1])
        x2, y2 = int(bbox[2][0]), int(bbox[2][1])
        cv2.rectangle(img, (x1, y1), (x2, y2), COLOR_OTHER, 1)

    output_path = OUTPUT_DIR / f"bboxes_{img_path.stem}.jpg"
    cv2.imwrite(str(output_path), img)
    return output_path


def main():
    """Entry point: load images, run OCR, and save results."""
    arg_path = sys.argv[1] if len(sys.argv) > 1 else None
    images = get_image_list(arg_path)

    print(f"Images to process: {len(images)}\n")

    # Initialize EasyOCR once for all images
    print("Loading OCR model...")
    reader = easyocr.Reader(['es', 'en'], gpu=False)

    for i, img_path in enumerate(images, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(images)}] {img_path.name}")
        print(f"{'='*60}")

        data = process_image(img_path, reader)
        if data is None:
            continue

        # Print summary
        print(f"\nPrices found: {len(data['prices'])}")
        for j, (bbox, text, conf) in enumerate(data['prices'][:5], 1):
            print(f"  {j}. [{conf:.2f}] {text}")
        if len(data['prices']) > 5:
            print(f"  ... and {len(data['prices']) - 5} more")

        # Save markdown results
        output_file = save_results(data, img_path)
        print(f"\nSaved: {output_file.name}")

        # Save image with bounding boxes
        bbox_file = draw_bboxes(data, img_path)
        print(f"Bounding boxes: {bbox_file.name}")

    print(f"\n{'='*60}")
    print(f"Done: {len(images)} images processed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
