import subprocess

subprocess.run(["systemctl", "start", "redis.service"])
subprocess.run(["screen", "-dm", "python3.8", "bot.py", "prod"])
