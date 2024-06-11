import subprocess


subprocess.Popen(['gnome-terminal', '--', 'redis-server'])
subprocess.Popen(['gnome-terminal', '--', 'python3', 'Server.py'])