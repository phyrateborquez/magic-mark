# Publicar Magic Mark / Publishing Magic Mark

## Español

### Estado

Código y material ES/EN preparados. Textos y capturas aprobados por el mantenedor el 13/11/2026, con posibilidad de modificarlos después. Código publicado y primera ejecución CI aprobada. Repositorio: https://github.com/phyrateborquez/magic-mark. Mantenedor público: phyrateborquez; contacto por Issues, sin publicar correo personal. Publicación en tiendas aplazada por decisión del mantenedor: no se debe iniciar aún.

El mantenedor es la persona o cuenta que administra el proyecto, recibe avisos y publica versiones. Se usará el usuario público de GitHub propietario; no hace falta publicar un nombre legal ni correo personal. No se requieren contraseñas ni tokens en archivos o conversaciones.

### 1. Acceso y repositorio GitHub

Si GitHub CLI no tiene acceso vigente, ejecuta `gh auth login -h github.com`. Elige GitHub.com, HTTPS y “Login with a web browser”; sigue las instrucciones oficiales de autenticación. No publiques los códigos. Comprueba `gh auth status`.

Crear repositorio público `magic-mark` bajo la cuenta elegida, subir únicamente el árbol de código y revisar que CI termine correctamente. No incluir node_modules, artifacts, dist, cachés, perfiles ni navegadores. `.gitignore` evita su seguimiento; no reduce su tamaño local por sí solo.

Descripción ES: Destacador temporal para Firefox y Chromium. Sin cuentas ni almacenamiento. Código abierto bajo MIT.

Description EN: Temporary text highlighter for Firefox and Chromium. No accounts or storage. Open source under MIT.

### 2. Soporte y seguridad

Usar Issues para consultas/errores sin datos privados. Habilitar Private Vulnerability Reporting en Settings → Advanced Security; comprobar Security → Advisories → Report a vulnerability y las notificaciones. Solo anunciar el canal privado después de verificar su activación. Añadir URLs reales a SUPPORT.md, SECURITY.md y store/metadata.json. No se necesita correo público personal.

### 3. Reconstruir y probar

Requisitos: Node.js 24 LTS y Python 3.10+. Ejecutar `npm ci --ignore-scripts` y `npm run verify`. Genera dist y ZIP en artifacts; se pueden borrar al terminar. Los navegadores/perfiles de pruebas ampliadas se descargan aparte solo si se necesitan. Las pruebas históricas conservan evidencia resumida en los Markdown; las capturas originales seleccionadas están en store/screenshots. Los archivos de diagnóstico grandes se retiraron deliberadamente.

Para regenerar iconos/imágenes, instalar Pillow 12.2.0 como herramienta de desarrollo y ejecutar `python scripts/prepare_assets.py`. No es una dependencia de la extensión. Los iconos PNG preparados ya están versionados; la construcción normal no necesita Pillow.

### 4. Tiendas, cuando el mantenedor lo decida

Antes de enviar: confirmar nombre disponible e identificador Firefox definitivo; mantenerlo estable, revisar versión, ficha, permisos, privacidad y requisitos vigentes. El identificador actual magic-mark@magic-mark.local es provisional. No se anuncia disponibilidad en tiendas hasta tener una ficha aprobada.

Firefox: crear o usar una cuenta Mozilla/AMO, aceptar personalmente los acuerdos, seleccionar distribución listada, subir ZIP de Firefox, completar licencia MIT, privacidad, soporte, descripciones ES/EN y capturas. Añadir notas de store/reviewer-notes.md. Esperar firma y revisión; una carga temporal no es una instalación de producción.

Después, si se autoriza Chromium: preparar cuenta de desarrollador de Chrome Web Store, aceptar sus acuerdos y cualquier coste personalmente; subir ZIP Chromium, completar ficha/privacidad y esperar revisión. Edge Add-ons es otra publicación independiente. No se debe entregar al agente contraseñas, tarjetas o códigos de verificación.

### Fuentes oficiales

https://extensionworkshop.com/documentation/publish/submitting-an-add-on/
https://developer.chrome.com/docs/webstore/publish
https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository

## English

### Status

Code and ES/EN materials prepared. Copy and images approved by the maintainer on November 13, 2026, with future changes possible. Source published and first CI run passed. Repository: https://github.com/phyrateborquez/magic-mark. Public maintainer: phyrateborquez; contact through Issues, without publishing personal email. Store submission is deferred by the maintainer and must not begin yet.

The maintainer is the person/account administering the project, receiving reports and releasing versions. Use the public owning GitHub username; a legal name or personal email need not be published. Never put passwords or tokens in files or conversations.

### 1. GitHub access and repository

If CLI access has expired, run `gh auth login -h github.com`, choose GitHub.com, HTTPS and “Login with a web browser”, and complete official authentication. Do not publish codes. Check `gh auth status`.

Create public `magic-mark` under the chosen account, push only the source tree and check CI. Exclude node_modules, artifacts, dist, caches, profiles and browsers. `.gitignore` prevents tracking but does not itself free local disk space. Suggested bilingual repository description is given above.

### 2. Support and security

Use Issues for ordinary reports without private data. Enable Private Vulnerability Reporting under Settings → Advanced Security; verify Security → Advisories → Report a vulnerability and notifications. Only advertise private reporting once verified. Add real URLs to SUPPORT.md, SECURITY.md and store/metadata.json. A public personal email is unnecessary.

### 3. Rebuild and test

Requires Node.js 24 LTS and Python 3.10+. Run `npm ci --ignore-scripts` and `npm run verify`. Generated dist and artifacts ZIPs may be deleted afterward. Extended-test browsers/profiles are downloaded separately only when needed. Historical test summaries remain in Markdown; selected original screenshots remain in store/screenshots. Large diagnostic files were deliberately removed.

To regenerate icons/images, install development-only Pillow 12.2.0 and run `python scripts/prepare_assets.py`. Pillow is not an extension dependency; prepared icons are committed and normal builds do not need it.

### 4. Stores, when the maintainer decides

Before submission, check name availability, final stable Firefox ID, version, listing, permissions, privacy and current policies. magic-mark@magic-mark.local is provisional. Do not claim store availability before approval.

Firefox: use a Mozilla/AMO account, personally accept agreements, select listed distribution, upload Firefox ZIP, add MIT license, privacy/support, ES/EN copy and images. Include store/reviewer-notes.md instructions. Await signing and review; temporary installation is not production distribution.

Later, if Chromium submission is authorized: prepare a Chrome Web Store developer account, personally accept agreements and fees, upload the Chromium ZIP, complete listing/privacy and await review. Edge Add-ons is a separate submission. Do not give the agent passwords, payment details or verification codes. Official sources are listed above.
