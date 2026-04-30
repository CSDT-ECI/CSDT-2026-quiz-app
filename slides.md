<!-- .slide: class="title" data-background-image="images/main.png" data-background-size="cover" -->

<div class="title-content">

# Análisis de deuda técnica<br>y refactorización

<div class="meta">

**Anti-Spaghetti-Squad** · Quiz App · CSDT 2026
Jairo Andrés Jiménez · Edgar Ricardo Álvarez · Juliana Briceño Castro

</div>

</div>

Note:
Bienvenida y presentación del equipo. La imagen muestra el "taller" del equipo: las herramientas que vamos a usar a lo largo de la charla — la matriz de priorización, la cuchilla de Clean Code, el cinturón de Refactor, el guantelete del ingeniero. El nombre del equipo, Anti-Spaghetti-Squad, refleja la misión: desenredar código tipo espagueti.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">Agenda · 15 minutos</div>

## Recorrido de la charla

| § | Tema | Imagen guía |
| :-: | :--- | :--- |
| 1 | **Code smells** detectados | Especímenes en frasco |
| 2 | **Técnicas de refactorización** propuestas | Máquina refactorizadora |
| 3 | **Priorización** impacto vs esfuerzo | Matriz steampunk |
| 4 | **Clean Code & XP** — qué cumplimos, qué no | Taller multinivel |
| 5 | **Deuda en testing** — el viaje 5.8 % → 90 % | Estación de remediación |
| 6 | **DevEx + SPACE** — métricas de equipo | Bastidor de medidores |
| 7 | **Architectural smells** — 8 hallazgos AS-01..AS-08 | Sala arquitectónica |

Note:
Cada sección abre con una de las imágenes generadas. La estructura es siempre la misma: encontramos X → proponemos Y. Resultado neto al final: lo que cambió y lo que sigue pendiente.

---

<!-- .slide: class="opener" data-background-image="images/Code smells.png" -->

<div class="opener-content">

<span class="eyebrow">Sección 1</span>

# Code smells & malas prácticas

</div>

Note:
Apertura de la sección 1. La imagen muestra el satchel de "Code Smell Refactor" con cables enredados saliendo — la metáfora literal del spaghetti code. Las dos botellas de vidrio funcionan como "antes y después": frasco de especímenes vs. frasco de Clean Code.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 1 · Code smells</div>

## Configuración, estructura y nomenclatura

<div class="found-fix">
<div class="col found">

#### Encontramos

- `SECRET_KEY = os.urandom(12)` se regenera en cada arranque → sesiones invalidadas, no apto para producción
- `@app.before_first_request` deprecado desde Flask 2.3
- `db` y `quiz` expuestos como globales en `app/db.py`
- Formularios hacen `db.users.find_one(...)` dentro de validadores
- Respuestas API alternan `'fail'` / `'failed'` sin criterio
- `get_scorest`, `Unkown`, `nilai()` (indonesio sin contexto)

</div>
<div class="col fix">

#### Proponemos

- `SECRET_KEY` desde **variable de entorno**, fallback solo en dev
- Reemplazar `before_first_request` por hook actual o **Flask CLI seed**
- Capa de **servicios** (`user_service`, `quiz_service`) entre formularios/vistas y `db`
- Constantes API: `API_STATUS_SUCCESS`, `API_STATUS_FAIL`
- Renombrar a `submit_quiz_answers()`, `get_scores()`, `MongoUtils`
- Limpiar imports muertos y `print()` → `app.logger`

</div>
</div>

Note:
Aquí están concentradas las 8 sub-categorías de code smells del documento. La columna izquierda lista los hallazgos más representativos; la derecha resume las acciones. Para detalle de cada uno hay 22 hallazgos puntuales en el documento — nos quedamos con los más impactantes.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 1 · Code smells · Bugs de frontend</div>

## JavaScript: errores que sí afectan producción

```javascript
// app/static/js/dashboard.js  (~línea 77)
if (path_name.length == 3 & path_name[1] == 'edit-quiz') { ... }
//                       ^ bitwise — debería ser &&

// app/static/js/dashboard.js  (~líneas 83–88)
$.post({ url: ..., data: ... });
// firma incorrecta — $.post espera (url, data, callback)

// app/static/js/script.js
$.ajax({ url, data }).done(...)
// sin .fail() — el usuario no recibe feedback si la red falla
```

**Impacto:** falsos positivos en navegación, errores AJAX silenciosos, comportamiento impredecible cuando `path_name.length` no es exactamente 3.

**Refactor sugerido:** sustituir por `$.ajax({ method: 'POST' }).done(...).fail(...)` y corregir `&` → `&&`.

Note:
Estos no son bugs académicos — son errores que probablemente ya están afectando a usuarios reales. El operador bitwise & sobre números pequeños a veces da el mismo resultado que && por coincidencia, lo cual hace el bug aún más insidioso. La falta de .fail() significa que cuando la red falla, el usuario simplemente ve la app "congelada".

---

<!-- .slide: class="opener" data-background-image="images/Refactoring techniques.png" -->

<div class="opener-content">

<span class="eyebrow">Sección 2</span>

# Técnicas de refactorización

</div>

Note:
La máquina refactorizadora: entrada caótica → válvulas con técnicas (Extract Method, Rename Symbol, Encapsulate Field, Separation of Concerns) → salida Clean Code. Es literalmente el flujo que vamos a discutir en esta sección.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 2 · 12 técnicas propuestas</div>

## Capas, servicios y centralización

| # | Técnica | Candidato concreto |
| :-: | :--- | :--- |
| 2.1 | *Replace Magic String with Constant* | `'fail'`, `'failed'`, `'success'` → `API_STATUS_*` |
| 2.2 | *Extract Class* / Service Layer | `app/services/user_service.py` |
| 2.3 | *Extract Class* / Service Layer | `app/services/quiz_service.py` + `score_service.py` |
| 2.4 | *Extract Method* + Parameter Object | `auth_utils.is_quiz_author_or_admin(...)` |
| 2.5 | *Replace Deprecated API* | `before_first_request` → Flask CLI `seed-admin` |
| 2.6 | *Replace Magic Value* | `SECRET_KEY` desde entorno, no `os.urandom(12)` |
| 2.10 | *Centralize Error Responses* | `@api.errorhandler` + formato `{status, message, code}` |

<small>Total: 12 técnicas catalogadas en el documento. Mostradas las de mayor impacto.</small>

Note:
La regla común a todas estas técnicas: las vistas Flask hoy actúan simultáneamente como controlador, servicio y repositorio. El refactor las devuelve a su rol natural — orquestar request/response — delegando lógica a servicios y acceso a datos a una capa explícita. Esto no es "ingeniería de astronauta" — es lo mínimo para poder testear.

---

<!-- .slide: class="opener" data-background-image="images/Prioritization matrix.png" -->

<div class="opener-content">

<span class="eyebrow">Sección 3</span>

# Priorización

</div>

Note:
La matriz steampunk muestra exactamente lo que vamos a hacer: clasificar cada hallazgo por impacto (alto/bajo) y esfuerzo (alto/bajo), y dejar caer cada uno en su cuadrante: Quick Wins, Major Projects, Filler, Time Sinks.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 3 · Impacto × Esfuerzo</div>

## Qué atacar primero

| Prioridad | Tema | Impacto | Esfuerzo |
| :-: | :--- | :--- | :-: |
| <span class="badge high">ALTA</span> | Unificar respuestas API y no exponer excepciones | Seguridad y consistencia | Bajo |
| <span class="badge high">ALTA</span> | `SECRET_KEY` desde entorno + reemplazo `before_first_request` | Seguridad y compatibilidad | Bajo |
| <span class="badge high">ALTA</span> | Corregir `$.post` y `&` en `dashboard.js` | Bugs en producción | Bajo |
| <span class="badge medium">MEDIA</span> | Service layer: usuario, quiz, scores | Mantenibilidad y tests | Medio |
| <span class="badge medium">MEDIA</span> | Helpers de autorización + manejo centralizado de errores | Consistencia | Bajo–Medio |
| <span class="badge low">BAJA</span> | Limpieza de imports, typos, refactor de `utils.py` | Claridad | Bajo |

**Estrategia:** atacar los **Quick Wins** primero — todos son bajo esfuerzo y dos de ellos son problemas activos de seguridad.

Note:
La regla del cuadrante Quick Wins: si el esfuerzo es bajo y el impacto es alto o medio, no hay razón para postergarlo. Las tres entradas marcadas ALTA son exactamente eso. Los Major Projects (capa de servicios) requieren tener tests primero — por eso están en Media, no en Alta.

---

<!-- .slide: class="opener" data-background-image="images/Clean Code & XP.png" -->

<div class="opener-content">

<span class="eyebrow">Sección 4</span>

# Clean Code & XP Practices

</div>

Note:
La gran sala-taller de la imagen sugiere que Clean Code no es un truco aislado — es una disciplina de equipo a escala arquitectónica. Los pequeños trabajadores en las estaciones laterales son una metáfora del pair programming. La torre central con el helix verde-rojo es el "ADN" del código limpio: tests, refactoring, simple design.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 4 · Clean Code · Diagnóstico</div>

## ¿Qué cumplimos? ¿Qué no?

<div class="two-col">
<div class="col good">

### ✅ Sí cumplimos

- **Estructura modular** con Blueprints (auth, api, dashboard)
- **Decoradores** para concerns transversales: `login_required`, `admin_required`
- **Validación declarativa** con WTForms
- **Funciones utilitarias pequeñas** (<10 líneas, una sola cosa)
- **Configuración centralizada** (`config.py` jerárquico)
- **Protección CSRF** integrada en toda la app
- **Templates con includes** — DRY en presentación

</div>
<div class="col bad">

### ❌ No cumplimos

- **Nombres significativos** — `nilai()`, `get_scorest`, `Mongo_Utils`
- **Funciones pequeñas** — `nilai()` mezcla parsing, cálculo, BD y respuesta en 40+ líneas
- **No exponer detalles** — `str(e)` enviado al cliente
- **Eliminar código muerto** — imports no usados, `print()` de debug
- **Manejo de errores consistente** — `'fail'` vs `'failed'`
- **Sin números mágicos** — `type == 1`, `100`, `14` repetidos
- **Tests** — auditoría inicial: cero tests significativos

</div>
</div>

Note:
La columna verde no es trivial — Clean Code reconoce que el proyecto tiene *bones* sólidos: la modularización con Blueprints, los decoradores, WTForms. Lo que falla es la disciplina al detalle: nombres, tamaño de funciones, manejo de errores. Esos son los que se atacan en las próximas semanas. Cita: "Si tienes que adivinar qué hace una función por su nombre, el nombre está mal" — Robert C. Martin.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 4 · SOLID & XP</div>

## Principios — estado del proyecto

| | S | O | L | I | D | DRY | KISS | Fail-Fast |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Estado** | ❌ | ❌ | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ |

#### Prácticas XP priorizadas

| 🔴 1 | **TDD / Crear tests** — habilitador de todo lo demás |
| :-: | :-- |
| 🔴 2 | **Integración Continua** — automatiza verificación |
| 🟡 3 | **Estándares + linter** (`ruff` / `flake8`) |
| 🟡 4 | **Refactoring continuo** — "Boy Scout Rule" |
| 🟢 5 | **Pair Programming** — especialmente seguridad |
| 🟢 6 | **Diseño Simple** + releases pequeños |

Note:
La prioridad 1 es TDD por una razón muy concreta: sin tests, *cualquier* refactor es un acto de fe. Una vez que existen tests confiables, la priorización 2-6 baja en costo. Es el "habilitador" del resto. Por eso la sección 5 es la más larga y la más importante de la presentación.

---

<!-- .slide: class="opener" data-background-image="images/Testing debt.png" -->

<div class="opener-content">

<span class="eyebrow">Sección 5</span>

# Deuda técnica en pruebas

</div>

Note:
Esta es la sección clave de la presentación. La imagen muestra a los miembros del equipo trabajando en la "Testing Debt Remediation Station" — los cables enredados son código sin tests, salen ordenados después de pasar por la máquina de cobertura. Las métricas en la pantalla del fondo (Coverage 90%, Risk Level Low) son nuestras métricas reales, no de adorno.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 5 · Estado inicial</div>

## Antes de intervenir

<div class="metric-grid">
<div class="metric">
<div class="label">Tests totales</div>
<div class="value">8</div>
<div class="delta">solo smoke tests</div>
</div>
<div class="metric">
<div class="label">Cobertura líneas</div>
<div class="value">5.8 %</div>
<div class="delta">29 / 499</div>
</div>
<div class="metric">
<div class="label">Cobertura branches</div>
<div class="value">0 %</div>
<div class="delta">0 / 98</div>
</div>
</div>

#### Prácticas de testing debt identificadas

- ❌ **Cero tests de lógica de negocio** — `nilai()`, `add_account()`, `api_login()` sin tests
- ❌ **Tests superficiales** — solo `assert response.status_code == 200`
- ❌ **Sin tests de funciones puras** — las más fáciles, las más descuidadas
- ❌ **Sin tests de seguridad** — `login_required`, `admin_required` no verificados
- ❌ **Sin tests de edge cases** — inputs inválidos, archivos malformados
- ❌ **Mock de MongoDB frágil** — `RuntimeError: MONGODB_URI not found` en CI

Note:
8 tests de tipo smoke significa que verificábamos que las páginas respondieran 200, pero no que hicieran lo que decían hacer. Cubrir 0% de branches significa que ninguna decisión `if/else` se ejecutaba en pruebas — los caminos de error eran completamente ciegos.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 5 · Después de dos intervenciones</div>

## Resultado: el viaje 5.8 % → 90 %

<div class="metric-grid">
<div class="metric headline">
<div class="label">Tests totales</div>
<div class="value">84</div>
<div class="delta">+76 nuevos · ×10.5</div>
</div>
<div class="metric headline">
<div class="label">Cobertura líneas</div>
<div class="value">90 %</div>
<div class="delta">+84 puntos · ×15.5</div>
</div>
<div class="metric headline">
<div class="label">Cobertura branches</div>
<div class="value">~84 %</div>
<div class="delta">+84 puntos · de 0%</div>
</div>
</div>

| Métrica | Inicial | 1ª intervención | **2ª intervención** |
| :--- | :-: | :-: | :-: |
| Tests totales | 8 | 45 | **84** |
| Cobertura líneas | 5.8 % | 70.54 % | **90 %** |
| Cobertura branches | 0 % | 29.59 % | **~84 %** |
| Archivos 100 % cubiertos | 2 | 12 | **16** |
| `dashboard/views.py` | 0 % | 46.94 % | **85 %** |
| `api/quiz.py` | 0 % | 57.72 % | **85 %** |

Note:
Este es el slide más importante de la presentación. 84 tests, 90% cobertura de líneas, ~84% cobertura de branches. Tres archivos críticos (dashboard/views, api/quiz, api/views) pasaron de 0% a más de 85%. La segunda intervención añadió tres módulos completos: test_dashboard_views (18), test_upload_csv (8), test_api_admin (13). Ese salto de cobertura de branches de 0 a 84 es probablemente el más significativo, porque las branches son donde viven los bugs de autorización.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 5 · Deuda remanente</div>

## Lo que aún falta

| Área | Descripción | Prioridad |
| :--- | :--- | :-: |
| `test_add_account_success` | Contaminación de BD: fixture `registered_user` con `autouse=True` inserta `testuser` antes del test | <span class="badge high">Alta</span> |
| `dashboard.download_quiz` | Agregación de MongoDB no soportada por mongomock | <span class="badge medium">Media</span> |
| `quiz_search` | Índice `$text` con soporte limitado en mongomock | <span class="badge low">Baja</span> |
| **Tests E2E** | Flujos completos: registro → login → crear → responder → ver scores | <span class="badge high">Alta</span> |
| **Tests de frontend (JS)** | `dashboard.js`, `script.js` — el bug `&` vs `&&` no está cubierto | <span class="badge medium">Media</span> |

**Patrón de la deuda restante:** dependencias del entorno (mongomock vs MongoDB real) y áreas no-Python (frontend). Pasos siguientes: tests E2E con Playwright, fixtures con limpieza explícita, ESLint para JS.

Note:
La prioridad alta de "Tests E2E" no es dogmática — es porque actualmente cada capa está testeada en aislamiento, pero los flujos completos no. Un usuario que se registra, hace login, crea un quiz, lo responde y ve sus scores toca cinco endpoints distintos; un fallo en el handoff entre dos de ellos no se detecta con tests unitarios.

---

<!-- .slide: class="opener" data-background-image="images/DevEx + SPACE framework.png" -->

<div class="opener-content">

<span class="eyebrow">Sección 6</span>

# DevEx + SPACE Framework

</div>

Note:
La imagen del bastidor de medidores y el panel de control con dimensiones medibles es exactamente lo que SPACE propone: convertir la "experiencia del desarrollador" en métricas observables. Cinco dimensiones, métricas concretas para cada una.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 6 · DevEx · Diagnóstico</div>

## Fortalezas y fricciones del proyecto

<div class="two-col">
<div class="col good">

### ✅ Fortalezas

- **CI/CD con GitHub Actions** — pytest + coverage + SonarCloud
- **Suite de 84 tests** + mongomock para aislamiento
- **90 % cobertura** con configuración explícita
- **Configuración por entornos** (dev / test / prod)
- **Blueprints modulares** — bajo acoplamiento
- **`requirements.txt` minimalista** (36 deps)
- **README** con features, screenshots, demo
- **SonarCloud** configurado y activo

</div>
<div class="col bad">

### ❌ Fricciones

- **Sin `.env.example`** — onboarding manual, doloroso
- **Sin pre-commit hooks** — typos llegan a `main`
- **Sin script `setup.sh`** — primer commit ~15-30 min
- **Flask 2.0.2 (2021)** — vulnerabilidades conocidas
- **Sin type hints** — menos tooling, más carga cognitiva
- **`print()` en producción** — sin trazabilidad
- **`SECRET_KEY` en código** — riesgo si se sube
- **Métricas de equipo invisibles** — sin tracking SPACE

</div>
</div>

Note:
La asimetría aquí es interesante: las fortalezas son cosas que el equipo hizo deliberadamente (configurar CI, escribir tests, modularizar). Las fricciones son cosas que faltan por hacer — no errores, sino oportunidades. Eso significa que mejorar DevEx es esencialmente añadir, no reescribir.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 6 · SPACE</div>

## Cinco dimensiones, métricas observables

| | Dimensión | Métrica clave actual | Meta |
| :-: | :--- | :--- | :--- |
| **S** | Satisfaction | Tiempo a primer commit ~15-30 min | < 10 min |
| **P** | Performance | Cobertura 90 %, debt ratio ~10 % | > 85 % / < 5 % |
| **A** | Activity | ~2-3 commits/sem, ~1-2 PRs/sem | 5-10 / 3-5 |
| **C** | Communication | 0 ADRs documentadas | > 5 ADRs |
| **E** | Efficiency | Build CI ~2-3 min, cold-start 15-30 min | < 2 min / < 10 min |

#### Plan de implementación · 3 fases

- **Fase 1 (sem 1-2)** — Quick wins: `.env.example`, pre-commit, `setup.sh`, README
- **Fase 2 (sem 3-6)** — Migrar a Flask 3.x, service layer, dashboard de métricas
- **Fase 3 (mes 2-3)** — Type hints completos, E2E con Playwright, ADRs, encuesta trimestral

Note:
SPACE — Forsman et al. 2021 — fue diseñado precisamente para resolver el problema de "no sé si mi equipo va bien". Las cinco dimensiones son ortogonales: un equipo puede ser muy productivo (P) y al mismo tiempo estar muy infeliz (S), lo cual es un desastre futuro disfrazado de éxito. La inversión sugerida: 40% quick wins / 35% tooling / 25% métricas.

---

<!-- .slide: class="opener" data-background-image="images/Architectural smells.png" -->

<div class="opener-content">

<span class="eyebrow">Sección 7</span>

# Architectural smells

</div>

Note:
A diferencia de los code smells, los architectural smells afectan la *estructura* del sistema, no funciones individuales. Marco de referencia: Mumtaz, Singh & Blincoe (2020), Journal of Systems and Software. Identificamos 8 smells clasificados en MVC, Dependency y Component.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">§ 7 · 8 architectural smells identificados</div>

## Catálogo AS-01 .. AS-08

<div class="smells-grid">

<div class="smell-card high">
<span class="id">AS-01</span>
<span class="name">Scattered Functionality</span>
<span class="desc">Lógica de autorización duplicada en 5+ puntos. Refactor: `auth_service.is_quiz_author_or_admin(...)`</span>
</div>

<div class="smell-card high">
<span class="id">AS-02</span>
<span class="name">God Component</span>
<span class="desc">`api/quiz.py:nilai()` mezcla parsing, cálculo, BD y respuesta en 40 líneas. Refactor: extract methods.</span>
</div>

<div class="smell-card high">
<span class="id">AS-03</span>
<span class="name">Cyclic Dependency</span>
<span class="desc">`app.db ↔ app.modules.utils` se importan mutuamente. Romper extrayendo Mongo_Utils a su sitio.</span>
</div>

<div class="smell-card med">
<span class="id">AS-04</span>
<span class="name">Abstraction without Decoupling</span>
<span class="desc">`Mongo_Utils.get_db()` retorna tupla `(db, collection)` — todos dependen de la estructura completa.</span>
</div>

<div class="smell-card med">
<span class="id">AS-05</span>
<span class="name">Sloppy Delegation</span>
<span class="desc">Vistas pasan datos crudos a templates sin transformación. Templates terminan con lógica de negocio.</span>
</div>

<div class="smell-card med">
<span class="id">AS-06</span>
<span class="name">Ambiguous Interface</span>
<span class="desc">Endpoints con respuestas heterogéneas: a veces `jsonify`, a veces `abort`, a veces `return 'no'`.</span>
</div>

<div class="smell-card high">
<span class="id">AS-07</span>
<span class="name">Feature Concentration</span>
<span class="desc">El blueprint `api` concentra lógica de auth, quiz, scores y admin. Falta separación por dominio.</span>
</div>

<div class="smell-card med">
<span class="id">AS-08</span>
<span class="name">Implicit Cross-module Dependency</span>
<span class="desc">Templates dependen de `csrf_token` definido implícitamente en HTML padre. Acoplamiento oculto.</span>
</div>

</div>

<small>Marco: Mumtaz, Singh & Blincoe (2020) — Categorías MVC / Dependency / Component. Detalle completo en `ArchitecturalSmells.md`.</small>

Note:
8 smells catalogados, 4 marcados Alta severidad (rojo). El patrón común: el proyecto sigue una arquitectura por capas (Blueprints) pero las capas no tienen fronteras explícitas — vistas hacen el trabajo de servicios, formularios hacen el trabajo de repositorios. La mayoría de los smells son consecuencia de esa difuminación. Los refactors de Sección 2 (service layer) atacan AS-01, AS-02, AS-04, AS-07 simultáneamente. Por eso priorizar la capa de servicios es alto-impacto.

---

<!-- .slide: class="content" -->

<div class="slide-eyebrow">Cierre</div>

## Lo que entregamos · lo que sigue

<div class="two-col">
<div class="col good">

### ✅ Entregado en este análisis

- **Catálogo de 22 code smells** con ubicación file:line
- **12 técnicas de refactorización** con candidatos concretos
- **Matriz de priorización** impacto × esfuerzo
- **84 tests / 90 % cobertura** (de 8 / 5.8 % inicial)
- **3 módulos de test nuevos** en la 2ª intervención
- **Análisis Clean Code & XP** — fortalezas y gaps
- **Análisis DevEx + SPACE** con plan en 3 fases
- **8 architectural smells** catalogados (AS-01..AS-08)

</div>
<div class="col bad">

### → Próximos pasos

- **Quick wins de seguridad** — `SECRET_KEY` desde entorno, fix `before_first_request`
- **Bugs de frontend** — `&` → `&&`, `$.post` → `$.ajax`
- **Service layer** — habilita el resto de refactors
- **`.env.example` + `setup.sh`** — onboarding < 10 min
- **Pre-commit hooks** + **ruff/flake8** — calidad antes de CI
- **Tests E2E con Playwright** — flujos completos
- **ADRs** — documentar decisiones arquitectónicas
- **Migrar a Flask 3.x LTS**

</div>
</div>

Note:
El balance: el análisis está completo y la suite de tests está sólida. Lo que falta es ejecutar los refactors priorizados. La estrategia es atacar los Quick Wins de seguridad primero (1 día), luego service layer (2-3 semanas con TDD), luego DevEx mejorado (Fase 1 de SPACE). El proyecto pasa de "funciona pero es frágil" a "funciona y es modificable con confianza".

---

<!-- .slide: class="closing" -->

# ¡Gracias!

### Anti-Spaghetti-Squad

Jairo Andrés Jiménez · Edgar Ricardo Álvarez · Juliana Briceño Castro

<div class="closing-meta">

📋 **Documento completo:** `Anti-Spaghetti-Squad_CSDT_2026.md`
🏛️ **Architectural smells:** `ArchitecturalSmells.md`
🌐 **Repo:** [github.com/CSDT-ECI/CSDT-2026-quiz-app](https://github.com/CSDT-ECI/CSDT-2026-quiz-app)

CSDT 2026 · Escuela Colombiana de Ingeniería

</div>

Note:
Tiempo para preguntas. Si la audiencia quiere profundizar en algún smell o técnica específica, los documentos detallados (Anti-Spaghetti-Squad_CSDT_2026.md y ArchitecturalSmells.md) tienen el detalle completo con file:line y código.
