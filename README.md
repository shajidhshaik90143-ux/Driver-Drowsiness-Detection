# Driver Drowsiness Detection System

A complete real-time Python computer-vision project that monitors a driver's face through a webcam and detects possible drowsiness using:

- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR) for yawning
- Consecutive closed-eye frames
- Yawn duration/count
- Drowsiness score
- Audible alarm
- Event logging to CSV
- Live dashboard with status, metrics, FPS and event history
- Automatic screenshot capture when a drowsiness event is triggered

## Project Structure

```text
Driver_Drowsiness_Detection/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── config.py
├── src/
│   ├── __init__.py
│   ├── detector.py
│   ├── metrics.py
│   ├── alarm.py
│   ├── logger.py
│   └── utils.py
├── assets/
│   └── README.txt
├── models/
│   └── README.txt
└── logs/
    └── README.txt
```

## Requirements

- Python 3.10–3.13 recommended
- Webcam
- Windows/Linux/macOS
- Good front-facing lighting

> Python 3.14 may not have wheels available for every computer-vision dependency. If installation fails on Python 3.14, use Python 3.12.

## Installation

### Windows

```powershell
cd Driver_Drowsiness_Detection
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/macOS

```bash
cd Driver_Drowsiness_Detection
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

The application opens your default webcam.

Controls:

- `Q` = quit
- `R` = reset counters/state
- `S` = save a screenshot manually

## Detection Logic

The system uses facial landmarks from MediaPipe Face Mesh.

### Eye Aspect Ratio

For an eye with six landmark points:

```text
EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
```

When the EAR stays below the configured threshold for enough consecutive frames, the system marks the eyes as closed.

### Mouth Aspect Ratio

MAR is calculated from mouth landmarks. A sustained high MAR is treated as a possible yawn.

### Drowsiness Event

An alert is triggered when:

1. Eyes remain closed longer than the configured duration, OR
2. A high drowsiness score is maintained for enough frames.

The system also considers yawning as supporting evidence rather than relying on one noisy frame.

## Configuration

Edit `config.py` to tune thresholds for your camera/environment.

Important parameters:

- `EAR_THRESHOLD`
- `EYE_CLOSED_SECONDS`
- `MAR_THRESHOLD`
- `YAWN_SECONDS`
- `ALARM_COOLDOWN_SECONDS`
- `CAMERA_INDEX`

If false alerts occur, increase `EAR_THRESHOLD` carefully or increase `EYE_CLOSED_SECONDS`.

If the system misses closed eyes, increase `EAR_THRESHOLD` slightly.

## Logs

Drowsiness events are stored in:

```text
logs/drowsiness_events.csv
```

Screenshots from alert events are stored in:

```text
logs/events/
```

## Resume Description

**Driver Drowsiness Detection System — Python, OpenCV, MediaPipe**

Developed a real-time computer-vision safety application that detects driver drowsiness from webcam video using facial landmarks, Eye Aspect Ratio (EAR), Mouth Aspect Ratio (MAR), temporal thresholds, alert scoring, audible alarms, event logging, and automatic evidence screenshots. Designed configurable detection logic and a live monitoring dashboard with FPS and driver-status indicators.

## Notes

This is an educational/prototype system. It should not be treated as a certified automotive safety system. Camera angle, lighting, glasses, occlusion, face position, and individual facial characteristics can affect accuracy.
