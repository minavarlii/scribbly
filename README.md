# Scribbly

Scribbly is a real-time, gesture-based whiteboard built with Python.  
It allows users to draw on the screen using their index finger, powered by live hand tracking from a standard webcam.

The project is designed as a lightweight visual aid that can be screen-shared during online meetings, without requiring a tablet, stylus, or additional hardware.

## Motivation

Visual explanations during online meetings are often difficult without a tablet or stylus. Switching between tools or setting up additional software can interrupt the flow of discussion.

Scribbly was built to provide a simple alternative: a camera-based whiteboard that allows quick, informal drawing using natural finger movements.

## Features

- Real-time hand tracking using a webcam  
- Drawing with the index finger  
- Multiple drawing colors  
- Adjustable brush size  
- Erase mode  
- Stroke-based undo and redo  
- Hover-activated UI controls to reduce accidental input

## Testing & Quality Assurance

The project includes unit tests for deterministic core components such as stroke history handling and internal state management.

Due to the real-time and camera-dependent nature of hand tracking, testing focuses on logic that can be validated reliably without hardware input.

Tests are written using pytest and are designed to:
- validate correct stroke recording and undo/redo behavior
- ensure predictable state transitions
- reduce the risk of regressions in core drawing functionality

## Requirements

To run Scribbly, you need:

- **Python 3.10 or newer**
- A working **webcam**
- macOS, Linux, or Windows

### Python dependencies

The following Python libraries are required:

- **OpenCV (`opencv-python`)** – camera access and drawing  
- **MediaPipe** – real-time hand tracking  
- **NumPy** – image and numerical operations  

All dependencies are listed in `requirements.txt`.

## Installation

Create and activate a virtual environment, then install dependencies:

## Running the project

After installing the required dependencies, start Scribbly by running the following command from the project root:

`bash`

python3 src/main.py

A window will open showing the camera feed and drawing interface. You can draw by pointing your index finger at the screen.

Press Q at any time to close the application.

## Testing

The project includes unit tests for the core logic and stroke history handling. These tests focus on deterministic components of the system rather than camera input.

To run the tests, use:
pytest

## Intended use

Scribbly is designed to be run locally and used via screen sharing during online meetings such as Zoom, Microsoft Teams, or Google Meet. It does not require any plugins, browser extensions, or system-level integrations.

## Tech stack
	•	Python
	•	OpenCV
	•	MediaPipe
	•	NumPy
	•	pytest



