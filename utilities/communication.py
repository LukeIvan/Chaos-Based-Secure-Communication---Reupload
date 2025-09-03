# communication.py
import socket
import pickle
import numpy as np
import time

class Communicator:
    def __init__(self, port, is_sender):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.is_sender = is_sender
        
        if not is_sender:
            self.sock.bind(('', port))
            self.sock.settimeout(0.1)


    def send(self, state, true_state=None, dest='localhost:12346'):
        """Correct parameter order maintained"""
        ip, port = dest.split(':')
        packet = pickle.dumps({
            'state': state.astype(np.float32).tolist(),
            'true_state': true_state.astype(np.float32).tolist() 
                        if true_state is not None else None,
            'timestamp': time.time_ns()
        })
        self.sock.sendto(packet, (ip, int(port)))


    def receive(self):
        try:
            data, _ = self.sock.recvfrom(4096)
            packet = pickle.loads(data)
            return (
                np.array(packet['state'], dtype=np.float64),
                np.array(packet['true_state'], dtype=np.float64) 
                if packet['true_state'] is not None else None
            )
        except (socket.timeout, pickle.UnpicklingError):
            return None, None

    def close(self):
        self.sock.close()
