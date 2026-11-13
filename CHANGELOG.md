# Cambios

## 0.1.3 — preparación local, sin publicar

- Atajos opcionales sin combinación predeterminada: el usuario informó que Alt+Shift+M abre Marcadores en su Firefox.
- Destacar, deshacer y borrar siguen disponibles en el menú; el botón sigue destacando la selección.
- Las pruebas asignan atajos solo en su copia aislada y la validación de distribución impide reintroducir defaults por accidente.

## 0.1.2 — preparación local, sin publicar

- Limpieza de rangos colapsados o desconectados al solicitar otra acción, sin observadores continuos.
- Lista propia de referencias para evitar restricciones de iteradores nativos de Firefox, también al deshacer.
- Diez pruebas automatizadas y ampliación de casos reales: CSP, editores, selección entre párrafos, reemplazo dinámico y páginas públicas.
- Prueba de deshacer/borrar mediante comandos configurados en una copia aislada; sin cambios en los atajos predeterminados distribuidos.

## 0.1.1 — preparación local, sin publicar

- Lint oficial Firefox sin errores ni advertencias y versión Android mínima coherente.
- Mínimo Chromium ajustado a 123 por la API Promise de contextMenus.removeAll.
- Manejo de errores de inyección y cierre de ventana más robusto.
- Construcción reproducible, archivo fuente, checksums y configuración CI.
- Nuevas pruebas y documentación de validación y publicación.

## 0.1.0 — preparación local, sin publicar

- Destacados amarillos nativos, independientes por documento.
- Botón, comando de teclado, menú contextual, deshacer y borrar.
- Sin persistencia, red, telemetría ni seguimiento continuo.
- Paquetes Firefox y Chromium; licencia MIT y documentación comunitaria.
- Validación Firefox aislada y herramientas locales para preparar publicación.
