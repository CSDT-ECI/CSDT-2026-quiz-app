<div align="center">

# 🏛️ Architectural Smells — Quiz App · CSDT 2026

*Identificación y documentación de malas prácticas arquitecturales*

---

</div>

> Este documento identifica y documenta los **architectural smells** detectados en el repositorio Quiz App, clasificados según el catálogo establecido en el paper de referencia:
>
> Mumtaz, H., Singh, P., & Blincoe, K. (2020). *A Systematic Mapping Study on Architectural Smells Detection*. Journal of Systems and Software. https://doi.org/10.1016/j.jss.2020.110885

---

## 👥 Equipo

| | |
| :--- | :--- |
| **Nombre del equipo** | Anti-Spaghetti-Squad |
| **Integrantes** | Jairo Andrés Jimenez · Edgar Ricardo Alvarez · Juliana Briceño Castro |

---

## 📑 Índice

1. [Contexto arquitectural del proyecto](#1-contexto-arquitectural-del-proyecto)
2. [Catálogo de Architectural Smells identificados](#2-catálogo-de-architectural-smells-identificados)
   - [AS-01 · Scattered Functionality](#as-01--scattered-functionality)
   - [AS-02 · God Component / Concern Overload](#as-02--god-component--concern-overload)
   - [AS-03 · Cyclic Dependency](#as-03--cyclic-dependency)
   - [AS-04 · Abstraction without Decoupling (Dependency Inversion Violation)](#as-04--abstraction-without-decoupling-dependency-inversion-violation)
   - [AS-05 · Sloppy Delegation](#as-05--sloppy-delegation)
   - [AS-06 · Ambiguous Interface](#as-06--ambiguous-interface)
   - [AS-07 · Feature Concentration](#as-07--feature-concentration)
   - [AS-08 · Implicit Cross-module Dependency](#as-08--implicit-cross-module-dependency)
3. [Resumen y priorización](#3-resumen-y-priorización)
4. [Relación con deuda técnica documentada](#4-relación-con-deuda-técnica-documentada)
5. [Referencias](#5-referencias)

---

## 1. Contexto arquitectural del proyecto

La aplicación Quiz App sigue una arquitectura **web en capas** implementada con **Flask** (Python), organizada en Blueprints que separan temáticamente las rutas. Sus componentes principales son:

```
quiz-app/
├── app/
│   ├── __init__.py          ← application factory + global singletons
│   ├── db.py                ← acceso global a la BD
│   ├── api/                 ← Blueprint: endpoints REST (users + quizzes)
│   ├── auth/                ← Blueprint: autenticación + formularios
│   ├── dashboard/           ← Blueprint: vistas + formularios de gestión
│   ├── main/                ← Blueprint: landing page
│   ├── quiz/                ← Blueprint: flujo de resolución de quiz
│   └── modules/
│       ├── decorators.py    ← cross-cutting: autorización
│       ├── mongo.py         ← wrapper de conexión a MongoDB
│       └── utils.py         ← utilidades + re-export de Mongo_Utils
├── config.py                ← configuración por entorno
└── server.py                ← punto de entrada + seed de datos
```

**Estilo arquitectural adoptado:** MVC simplificado sobre Flask Blueprints, sin capa de servicios ni repositorios explícitos.

**Base de datos:** MongoDB (PyMongo), accedida a través de dos objetos globales (`db`, `quiz`) definidos en `app/db.py`.

---

## 2. Catálogo de Architectural Smells identificados

---

### AS-01 · Scattered Functionality

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | MVC / Component |
| **Clasificación en el paper** | *Scattered Functionality* — detectado por técnicas de code smells analysis y graph-based (Tabla 14, [P26, P27, P46, P47, P76, P77]) |
| **Calidad afectada** | Mantenibilidad, Cohesión |
| **Severidad** | Alta |

#### Descripción

Una funcionalidad que debería estar encapsulada en un único componente se encuentra **dispersa en múltiples módulos** sin ninguna capa de servicios intermedia. Concretamente, la **lógica de autorización** (decidir si un usuario puede ver o modificar un quiz) aparece duplicada en al menos cuatro lugares distintos del código:

```python
# app/dashboard/views.py — línea 56 (manage_quiz)
author = {'$exists':True} if session.get('type') == 1 else session.get('username')

# app/dashboard/views.py — línea 81 (edit_quiz)
if check and (session.get('username') == check['author'] or session.get('type') == 1):

# app/dashboard/views.py — línea 113 (delete_quiz)
if result.get('author') == session.get('username') or session.get('type') == 1:

# app/api/quiz.py — línea 50 (edit_quiz endpoint)
if check and (session.get('username') == check['author'] or session.get('type') == 1):

# app/api/quiz.py — línea 106 (get_scorest)
author = {'$exists':True} if session.get('type') == 1 else session.get('username')
```

De igual modo, la **lógica de acceso a datos de usuarios** (`db.users.find_one`, `db.users.insert_one`, `db.users.update_one`) está esparcida sin abstracción en `api/views.py`, `auth/forms.py` y `dashboard/forms.py`.

#### Evidencia directa

- `app/dashboard/views.py`: líneas 56, 81, 113
- `app/api/quiz.py`: líneas 50, 106
- `app/auth/forms.py`: líneas 60–65 (validadores con acceso directo a `db`)
- `app/dashboard/forms.py`: línea 29 (validador con acceso directo a `db`)

#### Impacto

Cualquier cambio en la política de autorización (p.ej. añadir un rol "moderador") requiere modificar **todos** los puntos manualmente, con alto riesgo de inconsistencia. La funcionalidad no tiene un "hogar" arquitectural único.

#### Refactoring sugerido

Crear `app/services/auth_service.py` con funciones como `is_quiz_author_or_admin(quiz_doc, session)` y `get_author_filter(session)`, y centralizar ahí toda la lógica de autorización.

---

### AS-02 · God Component / Concern Overload

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | MVC / Component |
| **Clasificación en el paper** | *God Component* (Tabla 3, [P84]) / *Concern Overload* (Tabla 4, [P30]) |
| **Calidad afectada** | Mantenibilidad, Cohesión, Modificabilidad |
| **Severidad** | Alta |

#### Descripción

El componente `app/api/` actúa como un **God Component**: concentra responsabilidades que pertenecen a capas distintas de la arquitectura. Los módulos `api/views.py` y `api/quiz.py` mezclan en una sola función:

1. **Parsing y validación de la request HTTP** (obtener JSON, validar con WTForms)
2. **Lógica de negocio** (calcular puntaje, generar códigos, decidir autorización)
3. **Acceso directo a la base de datos** (queries MongoDB)
4. **Formateo de la respuesta HTTP** (construcción del JSON de respuesta)

El ejemplo más claro es la función `nilai()` en `api/quiz.py` (líneas 57–97):

```python
@api.route('/quiz/nilai/<code>', methods=['POST'])
def nilai(code):
    # 1. Acceso a BD
    check = json_decoder(quiz.find_one({'code':code}))
    json_request = request.get_json()
    if check:
        # 2. Lógica de negocio: parseo de respuestas
        list_id = [int(x.replace('quest_','')) for x in json_request]
        list_answer = json_request.values()
        zipper = zip(list_id, list_answer)
        data_check = check['data']
        # 3. Lógica de negocio: cálculo de puntaje
        list_true = [data_check[x]['question'] for x, y in zipper
                     if data_check[x].get('answer') and data_check[x].get('answer').lower() == y]
        perfect_value = 100
        per_true = perfect_value/len(data_check)
        fix_value = round(len(list_true) * per_true)
        # 4. Acceso a BD: buscar usuario
        user = json_decoder(db.users.find_one({'username':session.get('username', None)}))
        # 5. Acceso a BD: insertar score
        db.score.insert_one(json_decoder(data_value))
        # 6. Respuesta HTTP
        return jsonify(status='success', data=data_value)
```

Esta función ejecuta **cuatro responsabilidades distintas** en ~40 líneas, violando el principio de Single Responsibility en el nivel arquitectural.

#### Evidencia directa

- `app/api/quiz.py`: función `nilai()`, líneas 57–97
- `app/api/views.py`: función `add_account()`, líneas 19–47 (validación + negocio + BD + respuesta)
- `app/api/views.py`: función `edit_profile()`, líneas 105–120 (negocio + BD + sesión + respuesta)

#### Impacto

Los módulos de API no pueden ser probados de forma unitaria sin instanciar toda la pila (Flask + MongoDB). La adición de nuevas reglas de negocio requiere entender todo el flujo mezclado.

#### Refactoring sugerido

Introducir una capa de servicios: `app/services/quiz_service.py` (con `calculate_score`, `submit_answers`, `find_quiz_by_code`) y `app/services/user_service.py` (con `get_user`, `create_user`, `update_user`). Las funciones de vista solo orquestan request → servicio → response.

---

### AS-03 · Cyclic Dependency

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | Dependency |
| **Clasificación en el paper** | *Cyclic Dependency* — uno de los smells más detectados en la literatura (Tabla 14, detectado por rules-based, graph-based, DSM, code smells analysis, history-based y visualization) |
| **Calidad afectada** | Mantenibilidad, Modularidad, Testabilidad |
| **Severidad** | Alta |

#### Descripción

Existe una **dependencia circular** entre el módulo de aplicación y el módulo de base de datos:

```
app/__init__.py
  └── importa Mongo_Utils desde app.modules.utils
  └── crea mongo_utils = Mongo_Utils()

app/db.py
  └── from app import mongo_utils      ← importa desde app/__init__
  └── db, quiz = mongo_utils.get_db()  ← evalúa en tiempo de importación

app/modules/utils.py
  └── from .mongo import Mongo_Utils   ← re-exporta desde mongo.py
```

El ciclo completo es:

```
app/__init__.py  ←──────────────────────────────┐
      │                                          │
      └── crea mongo_utils                       │
                                                 │
app/db.py                                        │
      └── from app import mongo_utils  ──────────┘
      └── db, quiz = mongo_utils.get_db()  (ejecución al importar)
```

Además, `app/modules/utils.py` re-exporta `Mongo_Utils` desde `mongo.py`, haciendo que cualquier módulo que importe `utils` adquiera también la dependencia hacia el cliente de MongoDB:

```python
# app/modules/utils.py — línea 4
from .mongo import Mongo_Utils   # ← re-export no intencional que arrastra dependencia
```

Y `app/__init__.py` importa `Mongo_Utils` desde `utils` en lugar de hacerlo directamente desde `mongo`:

```python
# app/__init__.py — línea 2
from .modules.utils import Mongo_Utils   # ← debería ser from .modules.mongo
```

#### Evidencia directa

- `app/__init__.py`: línea 2 (`from .modules.utils import Mongo_Utils`)
- `app/db.py`: línea 1 (`from app import mongo_utils`)
- `app/modules/utils.py`: línea 4 (`from .mongo import Mongo_Utils`)

#### Impacto

Este ciclo hace frágil el orden de importación: si Python resuelve `app/db.py` antes de que `app/__init__.py` haya terminado de inicializarse, el objeto `mongo_utils` aún no existe y la aplicación lanza un `ImportError`. Los tests deben mockear cuidadosamente este ciclo (reflejado en la deuda de testing documentada: "dependencia frágil del mock de MongoDB").

#### Refactoring sugerido

- `app/__init__.py` debe importar `Mongo_Utils` directamente desde `app.modules.mongo`.
- `app/db.py` debe desaparecer: los módulos deben obtener la conexión bajo demanda a través de una función (`get_db()`) o un patrón de inyección de dependencias, no en tiempo de importación.
- Eliminar el re-export de `Mongo_Utils` desde `utils.py`.

---

### AS-04 · Abstraction without Decoupling (Dependency Inversion Violation)

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | Component / MVC |
| **Clasificación en el paper** | *Abstraction without Decoupling* (Tabla 14, [P16]) — también relacionado con *Unauthorized Dependency* |
| **Calidad afectada** | Mantenibilidad, Reusabilidad, Testabilidad |
| **Severidad** | Alta |

#### Descripción

Los módulos de **alto nivel** de la arquitectura (vistas, formularios) importan **directamente** el módulo de bajo nivel de acceso a datos (`app.db`), sin ninguna abstracción intermedia. Esto viola la Dependency Inversion Principle a nivel arquitectural:

```python
# app/api/views.py — línea 8
from app.db import db, quiz

# app/api/quiz.py — línea 7
from app.db import quiz, db

# app/dashboard/views.py — línea 11
from app.db import quiz, db

# app/auth/forms.py — línea 16
from app.db import db

# app/dashboard/forms.py — línea 5
from app.db import db
```

**Cinco módulos de capas distintas** (rutas de API, rutas de dashboard, formularios de autenticación) dependen directamente del objeto `db` que referencia a MongoDB. No existe ninguna capa de repositorio ni de servicio que abstraiga el mecanismo de persistencia.

Adicionalmente, los **formularios WTForms** (`auth/forms.py`, `dashboard/forms.py`) acceden directamente a la base de datos dentro de sus validadores, lo que representa una dependencia arquitecturalmente inapropiada: la capa de presentación (formularios) accediendo a la capa de datos sin intermediario:

```python
# app/auth/forms.py — línea 60
def validate_username(self, username):
    if db.users.find_one({'username':username.data}):   # ← capa presentación → BD
        raise ValidationError('Username already registered')

# app/dashboard/forms.py — línea 29
def validate_old_password(self, old_password):
    old_pw = db.users.find_one({'username':session.get('username')})  # ← ídem
```

#### Evidencia directa

- `app/api/views.py`: línea 8
- `app/api/quiz.py`: línea 7
- `app/dashboard/views.py`: línea 11
- `app/auth/forms.py`: línea 16 + líneas 60, 64 (queries dentro de validadores)
- `app/dashboard/forms.py`: línea 5 + línea 29 (query dentro de validador)

#### Impacto

Si se cambia MongoDB por otro motor de base de datos (PostgreSQL, SQLite), se deben modificar **todos** los archivos que referencian `db.users.*` o `quiz.*` directamente. Los formularios no pueden ser instanciados ni probados sin tener una conexión a la base de datos activa.

#### Refactoring sugerido

Crear repositorios o servicios (`UserRepository`, `QuizRepository`) como abstracción intermedia. Los formularios deben recibir una función de validación inyectada, no importar `db` directamente.

---

### AS-05 · Sloppy Delegation

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | MVC |
| **Clasificación en el paper** | *Sloppy Delegation* (Tabla 14, [P30]) — componente que delega inadecuadamente responsabilidades a otros |
| **Calidad afectada** | Mantenibilidad, Separación de preocupaciones |
| **Severidad** | Media |

#### Descripción

El módulo `app/modules/utils.py` realiza una **delegación inadecuada**: re-exporta `Mongo_Utils` desde `mongo.py`, mezclando en un solo módulo tanto utilidades puras (funciones de hash, generación de códigos, serialización JSON) como la clase de infraestructura de base de datos. Esta combinación hace que cualquier módulo que necesite una simple utilidad adquiera involuntariamente la dependencia hacia PyMongo:

```python
# app/modules/utils.py — mezcla de responsabilidades
import random
import string
from bson.objectid import ObjectId
from .mongo import Mongo_Utils          # ← infraestructura de BD (aquí no corresponde)
from werkzeug.security import generate_password_hash, check_password_hash
import json, bson
from bson.json_util import default
from bson import ObjectId              # ← importación duplicada de ObjectId (líneas 3 y 8)

def json_decoder(json_response): ...   # utilidad de serialización
def generate_code(nums: int=6): ...    # utilidad de generación
def generate_password(password): ...   # utilidad de seguridad
def check_password(pw_hash, password): # utilidad de seguridad
```

La re-exportación de `Mongo_Utils` en `utils.py` causa que `app/__init__.py` importe desde el lugar incorrecto:

```python
# app/__init__.py — línea 2
from .modules.utils import Mongo_Utils  # ← debería ser from .modules.mongo
```

Esto también es el origen de la dependencia circular documentada en AS-03.

#### Evidencia directa

- `app/modules/utils.py`: línea 4 (`from .mongo import Mongo_Utils`)
- `app/modules/utils.py`: líneas 3 y 8 (importación duplicada de `ObjectId`)
- `app/__init__.py`: línea 2 (importación desde lugar incorrecto)

#### Impacto

El módulo `utils.py` viola la cohesión modular. Un desarrollador que busque utilidades puras se encontrará con infraestructura de base de datos sin advertencia previa. Los imports duplicados (`ObjectId`) indican falta de revisión y aumentan el ruido cognitivo.

#### Refactoring sugerido

Separar `utils.py` en tres módulos con responsabilidad única:
- `app/modules/security.py`: funciones de hash y contraseñas
- `app/modules/utils.py`: solo utilidades puras (JSON, generación de códigos)
- `app/modules/mongo.py`: ya existe, debe ser la única fuente de `Mongo_Utils`

---

### AS-06 · Ambiguous Interface

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | MVC / Other smells |
| **Clasificación en el paper** | *Ambiguous Interface* (Tabla 14, [P34, P35, P46, P47, P76, P77]) |
| **Calidad afectada** | Mantenibilidad, Usabilidad de la API, Consistencia |
| **Severidad** | Media |

#### Descripción

La interfaz pública de la API REST presenta **contratos ambiguos** en múltiples dimensiones, haciendo que los consumidores no puedan predecir con certeza el comportamiento de los endpoints:

**a) Inconsistencia en el campo `status` de las respuestas JSON:**

```python
# app/api/views.py — línea 63
return jsonify(status='failed', message='what are you doing here?')

# app/api/views.py — línea 113
return jsonify(status='failed', message='Username already registered')

# app/api/quiz.py — línea 117
return jsonify(status='failed', data=[])

# app/api/views.py — línea 42
return jsonify(status='fail', errors='unkown failure')

# app/api/views.py — línea 87
return jsonify(status='fail', errors='invalid username / password')
```

El valor de `status` en caso de error alterna sin patrón entre `'fail'` y `'failed'`, obligando al cliente a manejar ambos casos.

**b) Inconsistencia en la clave del mensaje de error** (`errors` vs `message`):

```python
return jsonify(status='fail', errors='...')    # algunos endpoints
return jsonify(status='failed', message='...') # otros endpoints
```

**c) Exposición de detalles de implementación en errores:**

```python
# app/api/views.py — línea 44
except Exception as e:
    return jsonify(status='fail', errors='<p>{}'.format(e))  # ← stack trace al cliente
```

**d) Endpoint con nombre incorrecto (typo):**

```python
# app/api/quiz.py — línea 99–100
@api.route('/quiz/author/<author>/getScores')
def get_scorest(author):   # ← "scorest" en lugar de "scores"
```

#### Evidencia directa

- `app/api/views.py`: líneas 42, 44, 63, 87, 113, 116
- `app/api/quiz.py`: líneas 32, 55, 97, 117
- `app/api/quiz.py`: línea 100 (función `get_scorest`)

#### Impacto

Los clientes de la API (JavaScript frontend, tests) deben manejar múltiples representaciones del mismo concepto. El código JavaScript en `script.js` y `dashboard.js` ya presenta lógica defensiva por este motivo. La interfaz ambigua es un obstáculo para la integración de nuevos clientes o microservicios.

#### Refactoring sugerido

Definir en `app/api/constants.py` las constantes `API_STATUS_SUCCESS = 'success'` y `API_STATUS_FAIL = 'fail'`, y un helper `api_error(message, code=400)`. Unificar la clave de mensaje de error a `message`. Documentar el contrato con un esquema OpenAPI.

---

### AS-07 · Feature Concentration

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | MVC |
| **Clasificación en el paper** | *Feature Concentration* (Tabla 14, [P26, P27, P46, P47]) |
| **Calidad afectada** | Mantenibilidad, Modularidad |
| **Severidad** | Media |

#### Descripción

El Blueprint `api` concentra funcionalidades que, por diseño MVC limpio, deberían estar en componentes separados. El módulo `app/api/quiz.py` acumula sin distinción:

- Creación y edición de quizzes (`add_quiz`, `edit_quiz`)
- Cálculo y almacenamiento de puntajes (`nilai`)
- Consulta de scores por autor (`get_scorest`, `my_scores`)
- Búsqueda de quizzes (`quiz_search`)
- Carga masiva de datos desde CSV/JSON (`upload_csv`)

Son **cinco áreas funcionales distintas** concentradas en un único archivo de 206 líneas. De manera similar, `app/api/views.py` mezcla gestión de usuarios y lógica de sesión en el mismo componente.

Esta concentración se agrava porque el mismo Blueprint `api` engloba tanto la API de usuarios (`api/views.py`) como la API de quizzes (`api/quiz.py`), ambos registrados bajo el mismo prefijo sin separación semántica explícita.

Además, la ruta duplicada en `dashboard/views.py` es otro indicador de feature concentration mal gestionada:

```python
# app/dashboard/views.py — líneas 117–126
@dashboard.route('/scores')
@login_required
def scores():
    return render_template('dashboard/users-scores.html')   # ← duplicado exacto

@dashboard.route('/users-scores')
@login_required
def users_scores():
    return render_template('dashboard/users-scores.html')   # ← mismo template
```

#### Evidencia directa

- `app/api/quiz.py`: 206 líneas, 8 funciones con responsabilidades heterogéneas
- `app/api/views.py`: 121 líneas, mezcla gestión de usuarios y sesión
- `app/dashboard/views.py`: líneas 117–126 (rutas duplicadas para el mismo template)

#### Impacto

Cuando un desarrollador necesita modificar la lógica de cálculo de puntajes, debe navegar entre funciones de creación de quizzes, búsqueda y carga de archivos en el mismo archivo, aumentando la carga cognitiva. La colocación de rutas duplicadas puede crear comportamiento divergente futuro si se modifica una y no la otra.

#### Refactoring sugerido

Dividir el Blueprint `api` en sub-módulos: `api/users.py`, `api/quizzes.py`, `api/scores.py`. Eliminar la ruta duplicada `/scores` o `/users-scores` (mantener una y redirigir desde la otra).

---

### AS-08 · Implicit Cross-module Dependency

| Atributo | Detalle |
| :------- | :------ |
| **Categoría** | Dependency |
| **Clasificación en el paper** | *Implicit Cross-module Dependency* (Tabla 14, [P15, P16]) — dependencia entre módulos que no está declarada explícitamente en la interfaz |
| **Calidad afectada** | Mantenibilidad, Robustez, Testabilidad |
| **Severidad** | Media-Alta |

#### Descripción

Existen **dependencias implícitas de estado global** que no son declaradas en las firmas de las funciones ni en las interfaces de los módulos, sino que se consumen directamente desde el contexto de Flask (`session`) o desde variables globales de módulo (`db`, `quiz`).

**a) Dependencia implícita de sesión de Flask:**

Funciones en `dashboard/views.py`, `api/quiz.py` y `api/views.py` acceden a `session.get('username')`, `session.get('type')` sin recibirlo como parámetro. Esto crea una dependencia oculta del contexto HTTP de Flask que no es visible al leer la firma de la función:

```python
# app/dashboard/views.py — línea 56
def manage_quiz():
    author = {'$exists':True} if session.get('type') == 1 else ...
    # session no es un parámetro: es una dependencia implícita global
```

**b) Dependencia implícita de las variables globales `db` y `quiz`:**

El módulo `app/db.py` ejecuta código en tiempo de importación:

```python
# app/db.py
from app import mongo_utils
db, quiz = mongo_utils.get_db()   # ← efecto secundario en tiempo de importación
```

Cualquier módulo que haga `from app.db import db` adquiere una dependencia implícita en que MongoDB está disponible y en que `mongo_utils` ya fue inicializado. Esta dependencia no se declara en ninguna interfaz: es una precondición oculta del entorno.

**c) Dependencia implícita de orden de inicialización:**

`server.py` ejecuta el seed de datos **en tiempo de importación**, dentro de un bloque `with app.app_context()` a nivel de módulo. La función `seed_data()` no está registrada con ningún hook explícito del framework: simplemente se invoca antes de que el servidor WSGI empiece a aceptar requests, con acceso directo a `db` (importado también a nivel de módulo). Esto introduce varias precondiciones ocultas: que `create_app()` ya haya inicializado `mongo_utils`, que `app/db.py` se haya importado correctamente y que MongoDB sea alcanzable en ese instante.

```python
# server.py — líneas 10, 33–34
from app.db import db, quiz                  # ← import con efecto secundario (ver AS-03)

with app.app_context():
    seed_data()                              # ← falla al cargar el módulo si MongoDB no responde
```

Si MongoDB no está disponible al arrancar, la excepción de PyMongo se propaga durante la importación del módulo y no durante el manejo de un request, por lo que el mensaje no indica al operador que falta una dependencia externa.

#### Evidencia directa

- `app/db.py`: líneas 1–4 (ejecución en tiempo de importación)
- `server.py`: líneas 10 y 33–34 (import con efecto secundario + seed en tiempo de carga del módulo)
- `app/dashboard/views.py`: múltiples usos de `session.get(...)` como dependencia implícita
- `app/api/quiz.py`: múltiples usos de `session.get(...)` y `db`/`quiz` globales

#### Impacto

Las dependencias implícitas dificultan enormemente los tests: es necesario mockear el contexto de Flask, la sesión activa y la conexión a MongoDB simultáneamente para probar cualquier función. La deuda de testing documentada (en particular los problemas con `conftest.py` y el fixture `mock_mongodb`) es directamente causada por estas dependencias implícitas. En producción, si MongoDB no está disponible al inicio, la aplicación no falla con un mensaje claro sino con errores crípticos.

#### Refactoring sugerido

- Mover el `seed_data()` a un comando Flask CLI (`flask seed-admin`) o a un hook de inicialización explícito dentro del factory, de modo que no se ejecute en tiempo de importación.
- Encapsular el acceso a `session` en funciones utilitarias que reciban el contexto como parámetro.
- Reemplazar las variables globales `db`/`quiz` por funciones de acceso lazy (`get_db()`) que no ejecuten código en tiempo de importación.

---

## 3. Resumen y priorización

| # | Smell | Categoría | Severidad | Impacto Principal | Esfuerzo de Refactoring |
| :-: | :---- | :-------- | :-------: | :---------------- | :---------------------: |
| AS-01 | Scattered Functionality | MVC | 🔴 Alta | Mantenibilidad, Consistencia | Medio |
| AS-02 | God Component / Concern Overload | MVC / Component | 🔴 Alta | Mantenibilidad, Testabilidad | Alto |
| AS-03 | Cyclic Dependency | Dependency | 🔴 Alta | Modularidad, Inicialización | Medio |
| AS-04 | Abstraction without Decoupling | Component | 🔴 Alta | Testabilidad, Portabilidad | Alto |
| AS-05 | Sloppy Delegation | MVC | 🟡 Media | Cohesión, Claridad | Bajo |
| AS-06 | Ambiguous Interface | MVC | 🟡 Media | Usabilidad API, Consistencia | Bajo |
| AS-07 | Feature Concentration | MVC | 🟡 Media | Mantenibilidad, Legibilidad | Bajo-Medio |
| AS-08 | Implicit Cross-module Dependency | Dependency | 🟠 Media-Alta | Testabilidad, Robustez | Medio |

### Orden de atención sugerido

1. **AS-03 (Cyclic Dependency)** — Problema estructural de arranque; resuelve riesgos de `ImportError`.
2. **AS-04 (Abstraction without Decoupling)** — Habilita tests unitarios reales; precondición para refactorizar AS-01 y AS-02.
3. **AS-01 (Scattered Functionality)** — Una vez que existe una capa de servicios, centralizar la autorización es directo.
4. **AS-06 (Ambiguous Interface)** — Esfuerzo bajo, impacto en usabilidad inmediato.
5. **AS-05 (Sloppy Delegation)** — Limpieza estructural de `utils.py`.
6. **AS-07 (Feature Concentration)** — División de módulos de API.
7. **AS-02 (God Component)** — Requiere la capa de servicios (AS-04) como prerequisito.
8. **AS-08 (Implicit Cross-module Dependency)** — Paralelizable con AS-03 y AS-04.

---

## 4. Relación con deuda técnica documentada

Los architectural smells identificados tienen correspondencia directa con problemas ya documentados en el análisis de deuda técnica del proyecto (`Anti-Spaghetti-Squad_CSDT_2026.md`):

| Architectural Smell | Sección relacionada en el documento principal | Tipo de deuda |
| :------------------ | :-------------------------------------------- | :------------ |
| AS-01 Scattered Functionality | §1.2 "Lógica de autor repetida"; §2.4 "Helpers de autorización" | Deuda de diseño |
| AS-02 God Component | §1.5 "Lógica de negocio y vistas"; §4.2.1 SOLID-S | Deuda de diseño |
| AS-03 Cyclic Dependency | §1.2 "Acoplamiento a implementación" (`app/db.py`) | Deuda arquitectural |
| AS-04 Abstraction without Decoupling | §4.2.1 SOLID-D; §2.2 "Servicio de usuario"; §2.3 "Servicio de quiz" | Deuda arquitectural |
| AS-05 Sloppy Delegation | §2.8 "Módulo de utilidades"; §1.4 "Imports duplicados" | Deuda de diseño |
| AS-06 Ambiguous Interface | §2.1 "Respuestas API inconsistentes"; §1.3 "Consistencia y nomenclatura" | Deuda de código |
| AS-07 Feature Concentration | §2.9 "Rutas y vistas duplicadas"; §4.2.2 DRY | Deuda de diseño |
| AS-08 Implicit Cross-module Dependency | §1.1 "Deprecación de `before_first_request`"; §5.2.1 práctica #7 (deuda de testing) | Deuda arquitectural |

Los smells AS-03, AS-04 y AS-08 constituyen **deuda arquitectural primaria**: afectan la estructura de los módulos y la forma en que se resuelven las dependencias en tiempo de ejecución. Los smells AS-01, AS-02, AS-05 y AS-07 son **deuda de diseño en el nivel de componentes**. El smell AS-06 es de **deuda de interfaz**.

---

## 5. Referencias

- **Mumtaz, H., Singh, P., & Blincoe, K. (2020)**. A Systematic Mapping Study on Architectural Smells Detection. *Journal of Systems and Software*, 169, 110885. https://doi.org/10.1016/j.jss.2020.110885

- **Azadi, U., Fontana, F. A., & Taibi, D. (2019)**. Architectural smells detected by tools: A catalogue proposal. In *2019 IEEE/ACM International Conference on Technical Debt (TechDebt)*.

- **Fontana, F. A., Ferme, V., & Spinelli, S. (2012)**. Investigating the impact of code smells on system's quality: An empirical study on systems of different application domains. In *2012 IEEE International Workshop on Software Measurement*.

- **Martin, R. C. (2008)**. *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.

- **ISO/IEC 25010:2011**. Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models.

---

<div align="center">

*Documento elaborado para la rama `feat/architectural-smells-v2` — Quiz App · CSDT 2026 · Anti-Spaghetti-Squad*

*Puede actualizarse conforme se apliquen refactorizaciones o se detecten nuevos smells.*

</div>
