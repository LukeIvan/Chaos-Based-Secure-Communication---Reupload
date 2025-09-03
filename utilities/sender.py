# sender.py
import time
import numpy as np
from utilities.communication import Communicator
from utilities.perturbation import PerturbationEncoder
from utilities.lorenz import ChaoticSystem

class SecureSender:
    def __init__(self, dest_port=12346):
        self.comm = Communicator(port=12345, is_sender=True)
        self.system = ChaoticSystem(system_type='transmitter')
        self.dest = f"localhost:{dest_port}"
        self.sync_interval = 10  # Paper's 10:1 sync-to-message ratio
        self.dt = 0.001

    def _synchronization_preamble(self):
        """Paper's 500-1000 step initialization"""
        print("[SENDER] Transmitting sync preamble...")
        for _ in range(1000):
            true_state = self.system.continuous_step(dt=self.dt)
            self.comm.send(state=true_state, true_state=true_state, dest=self.dest)
            time.sleep(self.dt)


    def _encode_message(self, message):
        """Paper's signal masking from Section 3"""
        encoded = []
        true_states = [] 
        
        for char in message:
            perturb = PerturbationEncoder.encode(char)
            true_state = self.system.continuous_step(dt=self.dt)
            true_states.append(true_state.copy())  # Save true state
            
            masked_state = true_state.copy()
            masked_state[0] += perturb[0]  # v = x₁ + s
            encoded.append(masked_state)
        
        return encoded, true_states


    def run(self):
        self._synchronization_preamble()
        print("[SENDER] Ready for message input")
        sync_counter = 0
        try:
            while True:
                # Background sync transmission
                if sync_counter % self.sync_interval == 0:
                    state = self.system.continuous_step(dt=self.dt)
                    self.comm.send(state,true_state=state, dest=self.dest)  # Fixed here
                    
                # Message handling
                message = input("Enter message (or press Enter): ")
                if message:
                    encoded_states, true_states = self._encode_message(message)
                    for i, state in enumerate(encoded_states):
                        # Include both true_state and dest parameters
                        self.comm.send(
                            state=state,
                            true_state=true_states[i],  # Actual chaotic state
                            dest=self.dest
                        )
                        sync_counter += 1
                        time.sleep(0.001)

                
        except KeyboardInterrupt:
            pass
        finally:
            self.comm.close()
