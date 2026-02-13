<div align="center">

# 📋 Análisis de deuda técnica y refactorización

### Quiz App · CSDT 2026

*Olores de código, malas prácticas y plan de refactorización*

---

</div>

> Este documento resume los **olores de código** y **malas prácticas** detectados en el repositorio, así como **técnicas de refactorización** y **candidatos** concretos para aplicar.

---

## 👥 Equipo

| | |
| :--- | :--- |
| **Nombre del equipo** | Anti-Spaghetti-Squad |
| **Integrantes** | Jairo Andrés Jimenez<br>Edgar Ricardo Alvarez<br>Juliana Briceño Castro |

---

## 📑 Índice

1. [Olores de código y malas prácticas](#-1-olores-de-código-y-malas-prácticas)
2. [Técnicas de refactorización y candidatos](#-2-técnicas-de-refactorización-y-candidatos)
3. [Priorización sugerida](#-3-priorización-sugerida)

---

---

## 🔍 1. Olores de código y malas prácticas

### 1.1 ⚙️ Configuración y seguridad

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `config.py` | **SECRET_KEY volátil** | `SECRET_KEY = os.urandom(12)` genera una nueva clave en cada reinicio. Las sesiones se invalidan y no es adecuado en producción. |
| `config.py` | **Clave débil** | 12 bytes (96 bits) es insuficiente para secretos modernos; se recomienda 32+ bytes y que provenga de variables de entorno. |
| `server.py` | **Deprecación** | `@app.before_first_request` está deprecado desde Flask 2.3; puede dejar de funcionar en versiones futuras. |

---

### 1.2 🏗️ Estructura y responsabilidades

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `app/db.py` | **Acoplamiento a implementación** | Expone `db` y `quiz` como globales. Cualquier módulo que importe `app.db` depende de que `mongo_utils` esté ya inicializado (orden de importación frágil). |
| `app/modules/utils.py` | **Módulo con responsabilidades mezcladas** | Mezcla utilidades (JSON, contraseñas, códigos) con re-export de `Mongo_Utils` (que vive en `mongo.py`). Dificulta entender dónde está definida cada responsabilidad. |
| `app/auth/forms.py` | **Formularios acoplados a la base de datos** | `ProfileForm` hace `db.users.find_one(...)` dentro de validadores. Los formularios no deberían conocer el acceso a datos. |
| `app/dashboard/forms.py` | **Repetición de lógica de acceso a datos** | `ChangePwForm.validate_old_password` y otros usan `db` y `session` directamente. |

---

### 1.3 📝 Consistencia y nomenclatura

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `app/api/views.py`, `app/api/quiz.py` | **Respuestas API inconsistentes** | Se alterna `status='fail'` y `status='failed'` en respuestas JSON. Dificulta el manejo en el cliente y la documentación. |
| `app/api/quiz.py` | **Nombre de función** | `get_scorest` (typo: debería ser `get_scores`). |
| Varios | **Typos** | "Unkown" en lugar de "Unknown" (`quiz.py` líneas 50, 171, 195, 203). "unkown" en `api/views.py`. |
| `app/modules/mongo.py` | **Convención de nombres** | Clase `Mongo_Utils` con snake_case; en Python las clases suelen usar `PascalCase` (ej. `MongoUtils`). |

---

### 1.4 🧹 Código muerto e imports

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `app/auth/views.py` | **Import no usado** | `from sys import meta_path` no se utiliza. |
| `app/modules/utils.py` | **Imports duplicados/innecesarios** | `ObjectId` importado dos veces (líneas 3 y 8); `bson` importado y no usado. |
| `app/api/quiz.py` | **Import no usado** | `from codecs import decode` no se usa. |
| `app/api/quiz.py` | **Print en lógica** | `print('new index created ..')` en ruta de búsqueda; debería usar el logger de la aplicación. |

---

### 1.5 🧠 Lógica de negocio y vistas

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `app/dashboard/views.py` | **Rutas duplicadas** | `/scores` y `/users-scores` hacen lo mismo: `render_template('dashboard/users-scores.html')`. |
| `app/dashboard/views.py` | **Variable confusa** | En `edit_quiz`, el bucle usa `for data in range(len(check['data']))` y luego `check['data'][data]`; el nombre `data` como índice es engañoso (p. ej. `idx` o `i` sería más claro). |
| `app/dashboard/views.py` | **Lógica de autor repetida** | `author = {'$exists':True} if session.get('type') == 1 else session.get('username')` y comprobaciones similares se repiten en varios sitios (dashboard, api/quiz). |
| `app/api/views.py` | **Exposición de excepciones** | `return jsonify(status='fail', errors='<p>{}'.format(e))` devuelve el mensaje de excepción al cliente; riesgo de información sensible y poca utilidad para el usuario. |
| `app/api/views.py` | **Validación incompleta en edición de perfil** | `edit_profile` no valida formato de email ni longitud de `full_name`/`username`; la validación está en el formulario pero no se reutiliza de forma centralizada. |
| `app/api/quiz.py` | **Uso de `.values()` con `zip`** | En `nilai`, `list_answer = json_request.values()`; en Python 3 el orden es de inserción, pero la intención sería más clara alineando explícitamente por clave (p. ej. por `list_id`). |

---

### 1.6 💾 Persistencia y recursos

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `app/api/quiz.py` (upload CSV/JSON) | **Archivos en memoria** | `files.stream.read().decode('utf-8')` carga todo el archivo en memoria; archivos grandes pueden causar problemas de rendimiento o memoria. |
| `app/modules/mongo.py` | **Conexión por llamada** | `get_db()` crea `MongoClient(self.mongodb_uri)` en cada invocación; no se reutiliza conexión (aunque PyMongo suele agrupar por URI, el patrón no es explícito). |

---

### 1.7 🖥️ Frontend (JavaScript)

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `app/static/js/dashboard.js` (~línea 77) | **Operador incorrecto** | `path_name.length == 3 & path_name[1] == 'edit-quiz'` usa `&` (bitwise) en lugar de `&&` (lógico). |
| `app/static/js/dashboard.js` (~líneas 83–88) | **Uso incorrecto de jQuery** | `$.post({ url: ..., data: ... })` no es la firma de `$.post` (que es `url, data, callback`). Debería usarse `$.ajax({ method: 'POST', ... })`. |
| `app/static/js/script.js` | **Manejo de errores AJAX** | Las llamadas no tienen `.fail()`; si la petición falla por red, el usuario no recibe feedback. |
| `app/static/js/dashboard.js` | **Variable global** | Uso de `csrf_token` en `uploadfile()` sin definición visible en el fragmento; depende de que esté definido en el HTML/template. |

---

### 1.8 📌 Otros

| Ubicación | Problema | Descripción |
| :-------- | :------- | :---------- |
| `app/dashboard/views.py` (export-quiz) | **Content-Type y formato** | `mimetype='application/csv'` pero el cuerpo es `json_decoder(check_exists)` (objeto/dict), no CSV; el nombre del archivo en header usa `attachment:` en lugar de `attachment; filename=`. |
| `app/auth/forms.py` | **PasswordForm sin FlaskForm** | `PasswordForm` y `ProfileForm` son clases “mixins” sin heredar de `FlaskForm`; funcionan al combinarse con `FlaskForm`, pero la estructura es poco estándar y puede dar problemas con validadores o CSRF. |

---

## 🔧 2. Técnicas de refactorización y candidatos

### 2.1 Extraer constantes y normalizar respuestas API

| | |
| :--- | :--- |
| **Técnica** | *Introduce Constant* / *Replace Magic String with Constant* |
| **Candidatos** | Todas las cadenas `'fail'`, `'failed'`, `'success'` en `jsonify(...)`. |
| **Acción** | Definir constantes (p. ej. en `app/api/constants.py` o en un módulo compartido) como `API_STATUS_SUCCESS`, `API_STATUS_FAIL`, y usarlas en todas las rutas de la API. Unificar en una sola forma (por ejemplo siempre `fail` o siempre `failed`) y documentarla. |

---

### 2.2 Servicio de usuario / capa de acceso a datos

| | |
| :--- | :--- |
| **Técnica** | *Extract Class* / *Introduce Service Layer* |
| **Candidatos** | Toda lógica que hace `db.users.find_one`, `db.users.insert_one`, `db.users.update_one`, etc. repartida en `api/views.py`, `api/quiz.py`, `auth/forms.py`, `dashboard/forms.py`. |
| **Acción** | Crear un módulo (p. ej. `app/services/user_service.py`) con funciones como `get_user_by_username`, `create_user`, `update_user`, `get_user_for_session`. Los formularios y las vistas llamarían a este servicio en lugar de tocar `db` directamente. Reduce acoplamiento y facilita tests y cambios de almacenamiento. |

---

### 2.3 Servicio de quiz y puntuaciones

| | |
| :--- | :--- |
| **Técnica** | *Extract Class* / *Introduce Service Layer* |
| **Candidatos** | Lógica en `app/api/quiz.py` y `app/dashboard/views.py` que usa `quiz.find_one`, `quiz.insert_one`, `quiz.update_one`, `db.score.insert_one`, etc. |
| **Acción** | Extraer a `app/services/quiz_service.py` y `app/services/score_service.py` (o un único `QuizService` con métodos para quizzes y scores). Las rutas solo orquestan request/response y llaman al servicio. |

---

### 2.4 Helpers de autorización

| | |
| :--- | :--- |
| **Técnica** | *Extract Method* / *Introduce Parameter Object* |
| **Candidatos** | Expresiones repetidas como `author = {'$exists':True} if session.get('type') == 1 else session.get('username')` y comprobaciones “es autor o admin”. |
| **Acción** | Crear en `app/modules/decorators.py` o en un `app/modules/auth_utils.py` funciones como `current_user_is_admin(session)`, `get_quiz_author_filter(session)`, `can_edit_quiz(quiz_doc, session)`. Reutilizarlas en vistas y en la API. |

---

### 2.5 Seed y arranque (reemplazo de `before_first_request`)

| | |
| :--- | :--- |
| **Técnica** | *Replace Deprecated API* + *Extract Method* |
| **Candidatos** | `server.py`, función `seed_data()`. |
| **Acción** | • Mover la lógica de seed a un módulo (p. ej. `app/cli.py` o `app/scripts/seed.py`) y ejecutarla con un comando Flask CLI (`flask seed-admin`) o en un script de despliegue.<br>• O usar el evento correcto según la versión de Flask (p. ej. ejecutar el seed una vez al arranque en un hook que no esté deprecado).<br>Así se evita `before_first_request` y se hace el seed más explícito y testeable. |

---

### 2.6 Configuración de seguridad

| | |
| :--- | :--- |
| **Técnica** | *Replace Magic Value* + configuración por entorno |
| **Candidatos** | `config.py` (SECRET_KEY y tamaño). |
| **Acción** | • Leer `SECRET_KEY` desde variable de entorno (ej. `os.environ.get('SECRET_KEY')`) y, en desarrollo, usar un valor por defecto fijo solo si no hay variable.<br>• No generar `os.urandom(12)` en cada arranque en producción.<br>• Documentar en README o en este documento la necesidad de definir `SECRET_KEY` en producción. |

---

### 2.7 Formularios y validación

| | |
| :--- | :--- |
| **Técnica** | *Move Method* + *Introduce Service* |
| **Candidatos** | Validadores en `ProfileForm` y `ChangePwForm` que usan `db` y `session`. |
| **Acción** | • Mover la comprobación “username/email ya existe” al servicio de usuario.<br>• En el validador del formulario, llamar al servicio (inyectado o importado desde un módulo de servicios), en lugar de importar `db` en el formulario.<br>• Mantener en el formulario solo la validación de formato (longitud, regex, etc.) cuando sea posible. |

---

### 2.8 Módulo de utilidades

| | |
| :--- | :--- |
| **Técnica** | *Split Module* |
| **Candidatos** | `app/modules/utils.py` (mezcla de JSON, contraseñas, códigos y re-export de Mongo_Utils). |
| **Acción** | • Dejar en `utils.py` solo funciones genéricas (p. ej. `json_decoder`, `generate_code`).<br>• Mover `generate_password` y `check_password` a un módulo como `app/modules/security.py` o `app/services/auth_utils.py`.<br>• Importar `Mongo_Utils` desde `app.modules.mongo` en `app/__init__.py` en lugar de desde `utils`. |

---

### 2.9 Rutas y vistas duplicadas

| | |
| :--- | :--- |
| **Técnica** | *Collapse Hierarchy* / *Redirect* |
| **Candidatos** | Rutas `/scores` y `/users-scores` que renderizan el mismo template. |
| **Acción** | Mantener una sola ruta (p. ej. `/scores`) y hacer que la otra redirija a ella, o una única ruta que elija el template o los datos según rol/query. Así se evita duplicación y comportamiento divergente en el futuro. |

---

### 2.10 Manejo de errores en API

| | |
| :--- | :--- |
| **Técnica** | *Introduce Exception Handler* / *Centralize Error Responses* |
| **Candidatos** | Respuestas `jsonify(status='fail', ...)` repetidas y el caso donde se expone `str(e)` al cliente. |
| **Acción** | • Definir un formato estándar de error (ej. `{ "status": "fail", "message": "...", "code": "optional" }`).<br>• Crear un manejador de excepciones (decorador o `@api.errorhandler`) que capture excepciones no controladas y devuelva un mensaje genérico sin detalles internos.<br>• En los `except` actuales, registrar `e` en el logger y devolver un mensaje genérico al cliente. |

---

### 2.11 Frontend: AJAX y jQuery

| | |
| :--- | :--- |
| **Técnica** | *Correct API usage* + *Add error handling* |
| **Candidatos** | Uso de `$.post` en `dashboard.js` y falta de `.fail()` en `script.js`. |
| **Acción** | • Sustituir `$.post({...})` por `$.ajax({ url: endpoint, method: 'POST', data: ..., contentType: ... }).done(...).fail(...)`.<br>• Añadir `.fail()` (o `.catch()` si se usa promesas) en las llamadas de login/registro y otras críticas, mostrando un mensaje al usuario.<br>• Corregir la condición con `&` por `&&` en la comprobación de `path_name` y `edit-quiz`. |

---

### 2.12 Nombres y typos

| | |
| :--- | :--- |
| **Técnica** | *Rename Method* / *Rename Variable* |
| **Candidatos** | `get_scorest` → `get_scores`; "Unkown" / "unkown" → "Unknown"; variable `data` usada como índice en `edit_quiz` → `idx` o `i`. |
| **Acción** | Búsqueda y reemplazo controlado (y tests o revisión manual de referencias) para no romper rutas o clientes que dependan de nombres de endpoints (si `get_scorest` está en la URL, habría que mantener la ruta y solo renombrar la función internamente). |

---

## 📊 3. Priorización sugerida

| Prioridad | Tema | Impacto | Esfuerzo |
| :-------: | :--- | :------ | :------: |
| **Alta** | Unificar respuestas API y no exponer excepciones | Seguridad y consistencia | Bajo |
| **Alta** | SECRET_KEY desde entorno y reemplazo de `before_first_request` | Seguridad y compatibilidad | Bajo |
| **Alta** | Corregir `$.post` y `&` en dashboard.js | Bugs en producción | Bajo |
| **Media** | Servicio de usuario y desacoplar formularios de `db` | Mantenibilidad y tests | Medio |
| **Media** | Servicio de quiz/scores y helpers de autorización | Mantenibilidad | Medio |
| **Media** | Extraer constantes y manejo centralizado de errores API | Consistencia | Bajo–medio |
| **Baja** | Limpieza de imports y typos | Claridad | Bajo |
| **Baja** | Refactor de `utils.py` y nombre `Mongo_Utils` | Claridad y convenciones | Bajo |

---

<div align="center">

*Este documento puede actualizarse conforme se apliquen refactorizaciones o se detecten nuevos puntos de deuda técnica.*

</div>
