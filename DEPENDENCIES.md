# Dependency List

## Python Runtime

- Python 3.12
- `venv` module
- `pip`

## Python Package Dependencies

Defined in [requirements.txt](</home/thirdwing/crucible/obsidian-vault/ai-workspace/projects/GLKVM APP/requirements.txt>):

- `PySide6>=6.8,<7`

`PySide6` pulls in:
- `PySide6_Essentials`
- `PySide6_Addons`
- `shiboken6`

## Ubuntu System Packages

Required or recommended on Ubuntu 24:

- `python3`
- `python3-venv`
- `python3-pip`
- `libxcb-cursor0`

Install with:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip libxcb-cursor0
```

## Generated App Dependencies

Each generated GLKVM launcher app creates and uses its own private virtual environment and installs:

- `PySide6>=6.8,<7`

This is why generated apps remain functional even if the main builder folder is later removed.
