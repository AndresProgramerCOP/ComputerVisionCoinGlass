# ComputerVisionCoinGlass

Sistema de visión por computadora para extracción de datos de mapas de liquidaciones de CoinGlass.

## Objetivo

Extraer automáticamente información estructurada (precios, niveles de apalancamiento, volumen de liquidaciones) a partir de capturas de pantalla de dashboards de CoinGlass.

## Estructura del Proyecto

```
├── docs/           # Documentación
├── src/            # Código fuente
│   └── main.py     # Entrypoint principal
├── tests/          # Pruebas
├── data/
│   ├── input/      # Imágenes de entrada
│   └── output/     # Resultados procesados (Markdown)
├── pyproject.toml  # Configuración del proyecto
└── README.md
```

## Tecnologías

- **Python 3.12** — Lenguaje principal
- **OpenCV** — Procesamiento de imágenes
- **EasyOCR** — Extracción de texto (español + inglés)
- **NumPy** — Manejo de datos numéricos
- **Pillow** — Manejo de imágenes
- **Matplotlib** — Visualización
- **Pandas** — Manipulación de datos

## Instalación

```bash
# Crear entorno virtual e instalar dependencias
uv venv --python 3.12
uv pip install .

# Dependencias de desarrollo (pytest, ruff)
uv pip install ".[dev]"
```

## Uso

```bash
# Procesar todas las imágenes en data/input/
uv run python src/main.py

# Procesar una imagen específica
uv run python src/main.py "data/input/imagen.png"

# Procesar todas las imágenes de un directorio
uv run python src/main.py "data/input/"
```

Los resultados se guardan en `data/output/` como archivos Markdown con YAML frontmatter.

## Pipeline

1. **Entrada** — Carga imagen(es) de `data/input/`
2. **OCR** — EasyOCR extrae texto (precios, exchange, par, timeframe)
3. **Clasificación** — Clasifica detecciones por tipo
4. **Ordenamiento** — Ordena precios por posición X en la imagen
5. **Output** — Exporta como Markdown con metadatos YAML

## Formato de Salida

Cada resultado es un archivo `.md` con:

- **YAML frontmatter**: metadata (exchange, par, timeframe, fecha, resolución, etc.)
- **Tabla de precios**: precio, confianza, coordenadas bounding box
- **Tabla de otros textos**: texto detectado, confianza, coordenadas

Nombre del archivo: `ocr_{exchange}_{pair}_{timeframe}_{fecha}_{hora}.md`

## Roadmap

Ver `docs/tasks.md` para el plan completo de 7 fases. Actualmente: Fase 5 (extracción OCR) parcialmente implementada.
