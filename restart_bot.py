import subprocess
import sys

screen_output = subprocess.run(["screen", "-ls"], stdout=subprocess.PIPE).stdout.decode('utf-8')
screen_process = screen_output.split("\n")[1].split()[0]
subprocess.run(["screen", "-XS", screen_process, "quit"])
subprocess.run(["screen", "-dm", "python", "bot.py", "prod"])
