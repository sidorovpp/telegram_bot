import subprocess

cmd = [['sudo', 'docker', 'container', 'stop', 'telegram-bot'],
       ['sudo', 'docker', 'container', 'rm', 'telegram-bot'],
       ['sudo', 'docker', 'image', 'rm', 'telegram-bot'],
       ['sudo', 'docker', 'build', '--tag=telegram-bot', '.'],
       ['sudo', 'docker', 'run', '-d', '--network', 'host', '--restart=always', '--name=telegram-bot', 'telegram-bot']]
for cmd1 in cmd:
    subprocess.call(cmd1)
