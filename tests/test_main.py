"""Tests for main.py"""
from pathlib import Path
from unittest.mock import patch

import pytest

from src.main import get_image_list, save_results, extract_datetime


# --- Tests for get_image_list ---

class TestGetImageList:
    """Tests for the get_image_list function"""

    def test_returns_specific_file(self, tmp_path):
        """If arg_path is a file, return [path]"""
        img = tmp_path / "test.png"
        img.touch()
        result = get_image_list(str(img))
        assert result == [img]

    def test_returns_filtered_directory(self, tmp_path):
        """If arg_path is a directory, return filtered image files only"""
        (tmp_path / "a.png").touch()
        (tmp_path / "b.jpg").touch()
        (tmp_path / "c.txt").touch()  # not an image
        (tmp_path / "d.webp").touch()

        result = get_image_list(str(tmp_path))
        names = [f.name for f in result]
        assert "c.txt" not in names
        assert len(result) == 3

    def test_files_sorted_alphabetically(self, tmp_path):
        """Files are returned in sorted order"""
        (tmp_path / "c.png").touch()
        (tmp_path / "a.jpg").touch()
        (tmp_path / "b.png").touch()

        result = get_image_list(str(tmp_path))
        names = [f.name for f in result]
        assert names == ["a.jpg", "b.png", "c.png"]

    def test_nonexistent_path_exits(self, tmp_path):
        """If the path does not exist, sys.exit(1) is called"""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(SystemExit):
            get_image_list(str(nonexistent))

    def test_empty_input_dir_exits(self, tmp_path):
        """If no images in INPUT_DIR, sys.exit(1) is called"""
        with patch("src.main.INPUT_DIR", tmp_path):
            with pytest.raises(SystemExit):
                get_image_list()

    def test_supports_all_extensions(self, tmp_path):
        """Supports png, jpg, jpeg, webp, bmp"""
        for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
            (tmp_path / f"img{ext}").touch()

        result = get_image_list(str(tmp_path))
        assert len(result) == 5

    def test_case_insensitive_extensions(self, tmp_path):
        """Extension filtering is case-insensitive"""
        (tmp_path / "a.PNG").touch()
        (tmp_path / "b.JPG").touch()
        (tmp_path / "c.txt").touch()

        result = get_image_list(str(tmp_path))
        assert len(result) == 2


# --- Tests for extract_datetime ---

class TestExtractDatetime:
    """Tests for the extract_datetime function"""

    def test_standard_filename(self):
        """Extracts date/time from standard filename format"""
        date_str, time_str = extract_datetime("2026-07-10 00 40 28.jpg")
        assert date_str == "2026-07-10"
        assert time_str == "00.40"

    def test_filename_with_prefix(self):
        """Extracts date/time even with text prefix"""
        date_str, time_str = extract_datetime("imagen coinglass 2026-07-09 15 28 44.png")
        assert date_str == "2026-07-09"
        assert time_str == "15.28"

    def test_filename_without_date(self):
        """Returns None when no date pattern is found"""
        date_str, time_str = extract_datetime("test.png")
        assert date_str is None
        assert time_str is None


# --- Tests for save_results ---

class TestSaveResults:
    """Tests for the save_results function"""

    def _make_data(self):
        """Create sample OCR data for testing"""
        fake_img = type("FakeImg", (), {"shape": (480, 640, 3)})()
        return {
            "img": fake_img,
            "results": [
                ([[[10, 20], [100, 20], [100, 50], [10, 50]], "Binance Perpetual BTC/USDT", 0.95]),
                ([[[200, 300], [280, 300], [280, 330], [200, 330]], "65000", 0.88]),
            ],
            "prices": [
                ([[[200, 300], [280, 300], [280, 330], [200, 330]], "65000", 0.88]),
            ],
            "others": [
                ([[[10, 20], [100, 20], [100, 50], [10, 50]], "Binance Perpetual BTC/USDT", 0.95]),
            ],
            "exchange_pair": "Binance_BTC_USDT",
            "timeframe": "1d",
        }

    def test_creates_file(self, tmp_path):
        """save_results creates a .md file"""
        data = self._make_data()
        img_path = Path("test.png")

        with patch("src.main.OUTPUT_DIR", tmp_path):
            result = save_results(data, img_path)

        assert result.exists()
        assert result.suffix == ".md"

    def test_filename_pattern(self, tmp_path):
        """Output filename follows ocr_*_YYYY-MM-DD_HH.MM.md pattern"""
        data = self._make_data()
        img_path = Path("2026-07-10 00 40 28.jpg")

        with patch("src.main.OUTPUT_DIR", tmp_path):
            result = save_results(data, img_path)

        assert result.name.startswith("ocr_")
        assert "Binance" in result.name
        assert "BTC_USDT" in result.name
        assert "1d" in result.name
        assert "2026-07-10" in result.name
        assert "00.40" in result.name

    def test_contains_yaml_frontmatter(self, tmp_path):
        """File has valid YAML frontmatter with date from the image"""
        data = self._make_data()
        img_path = Path("2026-07-10 00 40 28.jpg")

        with patch("src.main.OUTPUT_DIR", tmp_path):
            result = save_results(data, img_path)

        content = result.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "---" in content[4:]
        assert 'title:' in content
        assert 'date: "2026-07-10"' in content
        assert 'time: "00:40:00"' in content

    def test_contains_price_table(self, tmp_path):
        """File has price table with correct headers"""
        data = self._make_data()
        img_path = Path("test.png")

        with patch("src.main.OUTPUT_DIR", tmp_path):
            result = save_results(data, img_path)

        content = result.read_text(encoding="utf-8")
        assert "## X-Axis Prices" in content
        assert "| Price |" in content
        assert "| 65000 |" in content

    def test_contains_other_texts_table(self, tmp_path):
        """File has other texts table"""
        data = self._make_data()
        img_path = Path("test.png")

        with patch("src.main.OUTPUT_DIR", tmp_path):
            result = save_results(data, img_path)

        content = result.read_text(encoding="utf-8")
        assert "## Other Texts" in content
        assert "Binance" in content

    def test_metadata_complete(self, tmp_path):
        """YAML contains all required metadata fields"""
        data = self._make_data()
        img_path = Path("test.png")

        with patch("src.main.OUTPUT_DIR", tmp_path):
            result = save_results(data, img_path)

        content = result.read_text(encoding="utf-8")
        fields = ["title", "date", "time", "image", "resolution",
                   "library", "exchange", "pair", "timeframe",
                   "total_texts", "total_prices", "output_format"]
        for field in fields:
            assert f"{field}:" in content


# --- Integration tests (require EasyOCR) ---

@pytest.mark.slow
class TestIntegration:
    """Tests that require EasyOCR to be installed"""

    def test_process_real_image(self):
        """Process a real image from data/input/"""
        import easyocr

        from src.main import process_image

        input_dir = Path("data/input")
        if not input_dir.exists():
            pytest.skip("data/input/ directory not found")

        images = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
        if not images:
            pytest.skip("No images in data/input/")

        reader = easyocr.Reader(['es', 'en'], gpu=False)
        result = process_image(images[0], reader)

        assert result is not None
        assert "prices" in result
        assert "others" in result
        assert "exchange_pair" in result
        assert "timeframe" in result
        assert isinstance(result["prices"], list)
