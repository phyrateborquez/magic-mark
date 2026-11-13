# Comparación A/B repetida — 12 de noviembre de 2026

Magic Mark 0.1.2, Firefox 159.0.1, un perfil de prueba separado. Tres páginas públicas reales; orden AB, BA, AB. A = extensión desinstalada. B = extensión instalada y 20 rangos repetidos en un párrafo. Se observaron 60 segundos por fase, más cinco de asentamiento: seis fases completas y unos 6.5 minutos más navegación/acciones.

| Página / orden | A: CPU / RSS | B: CPU / RSS | Diferencia B−A |
| --- | --- | --- | --- |
| https://example.com/ / AB | 18.22% / 1001.3 MiB | 2.60% / 855.7 MiB | -15.62 puntos / -145.6 MiB |
| https://en.wikipedia.org/wiki/Web_browser / BA | 1.04% / 1058.0 MiB | 1.72% / 1033.6 MiB | +0.68 puntos / -24.4 MiB |
| https://developer.mozilla.org/en-US/docs/Web/API/Range / AB | 1.28% / 1128.3 MiB | 1.20% / 1148.4 MiB | -0.08 puntos / +20.1 MiB |

Mediana exploratoria de B−A: -0.08 puntos porcentuales de un núcleo y -24.4 MiB RSS. No es una estimación causal fiable: el signo negativo, la dispersión y el primer A con CPU elevada muestran efectos de arranque, caché, GC y cargas de las páginas. No significa que añadir marcas ahorre memoria. No se estima un coste fijo por marca ni se prueba ausencia de fugas.

Las cifras cubren todo el árbol de procesos del Firefox aislado. RSS puede contar memoria compartida varias veces. CPU usa un núcleo lógico como referencia. La máquina realizó otras tareas de validación durante la sesión; no fue un laboratorio sin interferencia. Se conserva cada intervalo y no se descartan las muestras desfavorables.

Datos: artifacts/firefox-ab-results.json, complete=true. Los seis pares de modo/página se midieron sin fases ausentes. Reproducción: instalar la herramienta psutil de pruebas y ejecutar `python scripts/smoke-firefox.py --ab`. No se escribe almacenamiento desde la extensión; los resultados los escribe el controlador externo.


Nota de conservación / Retention note (13/11/2026): los diagnósticos, perfiles y navegadores locales de artifacts se eliminaron para conservar solo el repositorio fuente. Sus rutas en este documento son referencias históricas, no archivos distribuidos. Las capturas seleccionadas permanecen en store/screenshots. / Local diagnostics, profiles and browsers in artifacts were removed to retain only source repository files. Paths in this document are historical references, not distributed files. Selected screenshots remain in store/screenshots.
