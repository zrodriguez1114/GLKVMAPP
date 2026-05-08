# GLKVM App Builder

GLKVM App Builder is a Ubuntu 24 desktop utility that creates standalone GLKVM viewer applications from a name, an IP address, and an output directory.

The builder application generates:
- A dedicated launcher folder for each saved GLKVM
- A standalone Python desktop app for that GLKVM
- A local `viewer.html` wrapper
- A `.desktop` launcher entry for Ubuntu application search
- A private virtual environment inside the generated app folder

## Features

- Modern dark desktop interface
- Name, IP address, and output location fields
- One-click `Save and Create` generation flow
- Standalone generated apps that keep working after the builder is removed
- Refresh button in the generated GLKVM window
- Ubuntu application-search integration through `.desktop` launchers

## Requirements

- Ubuntu 24 LTS
- Python 3.12 or compatible Python 3
- `python3-venv`
- `pip`
- `libxcb-cursor0` for X11 Qt runtime support

## Setup

```bash
cd '/path/to/GLKVM APP'
./setup_glkvmapp.sh
```

If your system reports that the Qt `xcb` plugin could not be initialized:

```bash
sudo apt update
sudo apt install libxcb-cursor0
```

## Run

```bash
./run_glkvmapp.sh
```

On Wayland sessions, the launcher prefers Wayland automatically.

## How To Use

1. Enter a KVM name.
2. Enter the GLKVM IP address or URL.
3. Enter an output folder path.
4. Click `Save and Create`.

The generated launcher folder will be created inside the chosen output directory, and a matching `.desktop` file will be installed into:

```text
~/.local/share/applications/
```

## Generated App Layout

Each created GLKVM app folder contains:

```text
app.py
viewer.html
icon.svg
run_glkvm.sh
requirements.txt
venv/
<name>.desktop
```

## Dependencies

See [DEPENDENCIES.md](</home/thirdwing/crucible/obsidian-vault/ai-workspace/projects/GLKVM APP/DEPENDENCIES.md>) for the Python and system dependency list.

## GitHub Upload Notes

- Do not commit `.venv/`
- Do not commit `__pycache__/`
- Do not commit generated GLKVM output folders from your Desktop or other output paths
- Commit `GLKVMAPP.py`, `requirements.txt`, `setup_glkvmapp.sh`, `run_glkvmapp.sh`, `README.md`, `DEPENDENCIES.md`, and `.gitignore`
