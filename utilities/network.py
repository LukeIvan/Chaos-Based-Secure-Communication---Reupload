import socket
import pickle

class UDPConnection:
    def __init__(self, host='localhost', port=12345, is_sender=False):
        self.host = host
        self.port = port
        self.is_sender = is_sender
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if not is_sender:
            self.sock.bind((self.host, self.port))

    def send(self, data, dest_ip, dest_port):
        """Sends serialized Lorenz state data."""
        packet = pickle.dumps(data)
        self.sock.sendto(packet, (dest_ip, dest_port))

    def receive(self):
        """Receives data and returns deserialized Lorenz state."""
        data, _ = self.sock.recvfrom(1024)
        return pickle.loads(data)

    def close(self):
        self.sock.close()
