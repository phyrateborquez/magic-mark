# Medición de recursos — Magic Mark 0.1.1

Ensayo completado el 11 de noviembre de 2026 en Windows, Firefox 159.0.1 headless, perfil aislado y página local. Se midieron los procesos Firefox de ese perfil, incluidos sus descendientes. No se midió el Firefox habitual del usuario.

| Escenario | Observación | CPU media¹ | RSS mediana² | Memoria privada³ |
| --- | --- | --- | --- | --- |
| Firefox sin Magic Mark, una pestaña | 15 s | 8.22% | 806.7 MiB | 606.1 MiB |
| Magic Mark instalado, sin marcas | 15 s | 12.48% | 808.2 MiB | 610.3 MiB |
| Una pestaña, 1 rango | 15 s | 4.47% | 779.6 MiB | 570.6 MiB |
| Una pestaña, 20 rangos | 15 s | 5.31% | 798.7 MiB | 590.6 MiB |
| Una pestaña, 100 rangos | 60 s | 1.33% | 817.5 MiB | 602.7 MiB |
| Tres pestañas, 140 rangos | 20 s | 3.98% | 948.7 MiB | 673.9 MiB |
| Primera pestaña recargada; otras dos marcadas | 15 s | 5.52% | 966.1 MiB | 684.3 MiB |
| Una pestaña limpia tras cerrar las marcadas | 15 s | 0.94% | 816.4 MiB | 591.8 MiB |

¹ Porcentaje de un núcleo lógico, sumado entre los procesos; no porcentaje de toda la máquina. ² RSS es memoria residente sumada: puede contar páginas compartidas más de una vez. ³ Memoria privada comprometida, no necesariamente residente en RAM. No sumar las columnas RSS y privada.

## Lectura de los resultados

La observación de 100 rangos durante un minuto produjo 1.33% de un núcleo y 817.5 MiB RSS para el Firefox completo. Tras recargar y cerrar las otras pestañas marcadas, la página restante tenía cero destacados; la muestra final produjo 0.94% de un núcleo y 816.4 MiB RSS.

Estas cifras NO son el consumo exclusivo de Magic Mark. Firefox ya utilizaba 806.7 MiB RSS sin la extensión en la muestra inicial. Las etapas se midieron en secuencia: instalación, carga de procesos, apertura de pestañas, cachés y GC explican parte de las variaciones. Por ejemplo, la muestra inicial con la extensión instalada sin marcas mostró más CPU que la muestra con 100 rangos. No es válido calcular RAM por destacado o atribuir una diferencia pequeña al complemento.

No aparecieron fallos de marcado, recarga ni cierre durante el ensayo. El código de producción no cambió y sigue sin temporizadores, observadores, almacenamiento o red. El ensayo no prueba ausencia de fugas ni permite asegurar un coste fijo o mínimo absoluto. La memoria del navegador no tiene por qué regresar inmediatamente al valor inicial al liberar marcas.

## Método y reproducción

Herramienta psutil 7.1.3, instalada únicamente en artifacts/test-tools. Muestreo cada 5 segundos; mediana de memoria y media temporal de CPU. Las selecciones fueron rangos repetidos sobre los mismos párrafos. No hubo llamadas del controlador a la página durante las ventanas de reposo; el muestreo de procesos fue externo. Pueden perderse contadores de procesos que terminen entre muestras.

La primera ejecución encontró un error del controlador al enumerar pestañas al final. Se corrigió el manejo de la respuesta de Marionette y se repitió el ensayo completo con guardado incremental. La tabla corresponde únicamente a la segunda ejecución, completa y exitosa.

Datos originales: artifacts/firefox-process-performance.json. El checkpoint separado es parcial por diseño; el informe final contiene complete=true.

Para repetir: `python -m pip install --target artifacts/test-tools psutil==7.1.3` y `npm run measure:firefox`. Se requiere Firefox en la ruta Windows indicada en scripts/smoke-firefox.py y permiso para procesos/conexiones localhost. Las herramientas no se incluyen en el paquete instalable.

Quedan como validaciones más amplias una sesión prolongada con sitios reales, varias repeticiones y comparación A/B estabilizada. No se ha ejecutado un ensayo equivalente en Chrome/Edge.


Nota de conservación / Retention note (13/11/2026): los diagnósticos, perfiles y navegadores locales de artifacts se eliminaron para conservar solo el repositorio fuente. Sus rutas en este documento son referencias históricas, no archivos distribuidos. Las capturas seleccionadas permanecen en store/screenshots. / Local diagnostics, profiles and browsers in artifacts were removed to retain only source repository files. Paths in this document are historical references, not distributed files. Selected screenshots remain in store/screenshots.
