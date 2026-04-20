<div align="center">

```
 ██████╗ ███████╗██████╗ ████████╗    ██████╗  ██████╗ ██████╗  ██████╗
██╔════╝ ██╔════╝██╔══██╗╚══██╔══╝    ╚════██╗██╔═████╗╚════██╗██╔════╝
██║      ███████╗██║  ██║   ██║        █████╔╝██║██╔██║ █████╔╝███████╗
██║      ╚════██║██║  ██║   ██║       ██╔═══╝ ████╔╝██║██╔═══╝ ██╔═══██╗
╚██████╗ ███████║██████╔╝   ██║       ███████╗╚██████╔╝███████╗╚██████╔╝
 ╚═════╝ ╚══════╝╚═════╝    ╚═╝       ╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝
```

# Primera Entrega — Quiz App

### Calidad de Software y Deuda Técnica

**Equipo**: Anti-Spaghetti-Squad | **Fecha**: Marzo 2026

| Integrante |
| :--------- |
| Jairo Andrés Jimenez |
| Edgar Ricardo Alvarez |
| Juliana Briceño Castro |

---

*Repositorio*: [github.com/CSDT-ECI/CSDT-2026-quiz-app](https://github.com/CSDT-ECI/CSDT-2026-quiz-app)

</div>

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#-1-resumen-ejecutivo)
2. [Análisis de Deuda Técnica — Código](#-2-análisis-de-deuda-técnica--código)
3. [Deuda Técnica en Pruebas](#-3-deuda-técnica-en-pruebas)
4. [Modelos de Calidad — Análisis con Herramientas](#-4-modelos-de-calidad--análisis-con-herramientas)
5. [Clean Code y Prácticas XP](#-5-clean-code-y-prácticas-xp)
6. [Conclusiones y Lecciones Aprendidas](#-6-conclusiones-y-lecciones-aprendidas)

> **Bitácora completa**: [Anti-Spaghetti-Squad_CSDT_2026.md](./Anti-Spaghetti-Squad_CSDT_2026.md)
>
> **Dashboard SonarCloud**: [sonarcloud.io/project/overview?id=CSDT-ECI_CSDT-2026-quiz-app](https://sonarcloud.io/project/overview?id=CSDT-ECI_CSDT-2026-quiz-app)
>
> **Repositorio**: [github.com/CSDT-ECI/CSDT-2026-quiz-app](https://github.com/CSDT-ECI/CSDT-2026-quiz-app)

---

## 📌 1. Resumen Ejecutivo

Este documento consolida el trabajo realizado durante el curso de **Calidad de Software y Deuda Técnica (CSDT) 2026** sobre el proyecto **Quiz App**, una aplicación web construida con Flask y MongoDB que permite crear, compartir y responder quizzes en línea.

```
┌─────────────────────────────────────────────────────────────┐
│                    LÍNEA DE TRABAJO                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1] Olores de código y malas prácticas                     │
│       └──► 8 categorías, 25+ problemas documentados        │
│                                                             │
│  [2] Técnicas de refactorización                            │
│       └──► 12 técnicas propuestas con candidatos concretos  │
│                                                             │
│  [3] Clean Code y prácticas XP                              │
│       └──► 7 prácticas cumplidas, 8 incumplidas             │
│       └──► 9 prácticas XP evaluadas y priorizadas           │
│                                                             │
│  [4] Deuda técnica en pruebas                               │
│       └──► Cobertura: 5.8% → 64% → 90%                     │
│                                                             │
│  [5] Modelos de calidad                                     │
│       └──► SonarCloud + herramientas complementarias con IA │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 2. Análisis de Deuda Técnica — Código

Se identificaron **25+ problemas** agrupados en 8 categorías:

| Categoría | Severidad |
| :-------- | :-------: |
| Configuración y seguridad | 🔴 Alta |
| Estructura y responsabilidades | 🟡 Media |
| Consistencia y nomenclatura | 🟡 Media |
| Código muerto e imports | 🟢 Baja |
| Lógica de negocio y vistas | 🟡 Media |
| Persistencia y recursos | 🟡 Media |
| Frontend (JavaScript) | 🔴 Alta |
| Otros (Content-Type, herencia de formularios) | 🟡 Media |

Se propusieron **12 técnicas de refactorización** priorizadas por impacto y esfuerzo, incluyendo: extracción de constantes, creación de capa de servicios, helpers de autorización, configuración de seguridad por entorno y centralización de manejo de errores.

---

## 🧪 3. Deuda Técnica en Pruebas

### 3.1 Diagnóstico inicial

El proyecto contaba con **8 smoke tests** que solo verificaban códigos HTTP sin validar lógica, datos ni seguridad. La cobertura era de **5.8%** en líneas y **0%** en branches.

Se identificaron 7 tipos de testing debt en la primera revisión:

| Tipo de deuda | Resumen |
| :------------ | :------ |
| Tests ausentes para lógica crítica | Cálculo de puntajes, autenticación y permisos sin verificar |
| Tests superficiales | Solo `assert status_code == 200`, sin validar comportamiento |
| Funciones puras sin tests | Funciones deterministas y fácilmente testeables ignoradas |
| Seguridad sin verificar | Decoradores de autenticación sin cobertura |
| Edge cases ignorados | Sin tests para inputs inválidos o errores |
| Branches sin cubrir | 0% de ramas condicionales ejecutadas |
| Infraestructura de test rota | `conftest.py` con bug que impedía crear la app en tests |

Tras la primera intervención se elevó la cobertura a **70.54%**. El análisis posterior de la suite resultante reveló **5 prácticas adicionales de testing debt**:

| Tipo de deuda (segunda revisión) | Resumen |
| :-------------------------------- | :------ |
| **Tests con estado compartido** | `registered_user` (autouse) contamina tests que usan el mismo username, causando fallos dependientes del orden de ejecución |
| **`dashboard/views.py` sin cobertura** | Vistas de edición, eliminación, logout y descarga nunca ejecutadas en tests (46.94% cobertura) |
| **Flujos de carga de archivos sin cobertura** | Endpoint `uploadCsv` (CSV y JSON) con 0% de cobertura a pesar de aceptar entrada de usuario no confiable |
| **Operaciones de administración sin tests** | `manage_users` (delete/promote/unpromote) sin ningún test de integración |
| **Branches de autorización sin cubrir** | La rama `abort(403)` en `edit_quiz` nunca se ejecutaba; autorización sin verificación de caminos de rechazo |

### 3.2 Intervenciones

#### Primera intervención — 37 tests nuevos (4 módulos)

| Módulo | Tests | Alcance |
| :----- | :---: | :------ |
| `test_utils.py` | 14 | Funciones puras: generación de códigos, hashing, serialización |
| `test_decorators.py` | 4 | Decoradores de autenticación y autorización |
| `test_api_views.py` | 9 | Endpoints de usuario: registro, login, perfil |
| `test_api_quiz.py` | 10 | Endpoints de quiz: creación, preguntas, puntajes |

#### Segunda intervención — 39 tests nuevos (3 módulos)

| Módulo | Tests | Alcance |
| :----- | :---: | :------ |
| `test_dashboard_views.py` | 18 | Vistas de dashboard: edición/eliminación de quiz, autorización por rol, logout |
| `test_upload_csv.py` | 8 | Carga de archivos CSV y JSON con validación de formato y extensión |
| `test_api_admin.py` | 13 | Operaciones de admin, cambio de contraseña, edición de perfil, flujos de error |

### 3.3 Resultados

```
INICIAL           1ª INTERVENCIÓN          2ª INTERVENCIÓN
═══════           ═══════════════          ═══════════════

Tests:     8      Tests:     45  (+462%)   Tests:     84  (+950%)
Líneas:    5.8%   Líneas:    70%           Líneas:    90%  ██████████████████░░
Branches:  0.0%   Branches:  30%           Branches:  ~84% █████████████████░░░
```

---

## 📊 4. Modelos de Calidad — Análisis con Herramientas

### 4.1 SonarCloud

El proyecto tiene **SonarCloud** integrado mediante GitHub Actions, ejecutando análisis estático y reportando cobertura en cada push y PR hacia `main`.

SonarCloud evalúa la calidad según el modelo **SQALE**, alineado con **ISO/IEC 25010**:

| Dimensión | Métrica | Qué evalúa |
| :-------- | :------ | :---------- |
| Fiabilidad | Bugs | Defectos que causan comportamiento incorrecto |
| Seguridad | Vulnerabilities | Debilidades explotables por atacantes |
| Mantenibilidad | Code Smells | Problemas que dificultan la modificación del código |
| Mantenibilidad | Technical Debt | Tiempo estimado para resolver code smells |
| Mantenibilidad | Duplications | Código repetido |
| Fiabilidad | Coverage | Código cubierto por tests |

El **Quality Gate** por defecto ("Sonar way") exige cobertura ≥80% en código nuevo, duplicaciones ≤3%, y ratings A en fiabilidad, seguridad y mantenibilidad.

---

### 4.2 Herramientas complementarias con IA

Se analizaron herramientas modernas que incorporan inteligencia artificial para complementar el análisis de SonarCloud:

| Herramienta | Enfoque principal | Diferenciador con IA |
| :---------- | :---------------- | :------------------- |
| **Codacy** | Revisión automática multi-lenguaje | ML para priorizar issues y detectar patrones OWASP |
| **DeepSource** | Análisis estático + auto-fix | Genera correcciones automáticas con modelos de lenguaje |
| **CodeClimate** | Mantenibilidad y deuda técnica | Predicción de "hotspots" basada en historial de cambios |

```
                    SonarCloud  Codacy   DeepSource  CodeClimate
                    ──────────  ──────   ──────────  ───────────
Análisis estático      ✅        ✅        ✅          ✅
Cobertura              ✅        ✅        ✅          ✅
Multi-lenguaje         🟡        ✅        ✅          ✅
Auto-fix con IA        ❌        🟡        ✅          ❌
Análisis de seguridad  ✅        ✅        ✅          🟡
Hotspot prediction     ❌        ❌        ❌          ✅
Gratuito (open source) ✅        ✅        ✅          ✅
```

**Recomendación**: Mantener **SonarCloud** como herramienta principal y complementar con **DeepSource** para auto-fix de issues comunes y **CodeClimate** para monitoreo de mantenibilidad.

---

### 4.3 ISO/IEC 25010 aplicado al proyecto

| Característica | Estado general | Observaciones |
| :------------- | :------------: | :------------ |
| Adecuación funcional | 🟡 | Funcionalidad completa, pero con typos y inconsistencias en endpoints |
| Eficiencia de desempeño | 🟡 | Archivos cargados en memoria sin límite de tamaño |
| Compatibilidad | ✅ | API REST estándar con JSON |
| Usabilidad | 🔴 | Mensajes de error inconsistentes, sin feedback en fallos AJAX |
| Fiabilidad | 🔴 | Bugs en JS, baja cobertura de branches |
| Seguridad | 🔴 | SECRET_KEY volátil, excepciones expuestas al cliente |
| Mantenibilidad | 🟡 | Buena modularidad con Blueprints, pero sin capa de servicios ni DRY |
| Portabilidad | 🟡 | Configuración por entorno existe pero no se aprovecha completamente |

---

## 🧼 5. Clean Code y Prácticas XP

### Clean Code

| | Cumple | No cumple |
| :--- | :----: | :-------: |
| Prácticas generales | 7 | 8 |
| Principios SOLID | 0 | 5 |
| Otros principios (DRY, KISS, etc.) | 0 | 6 |

**Lo bueno**: Blueprints, decoradores, formularios declarativos, funciones pequeñas, configuración centralizada, CSRF, templates organizados.

**Lo pendiente**: Nombres inconsistentes, funciones con múltiples responsabilidades, código muerto, números mágicos, manejo de errores disperso.

### Prácticas XP

| Prioridad | Práctica | Estado |
| :-------: | :------- | :----: |
| 🔴 | TDD / Tests | Parcialmente implementado (90% cobertura líneas) |
| 🔴 | Integración Continua | Implementado (GitHub Actions + SonarCloud) |
| 🟡 | Estándares de codificación | Pendiente |
| 🟡 | Refactoring continuo | Planificado |
| 🟢 | Pair Programming | Recomendado |
| 🟢 | Diseño Simple | Guía para futuro |

---

## 💡 6. Conclusiones y Lecciones Aprendidas

1. **La testing debt bloquea todo lo demás** — Sin tests no se puede refactorizar con seguridad. Crear la base de tests fue el primer paso obligatorio antes de cualquier mejora.

2. **Los smoke tests dan falsa confianza** — Verificar que un endpoint retorna 200 no es verificar que funciona. Los tests deben validar comportamiento y lógica de negocio.

3. **Empezar por las funciones puras** — Las funciones sin dependencias externas son el punto de entrada ideal para construir una cultura de testing en un proyecto sin tests.

4. **Las herramientas de análisis estático complementan pero no reemplazan los tests** — SonarCloud detecta code smells y vulnerabilidades, pero solo los tests verifican que la lógica es correcta.

5. **La infraestructura de testing también es código** — Un bug en `conftest.py` puede invalidar toda la suite de tests silenciosamente.

### Métricas de impacto

```
INDICADOR                  ANTES          1ª ENTREGA     2ª ENTREGA
─────────────────────────────────────────────────────────────────────
Tests                      8              45             84
Cobertura de líneas        5.8%           70.54%         90%
Cobertura de branches      0%             29.59%         ~84%
Testing debt identificada  0              7 tipos        12 tipos
Problemas documentados     0              25+            25+
Refactorings planificados  0              12             12
CI/CD pipeline             No             GitHub Actions + SonarCloud
```

---

<div align="center">

**Anti-Spaghetti-Squad** · CSDT 2026 · Escuela Colombiana de Ingeniería

*"El código limpio no es el que se escribe bien la primera vez, sino el que se mejora continuamente."*

</div>
