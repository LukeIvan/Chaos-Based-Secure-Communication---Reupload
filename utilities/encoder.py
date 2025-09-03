class TextEncoder:
    def __init__(self, scale=0.001):
        self.scale = scale  # Scale factor for perturbations

    def encode(self, text):
        """Encodes text into perturbations for Lorenz initialization."""
        return [(ord(char) - 32) * self.scale for char in text]

    def decode(self, perturbations):
        """Decodes received perturbations back into text."""
        return ''.join(chr(int(p / self.scale) + 32) for p in perturbations)
