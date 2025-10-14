# **ELEMTRIX (Telemetry Data GUI)**

Python-based telemetry framework for **acquisition, parsing, and visualization** of live data over a serial interface.  
Architecture: **Backend (Flask/Serial/Parser/SQLAlchemy – optional DB)** serves live JSON; **Frontend (Dash/Plotly)** renders it in real time.

---

## Repository Structure

```text
/ (repo root)
├─ Gui.py                 ← Dash/Plotly GUI (port 8050); polls backend `/incoming_data`
├─ serial_reader02.py     ← Alternative/legacy backend (Flask + Serial) 
├─ Reader.py              ← Primary backend: Flask (8024) + Serial + Parser + Logging + (optional) DB
├─ einlese_test.py        ← Test/prototype reader
├─ animationView.py       ← Matplotlib animation from JSON logs (`logs/telemetry.log`)  not finished yet
├─ driver_input_msg_can.csv
├─ electrical_msg_can.csv
├─ error_msg_can.csv
├─ info_msg_can.csv
├─ temperature_msg_can.csv
├─ ObjectList.csv
└─ README.md
```

**Runtime paths (created/used at runtime):**
```text
logs/telemetry.log   ← JSON lines (one measurement per line)
telemetry.db         ← If SQLite is used (code can also target MySQL when enabled)
```

---

## Data Flow

1. **Serial → Parser** (`serial_reader02.py`)
   - `serial_port = "COM3"` (Linux/macOS: `/dev/ttyUSB0` / `/dev/ttyACM0`)
   - `baudrate = 115200`
   - **CSV signal maps** (CAN-like): `Name`, `Startbit`, `Length [Bit]`, `Factor`, `Offset`, …
   - ID → CSV mapping:
     - `420` → `error_msg_can.csv`
     - `421` → `info_msg_can.csv`
     - `422` → `temperature_msg_can.csv`
     - `423` → `driver_input_msg_can.csv`
     - `424` → `electrical_msg_can.csv`
   - Bit-slice → int → scale with `Factor`/`Offset`
   - Result stored in `latest_data` and appended to `logs/telemetry.log`

2. **Backend (Flask)**
   - Endpoint: `GET /incoming_data` → `jsonify(latest_data)`
   - Optional persistence via **SQLAlchemy** (e.g., MySQL or SQLite)  
     (typical tables: `Apps`, `Speed`, `Temperature`, `Inverter`, `Errors`)

3. **Frontend (Dash/Plotly, `Gui.py`)**
   - Polls `http://127.0.0.1:8024/incoming_data` ≈ every 500 ms
   - Plots: speed, SOC, currents/voltages, throttle/brake, motor/inverter temperatures
   - Status indicators for `error_*` signals

---

## API Contract

```text
GET /incoming_data
Content-Type: application/json

Response: { "<signal_name>": "<value_as_string>", ... }

Example:
{
  "speed": "31.25",
  "info_soc": "64.00",
  "voltage_left_inverter": "400.00",
  "error_imd": "0.00",
  ...
}
```

*Keys come from the CSV `Name` column. Values are already scaled and formatted.*

---

## Rules

- **Do not modify**
  - Stable parser contracts/data objects in `serial_reader02.py`
  - Public GUI APIs/components in `Gui.py`

- **Work only in your assigned module**
  - If you work on **GUI**, don’t change serial/parser internals
  - If you work on **serial/parser**, don’t change UI layout/threading

- **All commits must**
  - Run locally (backend responds; GUI starts cleanly)
  - Be small, single-purpose diffs
  - Contain no secrets or absolute local paths

---

## Branch & Contribution Policy

- `main` is protected — **never** push directly to it  
- Always use **feature branches** + **Pull Requests**


**Each PR must**
- Touch **one** logical module (GUI **or** Serial/Parser)
- Run locally (backend JSON OK; GUI renders without errors)
- Keep diffs minimal and clear
- Target Python **3.8+**

---

## Prerequisites

- **Python** 3.8+
- **Packages**:
  ```bash
  pip install dash plotly pandas requests flask sqlalchemy pyserial mysql-connector-python matplotlib numpy
  ```
  > On Linux, install `tkinter` if needed:
  > ```bash
  > sudo apt install python3-tk
  > ```

- **MySQL** only if DB persistence is enabled (running server + user/database)

---

## Configuration

**Serial** (in `serial_reader02.py` / variants):
```python
serial_port = "COM3"       # Linux/macOS: /dev/ttyUSB0 or /dev/ttyACM0
baudrate    = 115200
```

**Database (SQLAlchemy, e.g., MySQL)**:
```python
connection_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
```

Prefer environment variables / `.env` (do not hard-code credentials).

---

## Quickstart

```bash
# 1) (recommended) virtual environment
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt  # or the pip line from Prerequisites

# 3) Start backend (Flask + Serial + Parser)
python serial_reader02.py
# -> http://127.0.0.1:8024

# 4) Start GUI (Dash)
python Gui.py
# -> open http://127.0.0.1:8050
```

**Smoke test the API**
```bash
curl http://127.0.0.1:8024/incoming_data
```

---

## Troubleshooting

- **Port busy / permission denied**
  - Close other serial tools (IDE monitors, etc.)
  - Linux: `sudo usermod -a -G dialout $USER` (re-login)
    temporary: `sudo chmod 666 /dev/ttyUSB0`

- **Blank GUI / no values**
  - Is backend up? `curl 127.0.0.1:8024/incoming_data`
  - Check serial port/baudrate and CSV map ↔ ID match

- **GUI freezes**
  - Ensure serial reads **do not** block the UI thread (use a worker thread + queue)

