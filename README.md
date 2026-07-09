# ComputerVisionCoinGlass

Sistema de visión por computadora para extracción de datos de mapas de liquidaciones de CoinGlass.

## Objetivo

Extraer automáticamente información estructurada (precios, niveles de apalancamiento, volumen de liquidaciones) a partir de capturas de pantalla de dashboards de CoinGlass.

## Estructura del Proyecto

```
├── docs/           # Documentación
├── src/            # Código fuente
├── tests/          # Pruebas
├── data/
│   ├── input/      # Imágenes de entrada
│   └── output/     # Resultados procesados
├── pyproject.toml  # Configuración del proyecto
└── README.md
```

## Tecnologías

- **Python 3.12** — Lenguaje principal
- **OpenCV** — Procesamiento de imágenes
- **EasyOCR / PaddleOCR** — Extracción de texto
- **NumPy** — Manejo de datos numéricos
- **Matplotlib** — Visualización

## Instalación

```bash
# Crear entorno virtual
uv venv --python 3.12

# Activar entorno
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
uv pip install -r requirements.txt
```

## Uso

```bash
python src/main.py --input data/input/imagen.png
```

## Pipeline

1. **Captura** — Obtener imagen del dashboard
2. **Preprocesamiento** — Limpiar y preparar imagen
3. **Detección** — Identificar regiones (barras, curvas, ejes)
4. **OCR** — Extraer texto y números
5. **Output** — Exportar datos estructurados (JSON/CSV)
