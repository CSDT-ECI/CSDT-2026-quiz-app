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
4. [Clean Code & XP Practices](#-4-clean-code--xp-practices)

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

## 🧼 4. Clean Code & XP Practices

### 4.1 Prácticas de Clean Code — Evaluación

#### 4.1.1 ✅ Prácticas que SÍ se cumplen

| Práctica | Argumentación |
| :------- | :------------ |
| **Estructura modular con Blueprints** | La aplicación separa sus responsabilidades en Blueprints de Flask (`auth`, `api`, `dashboard`, `main`, `quiz`), lo que refleja el principio de **modularización** de Clean Code. Cada Blueprint agrupa rutas relacionadas temáticamente, facilitando la navegación del código. |
| **Uso de decoradores para cross-cutting concerns** | `login_required` y `admin_required` en `app/modules/decorators.py` encapsulan la lógica de autorización en un solo lugar reutilizable, siguiendo el principio **DRY** (Don't Repeat Yourself) y **Separation of Concerns**. Las vistas no repiten la verificación de sesión manualmente. |
| **Formularios con validación declarativa (WTForms)** | `app/auth/forms.py` y `app/dashboard/forms.py` usan `DataRequired`, `Length`, `Regexp` y validadores personalizados para definir las reglas de entrada de forma declarativa. Esto sigue el principio de **código auto-descriptivo**: las restricciones se leen directamente en la clase del formulario. |
| **Funciones utilitarias pequeñas** | Funciones como `generate_password()`, `check_password()`, `generate_code()` y `json_decoder()` en `app/modules/utils.py` son breves (menos de 10 líneas cada una) y hacen **una sola cosa**, alineándose con la regla de Clean Code de que las funciones deben ser pequeñas y tener un único propósito. |
| **Configuración centralizada** | `config.py` centraliza las variables de configuración (`SECRET_KEY`, `MONGO_URI`, nombres de BD) en clases jerárquicas (`Config`, `DevelopmentConfig`, `TestingConfig`), evitando que estos valores se dispersen por el código. Esto facilita cambiar el entorno sin modificar lógica de negocio. |
| **Protección CSRF integrada** | La aplicación usa `CSRFProtect` de Flask-WTF de forma global en `app/__init__.py`, lo que demuestra una preocupación por seguridad desde el diseño. El token CSRF se incluye en los templates vía `extra/csrf.html`. |
| **Separación de templates con includes** | Los templates HTML se organizan con archivos parciales (`includes/head.html`, `includes/sidebar.html`, `includes/script.html`, `extra/navbar.html`), aplicando el principio DRY en la capa de presentación y facilitando el mantenimiento del frontend. |

---

#### 4.1.2 ❌ Prácticas que NO se cumplen — Recomendaciones

| Práctica incumplida | Problema detectado | Recomendación |
| :------------------- | :----------------- | :------------ |
| **Nombres significativos y consistentes** | La función `nilai()` en `app/api/quiz.py` es una palabra en indonesio que no comunica su intención a un equipo hispanohablante/angloparlante. `get_scorest()` tiene un typo. `Mongo_Utils` usa snake_case en lugar de PascalCase. La variable `data` se usa como índice en `dashboard/views.py`. | Renombrar: `nilai()` → `submit_quiz_answers()`, `get_scorest()` → `get_scores()`, `Mongo_Utils` → `MongoUtils`. Usar nombres como `idx` o `i` para índices numéricos. **"Si tienes que adivinar qué hace una función por su nombre, el nombre está mal"** — Robert C. Martin. |
| **Funciones pequeñas con un solo nivel de abstracción** | `nilai()` en `app/api/quiz.py` mezcla parsing de JSON, cálculo de puntaje, generación de código, inserción en BD y respuesta HTTP — todo en una sola función de más de 40 líneas con múltiples niveles de indentación. | Extraer en funciones: `parse_answers(request)`, `calculate_score(answers, correct_answers)`, `save_score(score_data)`. Cada función debería operar en **un solo nivel de abstracción** (Regla del Paso Descendente). |
| **No exponer detalles internos al usuario** | En `app/api/views.py`, el bloque `except` devuelve `str(e)` al cliente en respuestas JSON, exponiendo trazas de error internas. | Registrar la excepción con `app.logger.error(e)` y devolver un mensaje genérico: `jsonify(status='fail', message='Error interno del servidor')`. Los detalles de implementación nunca deben cruzar la frontera de la API. |
| **Eliminar código muerto** | Imports no usados: `from sys import meta_path` (auth/views.py), `from codecs import decode` (api/quiz.py), `ObjectId` importado dos veces (utils.py). `print('new index created ..')` actúa como depuración olvidada. | Eliminar todos los imports muertos. Reemplazar `print()` por `app.logger.info()`. El código muerto genera **ruido** que dificulta la lectura y puede confundir al lector sobre dependencias reales. |
| **Manejo de errores consistente** | Las respuestas de error alternan entre `status='fail'` y `status='failed'`. Algunas rutas retornan `abort(403)`, otras `return 'no'`, otras `jsonify(status='fail')`. | Definir un contrato de respuesta estándar (ej. `{"status": "fail", "message": "..."}`) y un helper `api_error(message, code=400)`. **El manejo de errores es una responsabilidad**, no algo que se agrega ad-hoc. |
| **No usar números/cadenas mágicas** | `type == 1` para verificar administradores (repetido en múltiples archivos). `100` como puntaje perfecto. `14` como longitud de código. Cadenas como `'quiz_code'`, `'score'`, `'done_by'` repetidas por todo el código. | Extraer constantes: `USER_TYPE_ADMIN = 1`, `PERFECT_SCORE = 100`, `QUIZ_CODE_LENGTH = 14`. Colocarlas en `app/constants.py`. **Los números mágicos oscurecen la intención del programador.** |
| **Principio de mínimo asombro (Least Surprise)** | `export_quiz()` en `dashboard/views.py` declara `mimetype='application/csv'` pero devuelve contenido JSON. La ruta se llama "export" pero el Content-Disposition usa `attachment:` (sintaxis incorrecta; debería ser `attachment; filename=`). | Corregir el mimetype a `application/json` o convertir realmente a CSV. Usar la sintaxis correcta de Content-Disposition. **El código no debe sorprender a quien lo lee ni a quien lo consume.** |
| **Tests unitarios y de integración** | No existe ningún archivo de test en el repositorio. Ninguna función tiene tests automatizados. | Crear un directorio `tests/` con al menos: `test_utils.py` (funciones puras), `test_auth.py` (flujos de login/registro), `test_api.py` (endpoints). **"Código sin tests es código roto por diseño"** — Michael Feathers. |

---

### 4.2 Principios de programación — Incumplimientos documentados

#### 4.2.1 SOLID

| Principio | Estado | Evidencia |
| :-------- | :----: | :-------- |
| **S — Single Responsibility** | ❌ | `app/api/views.py` contiene funciones que validan entrada, ejecutan lógica de negocio, acceden a la BD y formatean respuestas HTTP, todo en el mismo método. `app/auth/forms.py` mezcla validación de formato con consultas a la base de datos (`db.users.find_one` dentro de validadores de formulario). `app/modules/utils.py` agrupa utilidades de JSON, hashing de contraseñas, generación de códigos aleatorios y re-exporta `Mongo_Utils`. |
| **O — Open/Closed** | ❌ | Para agregar un nuevo tipo de archivo de importación (ej. XML), habría que modificar directamente la función `upload()` en `api/views.py`, ya que no hay abstracción para parsers de archivos. No existe un mecanismo de extensión sin modificación. |
| **L — Liskov Substitution** | ⚠️ | `PasswordForm` y `ProfileForm` en `auth/forms.py` no heredan de `FlaskForm` sino que actúan como mixins; al combinarse con `FlaskForm` en `RegisterForm` funcionan, pero no son sustituibles de forma independiente — no se pueden usar como formularios por sí mismos. |
| **I — Interface Segregation** | ❌ | No se definen interfaces ni clases abstractas. `Mongo_Utils` expone `get_db()` que retorna una tupla `(db, collection)`, forzando a todos los consumidores a depender de la estructura completa de MongoDB incluso si solo necesitan una operación específica. |
| **D — Dependency Inversion** | ❌ | Los módulos de alto nivel (`api/views.py`, `dashboard/views.py`, `auth/forms.py`) importan directamente `from app.db import db, quiz`. No hay abstracción intermedia (repositorio, servicio). Si se cambiara MongoDB por PostgreSQL, habría que modificar **cada archivo** que usa `db`. |

---

#### 4.2.2 Otros principios

| Principio | Estado | Evidencia |
| :-------- | :----: | :-------- |
| **DRY** (Don't Repeat Yourself) | ❌ | La expresión `author = {'$exists':True} if session.get('type') == 1 else session.get('username')` se repite en `dashboard/views.py` y `api/quiz.py`. Las rutas `/scores` y `/users-scores` renderizan el mismo template. Patrones AJAX casi idénticos se repiten en `script.js` y `dashboard.js`. |
| **KISS** (Keep It Simple, Stupid) | ❌ | `json_decoder()` en `utils.py` convierte un objeto a JSON string y luego lo parsea de vuelta a dict — una conversión circular innecesaria cuando podría usarse directamente la serialización de BSON. La función `download_quiz()` usa un pipeline de agregación complejo para lo que podría ser un `find_one()`. |
| **YAGNI** (You Aren't Gonna Need It) | ⚠️ | `TestingConfig` y `ProductionConfig` existen en `config.py` pero no hay tests ni pipeline de CI/CD que los utilice, representando configuración prematura. Sin embargo, tenerlos no genera daño activo. |
| **Fail Fast** | ❌ | `app/db.py` ejecuta `mongo_utils.get_db()` a nivel de módulo sin capturar excepciones; si MongoDB no está disponible, la app falla con un error críptico de conexión en lugar de un mensaje claro al arranque. Las funciones de API no validan la existencia de campos requeridos al inicio — procesan datos parciales y fallan en puntos intermedios. |
| **Least Astonishment** | ❌ | `export_quiz()` dice CSV pero devuelve JSON. `nilai()` es un nombre en idioma diferente al resto del código. `&` (bitwise) en lugar de `&&` (lógico) en `dashboard.js` produce comportamiento inesperado en ciertos casos. |
| **Separation of Concerns** | ❌ | No existe capa de servicios ni repositorios. Las vistas de Flask actúan simultáneamente como controladores, servicios y repositorios. Los formularios WTForms acceden directamente a la base de datos. El frontend mezcla lógica de UI, llamadas a API y manipulación del DOM sin separación. |

---

### 4.3 Prácticas XP aplicables para mejorar el código

#### 4.3.1 Prácticas recomendadas

| Práctica XP | Aplicabilidad al proyecto | Acciones concretas |
| :---------- | :------------------------ | :----------------- |
| **Test-Driven Development (TDD)** | **Alta**. El proyecto tiene **cero tests**. No hay forma de verificar que una refactorización no rompe funcionalidad existente. Sin tests, cada cambio es un riesgo. | 1. Crear `tests/` con `conftest.py` para fixtures de Flask y MongoDB mock.<br>2. Escribir tests para las funciones puras primero (`generate_password`, `check_password`, `generate_code`, `json_decoder`).<br>3. Agregar tests de integración para los endpoints de API (`/api/login`, `/api/register`, `/api/quiz`).<br>4. Adoptar el ciclo **Red → Green → Refactor** para toda nueva funcionalidad. |
| **Refactoring continuo** | **Alta**. El documento actual (secciones 1 y 2) ya identifica deuda técnica significativa. Sin embargo, no hay evidencia de que se aplique refactoring de forma sistemática. | 1. Priorizar los refactorings de la sección 3 (priorización sugerida).<br>2. Aplicar la **Regla del Boy Scout**: "Deja el código más limpio de lo que lo encontraste" en cada commit.<br>3. Usar los tests (una vez creados) como red de seguridad antes de cada refactoring.<br>4. Hacer refactorings pequeños y frecuentes, no grandes reescrituras. |
| **Pair Programming** | **Media-Alta**. El equipo tiene 3 integrantes. Archivos críticos como `app/api/views.py` (165+ líneas con múltiples vulnerabilidades de seguridad) se beneficiarían enormemente de revisión en tiempo real. | 1. Programar en pares para los módulos de seguridad (`decorators.py`, endpoints de autenticación).<br>2. Rotar los pares para que todos conozcan todas las partes del sistema.<br>3. Usar pair programming especialmente al implementar los refactorings de la sección 2 (servicio de usuario, servicio de quiz). |
| **Integración Continua (CI)** | **Alta**. No existe pipeline de CI/CD. Los cambios se hacen directamente en `main` sin verificación automatizada. | 1. Configurar GitHub Actions con un workflow básico: `pip install` → `pytest` → `flake8`.<br>2. Bloquear merges a `main` sin que pasen los checks.<br>3. Agregar un linter (flake8 o ruff) para detectar imports muertos, typos y problemas de estilo automáticamente. |
| **Diseño Simple (Simple Design)** | **Alta**. Hay sobre-ingeniería en algunos puntos (`json_decoder` hace conversiones innecesarias, `download_quiz` usa agregaciones complejas) y sub-ingeniería en otros (sin capas de servicio, sin manejo de errores). | Aplicar las 4 reglas del Diseño Simple de Kent Beck:<br>1. **Pasa todos los tests** → primero crear tests.<br>2. **Revela intención** → renombrar funciones y variables (`nilai` → `submit_quiz_answers`).<br>3. **No tiene duplicación** → extraer helpers de autorización y constantes.<br>4. **Tiene el mínimo de elementos** → eliminar código muerto e imports no usados. |
| **Estándares de codificación (Coding Standards)** | **Alta**. El código mezcla convenciones: `Mongo_Utils` (snake_case para clase), `nilai` (indonesio), `getQuestion` (camelCase), `get_scorest` (typo). No hay linter configurado. | 1. Adoptar PEP 8 como estándar para Python y configurar `ruff` o `flake8` en el proyecto.<br>2. Definir convenciones de nombrado del equipo en un `CONTRIBUTING.md` o en este documento.<br>3. Configurar un pre-commit hook que ejecute el linter antes de cada commit.<br>4. Usar ESLint para el JavaScript del frontend. |
| **Propiedad Colectiva del Código** | **Media**. Con 3 integrantes, es importante que todos puedan modificar cualquier parte del sistema sin "dueños" de archivos. | 1. Rotar la responsabilidad de revisión de PRs.<br>2. Documentar las decisiones de arquitectura en este documento.<br>3. Asegurar que ningún módulo dependa del conocimiento de una sola persona (el pair programming ayuda con esto). |
| **Metáfora del Sistema** | **Media**. No hay documentación que explique la arquitectura general ni el flujo de datos del sistema. Un nuevo integrante tendría que leer todo el código para entender cómo funciona. | 1. Agregar un diagrama de arquitectura (Blueprints, flujo request→response, capas).<br>2. Documentar el modelo de datos (colecciones de MongoDB, campos esperados).<br>3. La metáfora podría ser: *"Un sistema de exámenes donde los profesores crean quizzes y los estudiantes los responden, con un panel de administración para gestión"*. |
| **Releases pequeños y frecuentes** | **Media**. El historial de commits muestra features completas en commits únicos. No hay evidencia de releases incrementales ni versionado. | 1. Adoptar versionado semántico (SemVer).<br>2. Hacer commits más granulares (un commit por cambio lógico, no por feature completa).<br>3. Usar feature branches y PRs para cada cambio, facilitando revisión y rollback. |

---

#### 4.3.2 Priorización de prácticas XP

| Prioridad | Práctica | Justificación |
| :-------: | :------- | :------------ |
| 🔴 **1** | **TDD / Crear tests** | Sin tests no se puede refactorizar con seguridad. Es el habilitador de todas las demás mejoras. |
| 🔴 **2** | **Integración Continua** | Automatiza la verificación y previene regresiones. Complementa directamente a TDD. |
| 🟡 **3** | **Estándares de codificación + Linter** | Elimina discusiones de estilo, detecta código muerto automáticamente y mejora la consistencia. Esfuerzo bajo, impacto alto. |
| 🟡 **4** | **Refactoring continuo** | Con tests y CI como base, se puede atacar la deuda técnica de forma segura y sistemática. |
| 🟢 **5** | **Pair Programming** | Mejora calidad del código en tiempo real, especialmente para los módulos de seguridad y la capa de servicios. |
| 🟢 **6** | **Diseño Simple + Releases pequeños** | Guía las decisiones de diseño durante el refactoring y mejora el flujo de trabajo del equipo. |

---

## 🧪 5. Deuda Técnica en Pruebas

### 5.1 Estado inicial del testing

Al inicio del análisis, el proyecto contaba con **8 tests** exclusivamente de tipo *smoke test* que verificaban códigos HTTP (200/302) sin validar lógica de negocio, datos de respuesta ni flujos completos.

| Métrica | Valor inicial |
| :------ | :-----------: |
| Tests totales | 8 |
| Cobertura de líneas | **5.8%** (29/499) |
| Cobertura de branches | **0%** (0/98) |
| Tests de lógica de negocio | 0 |
| Tests de funciones puras | 0 |
| Tests de seguridad/decorators | 0 |

---

### 5.2 Prácticas de Testing Debt identificadas

#### 5.2.1 Prácticas identificadas en la primera intervención (entrega anterior)

| # | Práctica de Testing Debt | Evidencia en el proyecto | Impacto |
| :-: | :---------------------- | :----------------------- | :------ |
| 1 | **Ausencia total de tests unitarios para lógica de negocio** | Funciones críticas como `nilai()` (cálculo de puntaje), `add_account()` (registro), `api_login()` (autenticación) no tenían ningún test. | Cualquier cambio en estas funciones podría romper funcionalidad sin ser detectado. |
| 2 | **Tests superficiales (smoke tests only)** | Los 8 tests existentes solo verificaban `response.status_code == 200`. No validaban el contenido de las respuestas, datos JSON, ni efectos en la base de datos. | Falsa sensación de seguridad: los tests pasan pero no detectan bugs reales. |
| 3 | **Sin tests de funciones puras** | `generate_code()`, `generate_password()`, `check_password()`, `json_decoder()` — funciones deterministas y fácilmente testeables — no tenían tests. | Las funciones más fáciles de testear eran las más descuidadas. |
| 4 | **Sin tests de seguridad** | Decoradores `login_required` y `admin_required` no estaban testeados. No se verificaba que rutas protegidas rechazaran usuarios no autenticados. | Vulnerabilidades de acceso podrían pasar desapercibidas. |
| 5 | **Sin tests de edge cases** | No había tests para inputs inválidos, campos faltantes, archivos malformados, usuarios duplicados, contraseñas incorrectas, etc. | Los caminos de error nunca se verificaban. |
| 6 | **Cobertura de branches en 0%** | Ninguna rama condicional (`if/else`) estaba cubierta por tests. | Las decisiones lógicas del código nunca se ejecutaban en tests. |
| 7 | **Dependencia frágil del mock de MongoDB** | El `conftest.py` original parcheaba `os.environ` pero no la config de Flask, causando `RuntimeError: MONGODB_URI not found` en todos los tests que requerían la app. | Los tests existentes probablemente nunca se ejecutaron con éxito en CI. |

#### 5.2.2 Prácticas de testing debt identificadas en la segunda intervención

Tras la primera intervención se incrementó la cobertura a 70.54%. Sin embargo, el análisis de la suite resultante reveló nuevas prácticas de deuda de testing que persistían:

| # | Práctica de Testing Debt | Evidencia en el proyecto | Impacto |
| :-: | :---------------------- | :----------------------- | :------ |
| 8 | **Tests con estado compartido (contaminación entre tests)** | `test_add_account_success` en `test_api_views.py` usa el username `testuser`, el mismo que inserta el fixture `registered_user` (con `autouse=True`). Al ejecutar la suite completa, el test falla porque el usuario ya existe en la BD mock. En aislamiento sí pasa. | Tests que pasan individualmente pero fallan en la suite completa generan falsa confianza e impiden detectar regresiones reales. |
| 9 | **Cobertura nula del módulo `dashboard/views.py`** | `dashboard/views.py` tenía 46.94% de cobertura. Vistas críticas como `edit_quiz`, `delete_quiz`, `logout`, `download_quiz` no tenían ningún test. La lógica de autorización (¿puede el usuario editar este quiz?) nunca se verificaba. | Las vistas de dashboard son las más usadas por usuarios autenticados; un bug en autorización podría permitir que un usuario edite o elimine quizzes de otro. |
| 10 | **Flujos de carga de archivos sin cobertura** | El endpoint `uploadCsv` en `api/quiz.py` tenía 0% de cobertura (líneas 148–205). Los flujos de CSV válido, CSV inválido, JSON válido, JSON inválido y archivo de extensión incorrecta nunca se ejecutaban en tests. | Este endpoint acepta entrada de usuario no confiable; un error en validación podría insertar datos malformados o causar errores en producción. |
| 11 | **Rutas de administración sin cobertura de integración** | Las operaciones de admin (`manage_users`: delete, promote, unpromote) y las verificaciones de autorización de perfil (`edit_profile`, `change_password` con contraseña incorrecta) no tenían tests. | Operaciones destructivas (eliminar usuarios) sin tests de integración son un riesgo alto: un bug silencioso podría borrar usuarios legítimos. |
| 12 | **Branches de autorización en vistas sin cubrir** | En `dashboard/views.py`, las ramas `edit_quiz` (acceso de admin vs. propietario vs. usuario ajeno) y `delete_quiz` (misma lógica) no tenían ningún test de branch. La cobertura de branches del módulo era 0%. | Verificar solo el camino feliz de una vista deja los paths de rechazo sin validación; regresiones en autorización no se detectarían. |

---

### 5.3 Ejemplos concretos de testing debt

#### Ejemplo 1: Función `nilai()` sin tests — Cálculo de puntaje no verificado

```python
# app/api/quiz.py — línea 58
@api.route('/quiz/nilai/<code>', methods=['POST'])
def nilai(code):
    # ... 40 líneas de lógica que mezclan parsing, cálculo y persistencia
    perfect_value = 100
    per_true = perfect_value/len(data_check)
    fix_value = round(len(list_true) * per_true)
```

**Problema**: Esta función calcula el puntaje de un quiz. Un error en la lógica de comparación de respuestas o en el cálculo del porcentaje afectaría directamente la calificación de los usuarios, y no existía ningún test que verificara que `100` se retornara para respuestas correctas o `50` para mitad correctas.

#### Ejemplo 2: Decorator `login_required` sin verificación

```python
# app/modules/decorators.py
def login_required(f):
    @wraps(f)
    def function(*args, **kwargs):
        if not session.get('username'):
            flash('login first ')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return function
```

**Problema**: Si alguien modificara accidentalmente la clave de sesión (`'username'` → `'user'`), todas las rutas protegidas quedarían abiertas. Sin tests, este cambio pasaría inadvertido.

#### Ejemplo 3: Registro de usuarios — Sin validación de duplicados testeada

```python
# app/api/views.py — línea 19
@api.route('/add-account', methods=['POST'])
def add_account():
    # ... la validación de duplicados depende de ProfileForm.validate_username
    # que hace db.users.find_one({'username':username.data})
```

**Problema**: La validación de username duplicado depende de que `ProfileForm` consulte la BD dentro de un validador. Sin tests, no se verificaba que registrar el mismo username dos veces retornara un error.

#### Ejemplo 4 (segunda intervención): Contaminación entre tests — BD mock compartida

```python
# tests/conftest.py
@pytest.fixture(autouse=True)          # ← se ejecuta en TODOS los tests
def mock_mongodb():
    ...

@pytest.fixture
def registered_user(app, sample_user_data):
    # inserta {"username": "testuser", ...} en la BD mock
    db.users.insert_one(user)
    return sample_user_data

# tests/test_api_views.py
def test_add_account_success(client):
    # intenta registrar {"username": "testuser", ...} — ya existe!
    response = client.post("/api/add-account", data=json.dumps({
        "username": "testuser", ...
    }))
    assert data["status"] == "success"  # ← FALLA cuando se corre con la suite completa
```

**Problema**: `mock_mongodb` aplica `autouse=True` (se inyecta en todos los tests) pero no limpia la BD entre tests. Si cualquier test que use `registered_user` corre antes de `test_add_account_success`, la BD ya tiene `testuser` y el test falla. Este es el patrón clásico de **test order dependency**: los tests no son idempotentes ni aislados.

#### Ejemplo 5 (segunda intervención): Lógica de autorización de dashboard sin tests

```python
# app/dashboard/views.py — línea 76
@dashboard.route('/edit-quiz/<code>')
@login_required
def edit_quiz(code):
    check = json_decoder(quiz.find_one({'code': code}))
    if check and (session.get('username') == check['author'] or session.get('type') == 1):
        # ... renderizar formulario de edición
        return render_template('dashboard/add-quizes.html', forms=forms)
    abort(403)  # ← esta rama nunca se ejecutaba en tests
```

**Problema**: La rama `abort(403)` — que protege el quiz de ser editado por un usuario que no es el autor ni admin — nunca se cubría. Un usuario ajeno podría acceder al quiz si se introdujera un bug en la condición y no habría test que lo detectara.

---

### 5.4 Tests implementados para reducir la deuda

#### 5.4.1 Primera intervención — 37 tests nuevos

| Módulo | Tests | Qué cubren |
| :----- | :---: | :--------- |
| `tests/test_utils.py` | 14 | Funciones puras: `generate_code`, `generate_password`, `check_password`, `json_decoder` |
| `tests/test_decorators.py` | 4 | Decoradores de autenticación y autorización |
| `tests/test_api_views.py` | 9 | Endpoints de usuario: registro, login, perfil, contraseña |
| `tests/test_api_quiz.py` | 10 | Endpoints de quiz: creación, preguntas, puntaje, scores |

#### 5.4.2 Segunda intervención — 39 tests nuevos

Se crearon **3 nuevos módulos de test** para cubrir las áreas con mayor deuda remanente:

| Módulo | Tests | Qué cubren |
| :----- | :---: | :--------- |
| `tests/test_dashboard_views.py` | 18 | Vistas de dashboard: autenticación, edición/eliminación de quiz, autorización por rol, logout, rutas duplicadas |
| `tests/test_upload_csv.py` | 8 | Carga de archivos CSV y JSON: formato válido, campos faltantes, extensión incorrecta, sin archivo |
| `tests/test_api_admin.py` | 13 | Operaciones admin: delete/promote/unpromote, cambio de contraseña, edición de perfil, visualización de quiz, flujos de error |

**Áreas específicamente cubiertas por primera vez:**
- `edit_quiz` con usuario propietario ✅, usuario ajeno (403) ✅, admin ✅
- `delete_quiz` con código existente y no existente ✅
- `logout` con verificación de sesión borrada ✅
- `uploadCsv` con CSV válido, CSV inválido, JSON válido, JSON inválido ✅
- `manage_users` (delete, promote, unpromote) ✅
- `change_password` con contraseña correcta e incorrecta ✅
- `edit_profile` con email duplicado ✅
- `nilai` para quiz inexistente ✅

---

### 5.5 Resultados después de cada intervención

| Métrica | Inicial | 1ª intervención | 2ª intervención |
| :------ | :-----: | :-------------: | :-------------: |
| Tests totales | 8 | 45 | **84** |
| Cobertura de líneas | 5.8% | 70.54% | **90%** |
| Cobertura de branches | 0% | 29.59% | **~84%** |
| Archivos con 100% cobertura | 2 | 12 | **16** |
| `dashboard/views.py` cobertura | 0% | 46.94% | **85%** |
| `api/quiz.py` cobertura | 0% | 57.72% | **85%** |
| `api/views.py` cobertura | 0% | 63.83% | **90%** |

---

### 5.6 Deuda de testing remanente

| Área | Descripción | Prioridad |
| :--- | :---------- | :-------: |
| `test_add_account_success` — contaminación de BD | El fixture `registered_user` con `autouse=True` inserta `testuser` antes de que el test intente registrarlo. Solución: usar username único en el test o añadir limpieza de BD en `teardown`. | Alta |
| `dashboard/views.py` — `download_quiz` | El endpoint de descarga usa una agregación de MongoDB que mongomock no soporta completamente. Requiere mock adicional o refactoring del endpoint. | Media |
| `api/quiz.py` — búsqueda por texto | El endpoint `quiz_search` requiere índice de texto de MongoDB; mongomock tiene soporte limitado para `$text`. | Baja |
| Tests de integración E2E | Flujos completos: registro → login → crear quiz → responder → ver scores con verificación end-to-end | Alta |
| Tests de frontend (JS) | `dashboard.js` y `script.js` no tienen tests; el bug del operador `&` vs `&&` no está cubierto | Media |

---

<div align="center">

*Este documento puede actualizarse conforme se apliquen refactorizaciones o se detecten nuevos puntos de deuda técnica.*

</div>

---

## 📊 6. Developer Experience (DevEx) & Framework SPACE

### 6.1 Developer Experience (DevEx)

#### 6.1.1 Definición y contexto

**Developer Experience (DevEx)** es el conjunto de factores que determinan qué tan fluida, eficiente y satisfactoria es la experiencia de un desarrollador al trabajar con una codebase, herramientas y procesos de desarrollo. Fue formalizado por GitHub en 2023 como un marco para medir la efectividad del desarrollo de software.

El framework DevEx evalúa cuatro dimensiones:
- **Feedback Loops**: Velocidad y calidad de la retroalimentación (compilación, tests, errores)
- **Cognitive Load**: Cantidad de información que el desarrollador debe mantener en mente simultáneamente
- **Flow State**: Capacidad del entorno para facilitar la concentración sostenida
- **Tooling**: Calidad y ergonomía de las herramientas utilizadas

#### 6.1.2 Análisis DevEx del proyecto

##### ✅ Puntos Positivos

| Área | Evidencia | Impacto en DevEx |
| :--- | :-------- | :--------------- |
| **CI/CD con GitHub Actions** | Workflow configurado en `.github/workflows/build.yml` con pytest, coverage y SonarCloud | Feedback loop automatizado; el desarrollador sabe inmediatamente si su código rompe algo |
| **Testing infrastructure** | Suite de 84 tests con pytest, fixtures en `conftest.py`, mongomock para aislamiento | Reduce incertidumbre; permite modificar código con confianza |
| **Cobertura de código** | 90% de cobertura de líneas, configuración en `.coveragerc` y `coverage.xml` | Feedback preciso sobre áreas no testeadas |
| **Configuración por entornos** | `config.py` con Development, Production, Testing configs separados | Facilita transiciones entre contextos sin cambios de código |
| **Blueprints modulares** | Flask Blueprints para auth, api, dashboard, main, quiz | Permite navegación clara del código; nuevo desarrollador encuentra dónde están las rutas |
| **Dependencies minimalistas** | 36 dependencias en requirements.txt (Flask, PyMongo, pytest) | Curva de aprendizaje reducida; menos tecnología que dominar |
| **Documentación existente** | README.md con features, screenshots, demo credentials | Bajo onboarding para nuevos contribuidores |
| **SonarCloud configurado** | `sonar-project.properties` con organización y project key | Análisis estático automático; deuda técnica visible |
| **Gitignore adecuado** | Excluye `__pycache__/`, `env/` | Reduce ruido en el repositorio |

##### ❌ Puntos Negativos

| Área | Problema | Impacto en DevEx |
| :--- | :------- | :--------------- |
| **Configuración manual de variables de entorno** | MONGODB_URI debe configurarse manualmente; no hay `.env.example` | Friction en onboarding; nuevo desarrollador tarda en levantar el proyecto |
| **Deprecación no abordada** | `@app.before_first_request` (Flask 2.3+) y `os.urandom(12)` | Técnicamente funciona pero genera warnings; riesgo de rotura futura |
| **Inconsistencia en respuestas API** | Alterna `status='fail'` y `status='failed'` | Dificultad para consumir la API; necesidad de manejar ambos casos |
| **Errores expuestos al cliente** | `str(e)` en respuestas JSON de API | Riesgo de seguridad + developer frustration al depurar |
| **Secretos hardcodeados en seed** | Admin credentials en `server.py:29` (`admin1`) | Si alguien sube esto, queda expuesto en historial de git |
| **Sin pre-commit hooks** | No hay validación antes de commits | Código con typos/lint puede llegar a main |
| **Typos en código** | `get_scorest`, `Unkown`, `unkown` | Confusión; afectan legibilidad y mantenimiento |
| **Dependencias desactualizadas** | Flask 2.0.2 (2021), Werkzeug 2.0.2 | Vulnerabilidades conocidas; comportamiento inesperado con Python 3.11+ |
| **Sin type hints** | Código sin annotaciones de tipo | Menor tooling (autocomplete, error checking); mayor carga cognitiva |
| **Logs usando print** | `print('new index created ..')` en `api/quiz.py` | Difícil trazabilidad en producción; polución de output |

##### 🔧 Oportunidades de Mejora DevEx

| Mejora | Prioridad | Esfuerzo | Impacto |
| :----- | :-------: | :------: | :------ |
| Agregar `.env.example` con variables requeridas | Alta | Bajo | Elimina fricción de onboarding |
| Crear script `scripts/setup.sh` para instalar deps + config inicial | Alta | Bajo | Automatiza primero 5 minutos del developer |
| Implementar pre-commit hooks (ruff/flake8 + pytest) | Alta | Bajo | Previene código de baja calidad en CI |
| Actualizar a Flask 3.x LTS | Media | Medio | Seguridad + nuevas features + mejor error messages |
| Agregar type hints progresivamente | Media | Alto | Mejor tooling, autocomplete, menos bugs |
| Centralizar manejo de errores API | Media | Bajo | Consistencia; mejor DX para consumir la API |
| Reemplazar `print` por `app.logger` | Baja | Bajo | Trazabilidad en producción |
| Documentar el flujo de datos con diagrams/ADR | Baja | Medio | Reduce carga cognitiva para nuevos devs |

---

### 6.2 Framework SPACE

#### 6.2.1 Definición

El framework **SPACE** (Forsman et al., 2021) mide la productividad del desarrollador en 5 dimensiones:
- **S** — Satisfaction: Satisfacción del desarrollador con su trabajo y herramientas
- **P** — Performance: Outcome medible del trabajo (velocity, bugs resueltos, features)
- **A** — Activity: Medidas de actividad (commits, PRs, builds, tests)
- **C** — Communication: Colaboración y teamwork
- **E** — Efficiency: Qué tan bien se usan los recursos (caching, parallelization, flow)

#### 6.2.2 Métricas Identificables para el Proyecto

##### Satisfaction (S)

| Métrica | Estado Actual | Cómo medir | Meta sugerida |
| :------- | :------------ | :--------- | :------------ |
| **Tiempo hasta el primer commit significativo** | ~15-30 min (config manual) | Medir onboarding de nuevos devs | < 10 min |
| **Frecuencia de bloqueos ("estoy atascado")** | Desconocido | Survey mensual | Reducir 30% |
| **NPS del equipo sobre herramientas** | Desconocido | Survey trimestral | > 50 |
| **Tasa de rotación de contexto** (switching entre tareas) | Alta (múltiples archivos sin service layer) | Telemetry / survey | < 5 switches/día |

##### Performance (P)

| Métrica | Estado Actual | Cómo medir | Meta sugerida |
| :------- | :------------ | :--------- | :------------ |
| **Features completadas por sprint** | Desconocido | GitHub milestones | Baseline + 20% |
| **Bugs en producción por release** | Desconocido | Bug tracker | < 3/release |
| **Cobertura de código** | 90% | `pytest --cov` | Mantener > 85% |
| **Debt ratio** (issues SonarCloud) | ~10% del código | SonarCloud | < 5% |
| **MRR** (Mean Repair Time) para bugs | Desconocido | Ticket resolution time | < 4 horas |

##### Activity (A)

| Métrica | Estado Actual | Cómo medir | Meta sugerida |
| :------- | :------------ | :--------- | :------------ |
| **Commits por semana** | ~2-3/semana (historial) | `git shortlog -sn --since="7 days"` | 5-10/semana |
| **PRs merged por semana** | ~1-2/semana | GitHub insights | 3-5/semana |
| **Tests ejecutados por día** | ~84 tests, 2-3 min | CI runs | Mantener o reducir tiempo |
| **Build time** | ~2-3 min (CI) | GitHub Actions logs | < 2 min |
| **Líneas de código escritas/eliminadas** | Net positivo (~50/week) | `git diff --stat` | Monitorear deuda técnica |

##### Communication (C)

| Métrica | Estado Actual | Cómo medir | Meta sugerida |
| :------- | :------------ | :--------- | :------------ |
| **Tiempo de review de PRs** | Desconocido | GitHub PR metrics | < 24 horas |
| **Reviewers por PR** | ~1 (comités limitados) | GitHub PR data | 2-3 |
| ** Comentarios en código/documentación** | Limitado | Survey | > 50%覆盖率 |
| **ADRs/decisiones arquitectónicas documentadas** | 0 | Archivos en `docs/` | > 5 ADRs |

##### Efficiency (E)

| Métrica | Estado Actual | Cómo medir | Meta sugerida |
| :------- | :------------ | :--------- | :------------ |
| **Costo de CI/CD por build** | ~$0 (GitHub Actions free tier) | GitHub Actions billing | Mantener |
| **Test suite execution time** | ~2-3 min | `pytest --durations=10` | < 2 min |
| **Tiempo de cold start** (setup dev environment) | ~15-30 min | Onboarding measurement | < 10 min |
| **Cache hit ratio en CI** | Desconocido | GitHub Actions cache stats | > 70% |
| **Parallelization en CI** | Parcial (tests secuenciales) | Workflow config | Tests paralelos |
| **Ratio tiempo-coding / tiempo-configurando** | Bajo (~70/30) | Time tracking | > 80/20 |

---

### 6.3 Dashboard de Métricas DevEx + SPACE Sugerido

```yaml
# .github/ISSUE_TEMPLATES/devex-metric.yml

DevEx & SPACE Metrics:
  S - Satisfaction:
    - First commit time: < 10 min
    - Setup script available: Yes/No
    - .env.example exists: Yes/No
  
  P - Performance:
    - Test coverage: > 85%
    - SonarQube issues: < 10 blockers
    - Bug escape rate: < 5%
  
  A - Activity:
    - Weekly commits: > 5
    - PRs merged: > 3
    - Build pass rate: > 95%
  
  C - Communication:
    - Avg PR review time: < 24h
    - PRs with 2+ reviewers: > 50%
  
  E - Efficiency:
    - CI time: < 2 min
    - Test suite time: < 2 min
    - Cold start: < 10 min
```

---

### 6.4 Plan de Implementación DevEx + SPACE

#### Fase 1: Quick Wins (Semana 1-2)

| Acción | Impacto | Métrica afectada |
| :----- | :------ | :--------------- |
| Crear `.env.example` | Onboarding | S (satisfaction) |
| Agregar pre-commit hook con ruff | Code quality | P (performance) |
| Script `scripts/setup.sh` | Onboarding | S (satisfaction), E (efficiency) |
| Actualizar README con setup rápido | Onboarding | S (satisfaction) |
| Corregir typos y `status='failed'` → `'fail'` | DX | E (efficiency) |

#### Fase 2: Medium-term (Semana 3-6)

| Acción | Impacto | Métrica afectada |
| :----- | :------ | :--------------- |
| Migrar a Flask 3.x con typing | Security + DX | P (performance), S (satisfaction) |
| Implementar Service Layer | Maintainability | E (efficiency), S (satisfaction) |
| Agregar GitHub Actions cache optimization | CI speed | E (efficiency), A (activity) |
| Dashboard de métricas con GitHub Actions | Visibility | C (communication), P (performance) |
| Integrar Slack/Teams para PR notifications | Communication | C (communication) |

#### Fase 3: Long-term (Mes 2-3)

| Acción | Impacto | Métrica afectada |
| :----- | :------ | :--------------- |
| Type hints en todo el codebase | DX + Reliability | S (satisfaction), P (performance) |
| E2E tests con Playwright/Cypress | Quality | P (performance) |
| Developer survey trimestral | Satisfaction | S (satisfaction) |
| Architecture Decision Records (ADRs) | Knowledge sharing | C (communication) |
| Onboarding documentation interactiva | Onboarding | S (satisfaction) |

---

### 6.5 Conclusiones y Recomendaciones Finales

#### Fortalezas del proyecto en DevEx + SPACE:
1. **Infraestructura de testing sólida** (84 tests, 90% coverage) — habilita confianza y productividad
2. **CI/CD configurado** con SonarCloud — visibility sobre calidad
3. **Estructura modular** con Blueprints — bajo acoplamiento, fácil navegación
4. **Documentación básica** — reduce curva de aprendizaje

#### Áreas críticas a mejorar:
1. **Onboarding friction** — sin `.env.example` ni script de setup
2. **Code quality tooling ausente** — sin pre-commit hooks, sin linter configurado
3. **Métricas de equipo invisibles** — sin tracking de satisfaction, communication, o long-term performance
4. **Actualización de dependencias** — Flask 2.0.2 (2021) con vulnerabilidades conocidas
5. **Centralización de configuración** — SECRET_KEY en código, MONGODB_URI manual

#### Inversión sugerida:
- **40%** del tiempo en quick wins (Fase 1) — impacto inmediato en satisfaction
- **35%** en tooling y automatización — impacto en efficiency y performance
- **25%** en métricas y feedback loops — impacto en communication y long-term improvement

---

*Sección creada para la rama `DevEx`. Actualizar conforme se implementen mejoras.*
