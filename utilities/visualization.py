import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.sender_line, = self.ax.plot([], [], 'r-', label='Sender')
        self.receiver_line, = self.ax.plot([], [], 'b-', label='Receiver')
        self.ax.legend()
        self.ax.set_xlim(-30, 30)
        self.ax.set_ylim(-30, 30)
        plt.ion()  # interactive mode on
        plt.show()

    def update(self, sender_state, receiver_state):
        # Wrap scalar values in lists.
        self.sender_line.set_data([sender_state[0]], [sender_state[1]])
        self.receiver_line.set_data([receiver_state[0]], [receiver_state[1]])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
