#!/bin/bash

# Abre una nueva terminal y ejecuta redis-server
gnome-terminal -- bash -c "redis-server; exec bash"

# Abre una nueva terminal y ejecuta Server.py con Python 3
gnome-terminal -- bash -c "python3 Server.py; exec bash"
