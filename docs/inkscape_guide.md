# Guía: Importar imágenes en Inkscape para verificar bounding boxes

## Problema

Cuando importas una imagen en Inkscape y las coordenadas de los bounding boxes (generados por EasyOCR) no coinciden con lo que ves en el editor.

## Solución

Usar la opción **"Enlazar"** al importar la imagen, con la configuración correcta de resolución.

## Pasos

1. Abrir Inkscape
2. Ir a **Archivo → Importar** (o Ctrl+I)
3. Seleccionar la imagen (`.jpg`, `.png`, etc.)
4. En el diálogo de importación, configurar:

| Opción | Valor |
|--------|-------|
| **Tipo de imagen importada** | Enlazar |
| **PPP de la imagen** | Resolución de importación predeterminada |
| **Modo de renderizado de imagen** | Ninguno (auto) |

5. Hacer clic en **OK**

## Configuración correcta

```
Tipo de imagen importada:  ○ Incrustar  ● Enlazar
PPP de la imagen:          ○ Desde archivo  ● Resolución de importación predeterminada
Modo de renderizado:       ● Ninguno (auto)  ○ Suave  ○ Bloques
```

![inkscape importar de forma adecuada sin perder tamano de px 2026-07-23 00 29 24](assets/inkscape%20importar%20de%20forma%20adecuada%20sin%20perder%20tamano%20de%20px%202026-07-23%2000%2029%2024.jpg)


## Verificación

Una vez importada la imagen:

1. Seleccionar la imagen
2. Verificar en la barra de propiedades que las dimensiones coincidan con la resolución original (ej: 933x451 px)
3. Las coordenadas de Inkscape ahora coincidirán con las del archivo Markdown generado por el OCR

## Nota importante

- **Enlazar** mantiene la imagen como referencia externa (el archivo .svg no contiene la imagen)
- **Incrustar** pega la imagen dentro del SVG, pero puede cambiar la escala
- La **resolución predeterminada** asegura que 1 píxel = 1 unidad en Inkscape

## Ejemplo práctico

Imagen: `2026-07-10 01 19 25.jpg` (933x451 px)

Precio detectado: `63791`
Coordenadas OCR: X1=87, Y1=429, X2=125, Y2=445

En Inkscape (con configuración correcta):
- El rectángulo debe estar en la parte inferior izquierda
- Coordenadas: (87, 429) a (125, 445)
- Ancho: 38px, Alto: 16px