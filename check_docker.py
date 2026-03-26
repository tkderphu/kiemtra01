import subprocess

# get ps
ps_out = subprocess.getoutput('docker ps -a')
names = []
for line in ps_out.split('\n'):
    if 'laptop-service' in line:
        parts = line.split()
        names.append(parts[-1]) # container name is usually last

log_out = ''
for name in names:
    log_out += f"\n\n--- Logs for {name} ---\n"
    log_out += subprocess.getoutput(f'docker logs {name}')

with open('docker_logs_dump.txt', 'w') as f:
    f.write(ps_out + '\n' + log_out)
