# Validación 0.1.1

11 de noviembre de 2026. Proyecto local, sin firma ni publicación.

## Comprobaciones locales

`npm run verify` pasa: sintaxis, ocho pruebas automatizadas (núcleo, errores de inyección y límites de distribución), generación de manifiestos, web-ext 10.8.0 con cero errores/avisos/advertencias de validación y creación de tres ZIP con SHA-256. El mensaje del actualizador de web-ext sobre acceso a su configuración no es un fallo del paquete; no se modificó la configuración global para silenciarlo.

Las pruebas de distribución verifican versión coherente, longitud de descripción, permisos mínimos, ausencia de scripts automáticos y validez PNG de iconos. Los ZIP instalables solo incluyen manifiesto, background.js, dos iconos y LICENSE. El ZIP source usa lista explícita y no incluye perfiles, cachés, node_modules ni resultados privados.

## Firefox 159.0.1

Perfil separado, headless, instalación temporal del ZIP 0.1.1 y página exclusivamente en localhost. El controlador crea selecciones DOM y activa el evento command del atajo registrado por Firefox: ejercita permisos activeTab, proceso de fondo y scripting.executeScript de la extensión instalada. No equivale a pulsación física ni clic de ratón.

Pasaron: dos marcas, aislamiento de dos pestañas con la misma URL, pestaña nueva limpia tras cerrar otra, recarga, navegación atrás sin marcas, exclusión de editor y selección con negrita/enlace. Captura de dos párrafos revisada visualmente, incluido fondo oscuro. Resultados en artifacts/firefox-results.json; capturas magic-mark-firefox-highlighted.png y magic-mark-firefox-reloaded.png.

## Chromium 145.0.7632.6

Perfil temporal y navegador completo de Playwright. La extensión descomprimida carga y arranca su service worker. El atajo sintético en headless no activó la acción; por ello NO se declara integración completa de la extensión instalada.

Por separado, el núcleo original se evaluó directamente sobre DOM real: destacó y limpió correctamente. Este ensayo no valida permisos ni UI de Chromium. Resultados en artifacts/chromium-results.json y captura magic-mark-chromium-core.png. Requiere Playwright Python y Chromium instalado; no son dependencias de la extensión.

## Recursos: ensayo preliminar

Medición sobre el núcleo en una página de Chromium, no sobre toda la extensión instalada. Una ejecución local con selecciones repetidas, GC solicitado antes de medir heap y alrededor de un segundo de reposo por muestra:

| Rangos | Tiempo del lote | Heap JS total de la página | Tareas del renderer en reposo |
| --- | --- | --- | --- |
| 0 | 0 ms | 891956 bytes | 0.535 ms |
| 1 | 0.3 ms | 887576 bytes | 0.346 ms |
| 20 | 0.7 ms | 910184 bytes | 0.335 ms |
| 100 | 1.5 ms | 909096 bytes | 0.286 ms |

Heap tras limpiar: 907252 bytes. Fuente: artifacts/performance-core.json. El heap incluye la página y el controlador; no mide memoria nativa de Range/Highlight, RSS del navegador ni consumo del worker. Las diferencias pequeñas tienen ruido y GC/JIT. No interpretar la tabla como RAM exacta por marca ni CPU total de Magic Mark. No hay sondeo ni observación continua en el código de producción.

## Pendientes explícitos

Interacción física botón/menú/teclado, integración completa Chrome/Edge, versiones mínimas reales (manifiestos: Firefox escritorio 140, Android 142 y Chromium 123), páginas reales variadas, marcos, pruebas dinámicas amplias y accesibilidad con lector de pantalla. El soporte Android no se anuncia. Ya se completó un ensayo de CPU y memoria de los procesos Firefox en una sesión aislada de varios minutos: ver RESOURCE-USAGE.md. Quedan sesiones prolongadas con sitios reales, CI ejecutado en GitHub y revisión de tiendas.

La auditoría npm de herramientas detecta un aviso bajo en deepmerge propagado a addons-linter/web-ext; no se distribuyen en la extensión. Ver SECURITY.md. No es una auditoría exhaustiva de seguridad.

## Reproducir

Node.js 24 LTS y Python 3.10+: `npm ci --ignore-scripts`, `npm run verify`, `npm run test:firefox`. Para Chromium, instalar Playwright y su navegador en el entorno de desarrollo y ejecutar `python scripts/smoke-chromium.py`. Los ensayos abren perfiles aislados y conexiones localhost, y cierran sus navegadores al terminar. El script Firefox tiene ruta de ejecutable Windows explícita que se debe adaptar en otro sistema.

## Comprobación posterior de recursos y uso manual

El usuario confirmó que la prueba en la ventana de Firefox se veía bien; no se infiere que haya comprobado cada ruta de menú/teclado o accesibilidad. La automatización visual de Windows se bloqueó por falta de soporte de política de URLs para ese Firefox, por lo que no se presenta como una prueba visual automatizada completada.

Ensayo de procesos completado con Magic Mark 0.1.1: sin extensión, instalada sin marcas, 1/20/100 rangos, tres pestañas, recarga y cierre de pestañas marcadas. Ver RESOURCE-USAGE.md y artifacts/firefox-process-performance.json. La observación de 100 rangos duró 60 segundos; la suma de las ocho ventanas de muestreo fue de unos 170 segundos, más las acciones. Son cifras de Firefox completo, no de la extensión aislada.

## Versión posterior 0.1.2

La evidencia de la ampliación, corrección de rangos y comandos deshacer/borrar está en EXTENDED-VALIDATION.md. La tabla histórica de rendimiento del núcleo de esta página pertenece al ensayo inicial; performance-core.json contiene el último ensayo y se regenera. RESOURCE-USAGE.md conserva las cifras multiproceso de 0.1.1 sin atribuirlas a versiones posteriores.

## Integración instalada en Edge 157

Se completó una prueba de acción real a nivel de navegador mediante CDP con la extensión instalada, permisos activeTab y ruta de fondo. También pasaron deshacer/borrar desde el fondo, marco del mismo origen y aislamiento/recarga. Ver INSTALLED-BROWSER-VALIDATION.md; no se equipara a clic físico ni prueba de Chrome. La sonda separada de detención del worker fue inconclusa y no se marca aprobada.

## Confirmación humana de lector — 12/11/2026

El usuario confirmó que el lector anuncia correctamente el nombre Magic Mark y las opciones destacar selección, deshacer y borrar. No indicó navegador ni lector/versión. Se aprueba esa lectura de nombres; no se extrapola a foco, zoom, activación por teclado o menús dentro de marcos. Ver NATIVE-ACCESSIBILITY-CHECK.md.

## Corrección del atajo — 0.1.3

El usuario informó que Alt+Shift+M abre Marcadores en su Firefox. Se elimina suggested_key de los comandos distribuidos, manteniendo la asignación voluntaria por el usuario. Once pruebas y lint Firefox pasan; se repitieron la regresión Firefox con comandos configurados en copia de prueba y la integración Chrome 157 con acción, permisos, worker, marcos y pestañas. Los datos de rendimiento anteriores conservan sus versiones originales y no se presentan como mediciones nuevas.

## Confirmación manual de botón y Enter — 12/11/2026

El usuario confirmó que el botón destaca la selección y que Enter sobre deshacer elimina la última marca. Se actualizan ROADMAP.md y NATIVE-ACCESSIBILITY-CHECK.md; no se amplía esa evidencia a marcos, recorrido completo o Chrome 123.

## Controles nativos en Brave — 12/11/2026

Prueba posterior realizada por el agente en Brave conectado con la página local `tests/native.html`: clic en botón, segunda marca mediante menú con teclado, deshacer y borrar, menú dentro de marco del mismo origen, foco visible y activación del botón con Tab/Enter al 200%. Se restauró el zoom inicial al 90%. Capturas y alcance exacto en NATIVE-ACCESSIBILITY-CHECK.md. No se modificó producción ni se añadió permiso de host a la extensión. Esta prueba de Brave no sustituye la de Chrome 123.

## Cierre manual de Chrome 123 — 12/11/2026

El usuario confirmó que hizo todas las pruebas en Chrome 123 después del bloqueo del control nativo del agente. Se cierra el punto pendiente de activeTab nativo por esa confirmación humana; no se declara ejecutado por el agente ni se inventan capturas o resultados individuales. El alcance previsto del MVP de escritorio queda cerrado; atajo propio opcional, Android fuera de alcance y publicación todavía pendiente. Ver NATIVE-ACCESSIBILITY-CHECK.md.


Nota de conservación / Retention note (13/11/2026): los diagnósticos, perfiles y navegadores locales de artifacts se eliminaron para conservar solo el repositorio fuente. Sus rutas en este documento son referencias históricas, no archivos distribuidos. Las capturas seleccionadas permanecen en store/screenshots. / Local diagnostics, profiles and browsers in artifacts were removed to retain only source repository files. Paths in this document are historical references, not distributed files. Selected screenshots remain in store/screenshots.
