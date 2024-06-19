#!/bin/bash

# Abre tres nuevas terminales y ejecuta terminal.py con Python 3
gnome-terminal -- bash -c "python3 terminal.py; exec bash"
gnome-terminal -- bash -c "python3 terminal.py; exec bash"
gnome-terminal -- bash -c "python3 terminal.py; exec bash"
