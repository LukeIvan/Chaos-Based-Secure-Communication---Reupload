# lorenz.py
import numpy as np

class ChaoticSystem:
    def __init__(self, system_type='transmitter'):
        # Paper's EXACT parameters from Section 3 Example
        self.alpha = 6.3       # R/L1 ratio = 0.1/0.0159 
        self.beta = 0.7        # R/L2 ratio = 0.1/0.1429
        self.gamma = 7         # 1/L2 = 1/0.1429
        self.a = -1.143        # Ra/R = -0.1143/0.1
        self.b = -0.714        # Rb/R = -0.0714/0.1
        self.I0 = 3.9          # Critical breakpoint from Fig 9
        self.L = np.array([1, -7, 0])  # Theorem 1 gains
        
        # Paper's exact initial conditions
        self.state = np.array([0.1, 0.11, 0.12], dtype=np.float64)
        self.system_type = system_type

    def nonlinear_func(self, x):
        """Implementation of Eq. (14) piecewise-linear function"""
        return self.b*x + 0.5*(self.a-self.b)*(
            np.abs(x + self.I0) - np.abs(x - self.I0)
        )

    def continuous_step(self, error_signal=0, dt=0.001):
        """Paper's continuous dynamics with time scaling t=6349.2τ"""
        x, y, z = self.state
        
        # Scaled time step from paper's circuit implementation
        scaled_dt = dt / 6349.2
        
        # Original dynamics from Eqs. 15-17
        dx = -self.alpha*(x + y + self.nonlinear_func(x))
        dy = -self.beta*(x + y) - self.gamma*z
        dz = y
        
        # Lyapunov control injection
        if self.system_type == 'receiver':
            dx += self.L[0] * error_signal
            dy += self.L[1] * error_signal
            dz += self.L[2] * error_signal
        
        # Scaled Euler integration
        self.state += np.array([dx, dy, dz]) * scaled_dt
        return self.state.copy()
