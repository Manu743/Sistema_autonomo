# System Improvement Plan — Exploration

## Change: system-improvement-plan
## Project: sistema_autonomo
## Date: 2026-06-07

---

## 1. Codebase Overview

| Attribute | Value |
|---|---|
| Language | Python 3.11 |
| GUI | PyQt5 |
| Database | SQLite (datos.db) |
| Vision | OpenCV + YOLOv5 + ArUco markers |
| Communication | WebSocket (robot commands) + HTTP (ESP32-CAM stream) |
| Reporting | ReportLab + PyMuPDF |
| Dependencies managed | No (equirements.txt absent) |
| Version control | Git (5 commits, single branch) |
| Tests | None |
| Linting/formatting | None |

### Directory Structure (source only)

`
.
├── GUI Login/
│   ├── Loguin.py          # Login window
│   ├── design.ui          # Qt Designer file
│   └── image/             # UI icons
├── Menu/
│   ├── Menu.py            # Main dashboard (1059 lines)
│   ├── Clases.py          # Data classes
│   ├── bd.py              # SQLite database layer (395 lines)
│   ├── datos.py           # Seed data script
│   ├── PDF.py             # PDF viewer window
│   ├── prueba.py          # Map prototype
│   ├── Prototipo.ui       # Qt Designer file
│   ├── mapa.html          # Leaflet map
│   ├── reportes/          # Generated PDFs
│   └── Iconos/            # UI assets
├── Control/
│   ├── Control.py         # Robot control panel (650 lines)
│   ├── Clases.py          # Duplicate of Menu/Clases.py
│   ├── Contro-Manuall.ui  # Qt Designer file
│   └── .venv/             # Virtual environment
├── Nueva carpeta/         # Experimental/spike code
│   ├── control.py         # Alternative controller
│   ├── Manejo_Autonomo.py # Standalone YOLO detection loop
│   ├── sensor.py          # WebSocket sensor listener
│   ├── mensajes.py        # WebSocket message test
│   └── websocket/         # Arduino WebSocket firmware
├── mapas/                 # Area map screenshots
└── openspec/
    ├── config.yaml
    ├── specs/
    └── changes/
`

---

## 2. Complete Issue Inventory

Issues are grouped by type and ordered by severity within each group.

### 🔴 SECURITY (4 issues)

| # | Issue | File(s) | Severity | Detail |
|---|---|---|---|---|
| S1 | **SQL injection — table/column names interpolated** | Menu/bd.py lines 287-288, 304, 316 | CRITICAL | Modificar(), Deshabilitar(), Habilitar() build queries with f-strings: "UPDATE {tabla} SET ... WHERE {condicion} = {id}". Both 	abla and condicion come from caller code and are not parameterized. id is also interpolated directly. |
| S2 | **SQL injection — unreachable but dangerous** | Menu/bd.py line 214 | MEDIUM | First Datos_matriz definition has a hardcoded SQL string comment + a parameterized query; overwritten immediately by second definition — dead code that signals past unsafe practices. |
| S3 | **Password hashing — SHA-256 without salt** | Menu/bd.py line 128, GUI Login/Loguin.py line 84 | MEDIUM | hashlib.sha256(password.encode()).hexdigest() uses raw SHA-256 with no salt, no bcrypt/argon2. Vulnerable to rainbow table attacks. |
| S4 | **Sensitive credentials in source** | Menu/datos.py lines 4-6 | HIGH | Plaintext passwords committed: Manu743_1905, Nat743, Wili743. These are seed data but still exposed. |

### 🏗️ ARCHITECTURE (8 issues)

| # | Issue | File(s) | Severity | Detail |
|---|---|---|---|---|
| A1 | **Module-level YOLO load at import** | Control/Control.py lines 28-31 | CRITICAL | 	orch.hub.load(...) runs at import time. Importing this module downloads/extracts YOLOv5 and loads the model. Also causes pathlib.PosixPath monkey-patch at module level. Blocks startup if model file missing. |
| A2 | **Module-level side effects in multiple files** | Control/Control.py lines 27-37, Nueva carpeta/Manejo_Autonomo.py lines 16-23 | CRITICAL | Monkey-patches (pathlib.PosixPath = pathlib.WindowsPath), model loading, shared mutable state (command_queue, stop_event, grilla_dato) all at module level. |
| A3 | **sys.path.append for cross-module imports** | Menu/Menu.py lines 14-16 | HIGH | sys.path.append hacks for importing Control and PDF modules. Fragile — depends on CWD at runtime. Breaks if launched from different directory. |
| A4 | **Duplicated Clases.py** | Menu/Clases.py and Control/Clases.py | HIGH | Two identical copies of data classes. Divergence risk — any change to one copy won't propagate. |
| A5 | **No separation of concerns — bd.py mixes schema, queries, and seed data comments** | Menu/bd.py | HIGH | Single class does schema creation, CRUD, and has dead methods (er(), er_Datos_Persona_Usuarios(), ista_Matriz()). Schema comments are commands, not config. |
| A6 | **Subprocess-based navigation** | Menu/Menu.py line 153, GUI Login/Loguin.py line 78 | MEDIUM | subprocess.run(["python", "./Menu/Menu.py"]) launches a new Python process instead of using signals/slots for window transitions. Hard to pass state between windows. |
| A7 | **Orphan experimental code** | Nueva carpeta/ | MEDIUM | Contains 6 Python files, 2 UI files, Arduino firmware. Duplicates logic from Control/ and Menu/. No __init__.py, not importable. Likely abandoned spikes. |
| A8 | **No config or environment abstraction** | All files | HIGH | Database path "datos.db", model path "C:/1/bestn.pt", camera calibration path are hardcoded strings. Not configurable via env vars, config files, or CLI args. |

### 🔧 RELIABILITY (10 issues)

| # | Issue | File(s) | Severity | Detail |
|---|---|---|---|---|
| R1 | **Duplicate function definition** | Menu/bd.py lines 209-218 and 221-232 | CRITICAL | Datos_matriz defined twice. Python uses the second definition. The first has different column indexing (i[3], i[4] vs i[4], i[5]) — this is a latent bug that could manifest if the order were reversed. |
| R2 | **conexion.close without parentheses (8 occurrences)** | Menu/bd.py lines 62, 81, 102, 123, 149, 157, 165, 180 | HIGH | conexion.close references the method without calling it. Connections are NEVER closed in these code paths. Causes resource leaks. |
| R3 | **WebSocketClient — no reconnection logic** | Control/Control.py lines 211-277 | HIGH | connect() is called once. If the WebSocket drops, self.connected stays False forever. Commands silently fail (print("WebSocket no conectado")). No exponential backoff, no reconnect. |
| R4 | **Race condition on shared mutable state** | Control/Control.py line 42 | HIGH | grilla_dato = [ [0 for _ in range(5) ] for _ in range(5) ] is module-level mutable state accessed from ecorrer_grilla() (thread target). Multiple VideoWorker instances would corrupt each other's data. |
| R5 | **Bare except:** | Control/Control.py line 634 | HIGH | except: catches everything including SystemExit and KeyboardInterrupt. Masks errors in the ESP32 stream reader. |
| R6 | **Hardcoded absolute paths (3 unique paths)** | Control/Control.py lines 30, 288; Nueva carpeta/Manejo_Autonomo.py line 21; Menu/prueba.py line 36 | HIGH | C:/1/bestn.pt (2x), C:/Users/maren/.../calibracion_camera.npz, C:/Users/maren/.../mapa.html. Breaks on any other machine. |
| R7 | **Temp files without cleanup** | Menu/Menu.py line 961 | MEDIUM | 	emp_{area}.png is created in CWD during PDF generation. Never deleted. Accumulates over time. |
| R8 | **Thread safety — WebSocketClient.send and lock** | Control/Control.py lines 262-272 | MEDIUM | 	ime.sleep(0.5) inside a lock-holding block blocks ALL WebSocket operations for 500ms. Lock is held for the full send+wait duration. |
| R9 | **No timeout on database operations** | Menu/bd.py | MEDIUM | SQLite operations have no timeout. Under concurrent access (unlikely but possible), sqlite3.OperationalError: database is locked would crash. |
| R10 | **Integer division in grid logic may cause off-by-one** | Control/Control.py lines 470-471, 521-525 | LOW | cell_w = w / self.grid_cols and similar may produce float values. Subsequent int() truncation could cause accumulation errors. |

### 🧹 MAINTAINABILITY (10 issues)

| # | Issue | File(s) | Severity | Detail |
|---|---|---|---|---|
| M1 | **No requirements.txt** | Root | HIGH | Cannot reproduce the environment. Dependencies like PyQt5, torch, opencv-python, websocket-client, reportlab, PyMuPDF, pyModbusTCP are undocumented. Version conflicts guaranteed. |
| M2 | **No .gitignore** | Root | HIGH | .venv/, __pycache__/, *.pyc, datos.db, 	emp_*.png, *.pdf are all tracked or cluttering status. |
| M3 | **No README** | Root | MEDIUM | No setup instructions, architecture docs, or usage guide. |
| M4 | **rom Clases import * / rom bd import *** | Menu/Menu.py lines 9, 12 | MEDIUM | Wildcard imports pollute namespace. Unclear which symbols come from where. |
| M5 | **Mixed Spanish/English identifiers** | All files | LOW | Variables like cargarAreas, Nombre_Completo, obtenerIDRobot, Contrase_Usuario. Some English (eload, logout), most Spanish. Inconsistent. |
| M6 | **Duplicate/redundant imports** | Menu/Menu.py lines 1, 2, 8, 11, 18, 19, 21-28 | LOW | Multiple import lines for same modules (eportlab.platypus imported 3 times, QIcon twice). Dead code imports (#from PyQt5.QtGui import QImage). |
| M7 | **Dead code / commented code** | Multiple files | LOW | Many commented-out code blocks, dead methods (d.ver(), d.ver_Datos_Persona_Usuarios(), d.vista_Matriz()), commented seed data calls. |
| M8 | **No logging — print() everywhere** | All files | MEDIUM | Over 50 print() statements. No log levels, no log files, no structured logging. Production debugging impossible. |
| M9 | **No type hints** | All files | MEDIUM | Python 3.11 supports typing, but no annotations exist. Makes refactoring riskier. |
| M10 | **Magic numbers** | Control/Control.py lines 300, 302, 337-356, 369-383 | LOW | Grid size 5, marker length 0.05, threshold 3000, sleep times (0.5s, 2s, 3s) are hardcoded throughout. |

### ⚡ PERFORMANCE (3 issues)

| # | Issue | File(s) | Severity | Detail |
|---|---|---|---|---|
| P1 | **YOLO loaded at import** | Control/Control.py line 30 | HIGH | Model loading blocks the importing thread. ~2-5 seconds of startup delay even if the model is never used immediately. GPU memory allocated permanently. |
| P2 | **No frame rate control in ESP32 stream** | Control/Control.py lines 617-635 | MEDIUM | update_stream() runs a busy loop with no sleep. Saturates the HTTP connection with continuous requests. |
| P3 | **Unbounded list for notifications** | Menu/Menu.py line 1020 | LOW | listView_3 grows without limit. No retention policy. Memory leak over long sessions. |

---

## 3. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Database corruption from unclosed connections (R2) | High | Data loss | Fix close() calls in Phase 1 |
| SQL injection via Deshabilitar/Habilitar (S1) | Medium | Data breach | Parameterize all queries |
| Module import failure on new machine (A1, R6) | High | App won't start | Lazy-load YOLO, use relative paths |
| Silent WebSocket failure stops robot (R3) | High | Robot control lost | Add reconnection with backoff |
| Race condition corrupts grid data (R4) | Medium | Wrong mine locations | Thread-local or synchronized state |
| Subprocess launch fails on non-Windows (A6) | Low | Login broken | Use in-process navigation |
| Dependencies drift (M1) | High | Build failures | Pin dependencies in requirements.txt |

---

## 4. Phased Improvement Plan

### Phase 1: Quick Wins (1-2 days)

| # | Task | Effort | Related Issues |
|---|---|---|---|
| 1.1 | Add .gitignore (Python + PyQt + SQLite + OS) | 15 min | M2 |
| 1.2 | Generate equirements.txt from .venv | 15 min | M1 |
| 1.3 | Fix conexion.close → conexion.close() (8 occurrences) | 15 min | R2 |
| 1.4 | Remove duplicate Datos_matriz — keep the second version | 15 min | R1 |
| 1.5 | Fix bare except: to except Exception: | 10 min | R5 |
| 1.6 | Remove duplicate import lines | 15 min | M6 |
| 1.7 | Remove hardcoded paths from prueba.py (experimental file) | 10 min | R6 |
| 1.8 | Add PyMuPDF to equirements.txt (missing from venv) | 5 min | M1 |
| 1.9 | Add README.md with setup instructions | 1 hr | M3 |
| **Total Phase 1** | **~2-3 hours** | | |

### Phase 2: Architecture (3-5 days)

| # | Task | Effort | Related Issues |
|---|---|---|---|
| 2.1 | **Lazy-load YOLO model** — move 	orch.hub.load into a function, not module level | 2 hr | A1, A2, P1 |
| 2.2 | **Config module** — create config.py with paths, DB name, model path, IPs via env vars + defaults | 3 hr | A8, R6 |
| 2.3 | **Deduplicate Clases.py** — move to shared models/ module, remove both copies | 1 hr | A4 |
| 2.4 | **Eliminate sys.path.append** — restructure imports with proper Python packaging | 2 hr | A3 |
| 2.5 | **Fix SQL injection vectors** — parameterize Modificar, Deshabilitar, Habilitar | 2 hr | S1 |
| 2.6 | **Add WebSocket reconnection** — exponential backoff in WebSocketClient | 3 hr | R3 |
| 2.7 | **Thread-safe grid state** — make grilla_dato instance-level with Lock | 2 hr | R4 |
| 2.8 | **Fix lock contention** — move 	ime.sleep outside the lock in send_command | 1 hr | R8 |
| 2.9 | **Remove Nueva carpeta/** — archive or delete experimental code | 30 min | A7 |
| 2.10 | **Replace subprocess navigation** — use signals/slots or QApplication windows | 3 hr | A6 |
| **Total Phase 2** | **~20 hours** | | |

### Phase 3: Quality & Hardening (4-6 days)

| # | Task | Effort | Related Issues |
|---|---|---|---|
| 3.1 | **Add test framework** — pytest + pytest-qt for UI testing | 4 hr | (new) |
| 3.2 | **Test database layer** — unit tests for all bd.py methods w/ in-memory SQLite | 4 hr | (new) |
| 3.3 | **Test WebSocket client** — mock WebSocket for reconnection tests | 3 hr | R3 |
| 3.4 | **Replace prints with logging** — Python logging module with handlers | 3 hr | M8 |
| 3.5 | **Add type hints** — mypy-friendly annotations across all source files | 6 hr | M9 |
| 3.6 | **Upgrade password hashing** — replace SHA-256 with bcrypt or argon2 | 2 hr | S3 |
| 3.7 | **Remove wildcard imports** — explicit imports only | 2 hr | M4 |
| 3.8 | **Clean dead code** — remove commented blocks, dead methods, unused imports | 3 hr | M7 |
| 3.9 | **Add temp file cleanup** — use 	empfile module or atexit handler | 1 hr | R7 |
| 3.10 | **Add database timeout** — sqlite3.connect(..., timeout=5) | 30 min | R9 |
| 3.11 | **Add notification list cap** — limit listView_3 to last N items | 30 min | P3 |
| 3.12 | **Unify naming conventions** — choose Spanish or English, snake_case consistently | 4 hr | M5 |
| **Total Phase 3** | **~33 hours** | | |

---

## 5. Effort Summary

| Phase | Focus | Hours | Calendar (1 dev) | Risk Reduction |
|---|---|---|---|---|
| Phase 1 | Quick Wins | 2-3 | 1 day | Medium |
| Phase 2 | Architecture | 18-20 | 3-5 days | High |
| Phase 3 | Quality | 30-33 | 4-6 days | Medium |
| **Total** | | **~55 hours** | **~10-12 days** | |

---

## 6. Execution Order Recommendation

`
Phase 1 ──► Phase 2 ──► Phase 3
  │              │
  │              └── 2.1 (Lazy YOLO) is the highest priority in Phase 2
  │                   — unblocks startup on other machines
  │
  └── 1.3, 1.4 are 15-minute fixes that prevent data corruption
`

**Recommended sequencing:**
1. **Phase 1 in full** — immediate risk reduction, low effort
2. **Phase 2 items 2.1, 2.2, 2.5, 2.6 first** — core architectural fixes
3. **Phase 2 items 2.3, 2.4, 2.7, 2.8, 2.9, 2.10 second** — structural cleanup
4. **Phase 3 in dependency order** — tests first, then hardening, then cleanup

---

## 7. Additional Issues Discovered (beyond initial list)

| # | Issue | Found In |
|---|---|---|
| 1 | conexion.close without () — 8 connection leaks | Menu/bd.py |
| 2 | Bare except: swallows SystemExit/KeyboardInterrupt | Control/Control.py |
| 3 | Lock held during 	ime.sleep(0.5) in WebSocket send | Control/Control.py |
| 4 | 3 hardcoded absolute paths (not just YOLO) | Control/Control.py, prueba.py |
| 5 | Race condition on shared grilla_dato | Control/Control.py |
| 6 | Dead code / orphan methods in bd.py | Menu/bd.py |
| 7 | Unbounded notification list | Menu/Menu.py |
| 8 | Temp files never cleaned | Menu/Menu.py |
| 9 | Plaintext passwords in seed data | Menu/datos.py |
| 10 | No config/environment abstraction | All files |
| 11 | No logging framework | All files |
| 12 | No type hints | All files |
| 13 | Magic numbers spread through Control.py | Control/Control.py |
| 14 | SHA-256 without salt for passwords | Menu/bd.py, Loguin.py |
| 15 | No database timeout configured | Menu/bd.py |
