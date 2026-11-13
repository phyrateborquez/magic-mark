# Magic Mark: investigación y decisión actualizada

11 de noviembre de 2026. El alcance confirmado sustituye la propuesta inicial: **no almacenar ni recuperar marcas**. Estado exclusivo en memoria volátil del documento; se pierde al recargar, navegar, cerrar o descargar la pestaña. Sin storage.session ni anclajes de texto.

JavaScript, CSS Custom Highlight API y WebExtensions MV3. Código compartido y manifiestos distintos para Firefox (background scripts) y Chromium (service worker). Solo activeTab, scripting y contextMenus. Sin dependencias de ejecución.

Referentes documentales: Web Highlights, Mark My Word y penciled. Se tomó como referencia conceptual la pintura nativa sin envolver texto; no se copió código de esos proyectos. No se utiliza su persistencia ni restauración.

Fuentes:

- https://developer.mozilla.org/en-US/docs/Web/API/CSS_Custom_Highlight_API
- https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/scripting/executeScript
- https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/background
- https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Content_scripts
- https://extensionworkshop.com/documentation/develop/firefox-builtin-data-consent/
- https://web-highlights.com/docs/introduction/installation
- https://mark-my-word.app/
- https://github.com/marcellosso/penciled

Roadmap vigente: ROADMAP.md. Descripciones de publicación: STORE-LISTING.md. No se han auditado exhaustivamente ni medido los referentes.
