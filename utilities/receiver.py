# receiver.py
import numpy as np
import time
from utilities.communication import Communicator
from utilities.plotter import RealTimeChaosPlotter
from utilities.lorenz import ChaoticSystem

class Receiver:
    def __init__(self, port=12346):
        self.comm = Communicator(port=port, is_sender=False)
        self.system = ChaoticSystem(system_type='receiver')
        self.decoded_buffer = []
        self.plotter = RealTimeChaosPlotter()
        self.dt = 0.001
        self.sync_threshold = 1e-4

    def _adaptive_sync(self):
        """Paper's continuous synchronization from Section 3"""
        print("[RECEIVER] Starting adaptive synchronization...")
        error_buffer = []
        
        while True:
            received_state, _ = self.comm.receive()
            if received_state is None:
                continue
            
            error = received_state - self.system.state
            error_buffer.append(np.linalg.norm(error))
            
            # Apply Lyapunov control
            self.system.continuous_step(
                error_signal=error[0],  # x-component feedback
                dt=self.dt
            )
            
        
            # Dynamic stability check
            if len(error_buffer) > 100:
                ma_error = np.mean(error_buffer[-100:])
                if ma_error < self.sync_threshold:
                    print(f"Synchronized (MAE: {ma_error:.2e})")
                    return True
                elif ma_error > 1e-2:  # Paper's resync condition
                    print("Resetting synchronization...")
                    self.system.state = np.array([0.1, 0.11, 0.12])
                    error_buffer.clear()


    def _decode_messages(self):
        """Paper's message recovery s_r = v - w"""
        print("[RECEIVER] Starting message decoding...")
        try:
            while True:
                masked_state, true_state = self.comm.receive()
                if masked_state is not None:
                    s_r = masked_state[0] - self.system.state[0]
                    decoded_char = self._scale_to_char(s_r)
                    self.decoded_buffer.append(decoded_char)
                    
                    error = masked_state - self.system.state

                    self.system.continuous_step(
                        error_signal=error[0],
                        dt=self.dt
                    )

                    self.plotter.update(
                        receiver_state=self.system.state.copy(),
                        perturb_value=s_r,
                        error=np.linalg.norm(masked_state - self.system.state),
                        message=decoded_char
                    )


        except KeyboardInterrupt:
            self.plotter.save_animation()
            print(f"\nFINAL MESSAGE: {''.join(self.decoded_buffer)}")
        finally:
            self.comm.close()


    def _scale_to_char(self, value):
        """Paper's I₀=3.9 scaling from Section 4"""
        scaled = value / (0.25/95)  # 0.25V max / 95 ASCII chars
        return chr(max(32, min(127, int(np.round(scaled + 32)))))

    def run(self):
        if self._adaptive_sync():
            self._decode_messages()
