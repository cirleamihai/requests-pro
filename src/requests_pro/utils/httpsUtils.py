import random
import socket

CHARLES_CONFIGURATION = ('127.0.0.1', 8888, 0.005)


def is_charles_running():
    return is_ip_port_taken(*CHARLES_CONFIGURATION)


def is_ip_port_taken(host, port, timeout=0.01):
    """Check if Charles Proxy is running by attempting to connect to the given host and port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def get_random_available_port(start=1024, end=49151) -> int:
    """
    Get a random available port on the machine.
    """
    while True:
        port = random.randint(start, end)
        if not is_ip_port_taken(host='127.0.0.1', port=port):
            return port
