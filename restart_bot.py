import subprocess

screen_output = subprocess.run(["screen", "-ls"], stdout=subprocess.PIPE).stdout.decode('utf-8')
screen_processes = [i.split()[0].split(".")[0] for i in screen_output.split("\n")[1:-3]]
screen_processes = sorted(screen_processes)

for process in screen_processes:
    subprocess.run(["screen", "-XS", process, "quit"])

subprocess.run(["systemctl", "restart", "redis.service"])
subprocess.run(["screen", "-dm", "python3.8", "bot.py", "prod"])
