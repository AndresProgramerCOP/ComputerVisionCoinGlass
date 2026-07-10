# Tareas - ComputerVisionCoinGlass

## Completado
- [x] Configurar entorno Python con uv
- [x] Instalar dependencias (OpenCV, EasyOCR, PaddleOCR, PyTorch)
- [x] Crear estructura del proyecto
- [x] Crear README.md
- [x] Primer commit en git
- [x] Subir repositorio a GitHub
- [x] Prueba OCR con imagen real de CoinGlass
- [x] Evaluar librerías OCR (EasyOCR, PaddleOCR, Tesseract)
- [x] **Decisión: Usar EasyOCR como librería principal**

## Pendiente

### Fase 1: Fundamentos
- [ ] Crear documentación de requisitos (docs/requirements.md)
- [ ] Crear documentación de arquitectura (docs/architecture.md)

### Fase 2: Pipeline de Captura
- [ ] Módulo de captura de imágenes (src/capture.py)
- [ ] Validación de imágenes de entrada

### Fase 3: Preprocesamiento
- [ ] Limpieza de imagen (src/preprocessing.py)
- [ ] Normalización de contraste y brillo
- [ ] Segmentación de regiones de interés (ROI)

### Fase 4: Detección
- [ ] Detección de barras (src/detection.py)
- [ ] Detección de curvas
- [ ] Identificación de ejes y escalas
- [ ] Extracción de leyenda

### Fase 5: OCR
- [ ] Extracción de texto (src/ocr.py)
- [ ] Extracción de números del eje X
- [ ] Extracción de valores del eje Y
- [ ] Extracción de precio actual

### Fase 6: Output
- [ ] Exportación a JSON (src/output.py)
- [ ] Exportación a CSV
- [ ] Generación de reporte resumen

### Fase 7: Tests
- [ ] Tests unitarios para cada módulo
- [ ] Tests de integración del pipeline

---

*Última actualización: 2026-07-09*
