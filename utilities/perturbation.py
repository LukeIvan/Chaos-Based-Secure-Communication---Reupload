# perturbation.py
import numpy as np

class PerturbationEncoder:
    MAX_AMPLITUDE = 0.25  # From paper's I₀=3.9 scaling (Fig 9)
    SCALE_FACTOR = MAX_AMPLITUDE / 95  # 95 ASCII chars (32-127)

    @classmethod
    def encode(cls, char):
        scaled = (ord(char) - 32) * cls.SCALE_FACTOR
        return np.array([scaled, 0.0, 0.0], dtype=np.float32)

class PerturbationDecoder:
    @classmethod
    def decode(cls, perturbation):
        scaled = perturbation[0] / PerturbationEncoder.SCALE_FACTOR + 32
        return chr(max(32, min(127, int(np.round(scaled)))))
