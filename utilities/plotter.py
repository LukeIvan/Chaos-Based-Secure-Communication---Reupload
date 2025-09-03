# plotter.py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from collections import deque
import time

class RealTimeChaosPlotter:
    def __init__(self):
        plt.ion()
        self.fig = plt.figure(figsize=(16, 10))
        self.last_update_time = time.time()
        self.setup_plots()
        self.init_data()
        
    def setup_plots(self):
        """Configure optimized layout with improved statistics"""
        gs = GridSpec(3, 3, figure=self.fig, height_ratios=[2, 1, 1])
        
        # Improved Perturbation Plot (now in top position)
        self.ax_perturb = self.fig.add_subplot(gs[0, :2])
        self.ax_perturb.set_title("Message Perturbations (Last 30 Characters)")
        self.ax_perturb.set_ylabel("Perturbation Magnitude")
        self.ax_perturb.grid(True, alpha=0.3)
        
        # Synchronization Error Plot
        self.ax_error = self.fig.add_subplot(gs[1, :2])
        self.ax_error.set_title("Synchronization Error")
        self.ax_error.set_xlabel("Time Steps")
        self.ax_error.set_ylabel("Error (log)")
        self.ax_error.set_yscale('log')
        self.ax_error.grid(True, alpha=0.3)
        
        # Stats & Message Panel
        self.ax_stats = self.fig.add_subplot(gs[0, 2])
        self.ax_stats.set_title("System Statistics")
        self.ax_stats.axis('off')
        
        # Message Display (now larger)
        self.ax_msg = self.fig.add_subplot(gs[1:, 2])
        self.ax_msg.set_title("Decoded Message")
        self.ax_msg.axis('off')

        
    def init_data(self):
        """Initialize plot elements and data buffers"""
        # Phase space plot elements
        # self.phase_scatter = self.ax_phase.scatter([], [], c='blue', s=2, alpha=0.5)
        # self.current_point = self.ax_phase.scatter([], [], c='red', s=50, marker='x')
        
        # Perturbation markers and annotations
        self.perturb_scatter = self.ax_perturb.scatter([], [], c='red', s=30, alpha=0.7)
        self.perturb_annotations = []
        
        # Error line
        self.error_line, = self.ax_error.plot([], [], 'k-', lw=1)
        
        # Message and stats text
        self.stats_text = self.ax_stats.text(0.05, 0.95, "", transform=self.ax_stats.transAxes,
                                            va='top', fontsize=9, fontfamily='monospace')
        self.msg_text = self.ax_msg.text(0.05, 0.95, "", transform=self.ax_msg.transAxes,
                                        va='top', wrap=True, fontsize=11)
        
        # Data buffers with appropriate sizes
        self.window_size = 1000
        self.trail_size = 100  # Number of points to show in phase trail
        self.rx_values = deque(maxlen=self.window_size)
        self.ry_values = deque(maxlen=self.window_size)
        self.error_values = deque(maxlen=self.window_size)
        self.perturb_times = []
        self.perturb_values = []
        self.messages = []
        
        # Statistics tracking
        self.sync_quality = 0
        self.sync_stability = []
        self.message_rate = 0
        self.total_chars = 0
        self.decode_start_time = time.time()
        
    def update(self, receiver_state, perturb_value, error, message):
        """Main update method with improved statistics"""
        # Process new data - now storing both X and Y components
        self.rx_values.append(receiver_state[0])
        # self.ry_values.append(receiver_state[1])
        self.error_values.append(error)
        
        # Track perturbations with proper positioning
        if message is not None:
            self.perturb_times.append(len(self.rx_values) - 1)
            self.perturb_values.append(perturb_value)
            self.messages.append(message)
            self.total_chars += 1
        
        # Calculate statistics
        self.update_statistics(error)
        
        # Update all plots
        # self.update_phase_plot()  # New phase plot update
        self.update_perturbation_plot()
        self.update_error_plot()
        self.update_message_display()
        self.update_stats_display()
        
        # Control update rate to prevent excessive redraws
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:  # Max 10 FPS
            plt.pause(0.001)
            self.last_update_time = current_time
    
    def update_phase_plot(self):
        """Update phase space visualization (X vs Y components)"""
        if len(self.rx_values) > 1 and len(self.ry_values) > 1:
            # Get last trail_size points for phase trail
            x_trail = list(self.rx_values)[-self.trail_size:]
            y_trail = list(self.ry_values)[-self.trail_size:]
            
            # Update trail line
            self.phase_line.set_data(x_trail, y_trail)
            
            # Update scatter plot for all points
            x_data = list(self.rx_values)
            y_data = list(self.ry_values)
            self.phase_scatter.set_offsets(np.column_stack((x_data, y_data)))
            
            # Update current point marker
            self.current_point.set_offsets(np.array([[x_trail[-1], y_trail[-1]]]))
            
            # Dynamically adjust limits
            x_min, x_max = min(x_data), max(x_data)
            y_min, y_max = min(y_data), max(y_data)
            
            # Set equal aspect ratio for true phase space visualization
            x_range = x_max - x_min
            y_range = y_max - y_min
            max_range = max(x_range, y_range)
            
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            
            self.ax_phase.set_xlim(x_center - max_range/1.8, x_center + max_range/1.8)
            self.ax_phase.set_ylim(y_center - max_range/1.8, y_center + max_range/1.8)
            
            # Update title with component ranges
            self.ax_phase.set_title(f"Phase Space (X: {x_min:.6f} to {x_max:.6f}, Y: {y_min:.6f} to {y_max:.6f})")
    
    def update_statistics(self, error):
        """Calculate enhanced system statistics"""
        # Sync quality - exponential moving average of log error
        alpha = 0.05  # EMA factor
        log_error = np.log10(max(error, 1e-10))
        self.sync_quality = (1-alpha) * self.sync_quality + alpha * (-log_error)
        self.sync_stability.append(error)
        if len(self.sync_stability) > 100:
            self.sync_stability.pop(0)
            
        # Message rate (chars per second)
        elapsed = max(1, time.time() - self.decode_start_time)
        self.message_rate = self.total_chars / elapsed
        
    def update_perturbation_plot(self):
        """Show only the last 30 non-space characters in perturbation plot"""
        # Clear previous annotations
        for ann in self.perturb_annotations:
            ann.remove()
        self.perturb_annotations = []
        
        if not self.perturb_times:
            return
            
        # Filter out spaces and get only last 30 characters
        non_space_indices = [i for i, msg in enumerate(self.messages) if msg != ' ']
        last_30_indices = non_space_indices[-30:] if len(non_space_indices) > 0 else []
        
        if not last_30_indices:
            return
        
        # Get plot data for these indices
        plot_times = [self.perturb_times[i] for i in last_30_indices]
        plot_values = [self.perturb_values[i] for i in last_30_indices]
        plot_msgs = [self.messages[i] for i in last_30_indices]
        
        # Update scatter plot with filtered data
        self.perturb_scatter.set_offsets(np.column_stack((plot_times, plot_values)))
        
        # Focus x-axis on where perturbations actually exist
        if plot_times:
            first_perturb = min(plot_times)
            last_perturb = max(plot_times)
            padding = max(10, (last_perturb - first_perturb) * 0.05)
            self.ax_perturb.set_xlim(first_perturb - padding, last_perturb + padding)
        
        # Add character annotations for all points
        for i in range(len(plot_times)):
            x, y = plot_times[i], plot_values[i]
            msg = plot_msgs[i]
            
            # Create styled annotation box
            ann = self.ax_perturb.annotate(
                msg, xy=(x, y), xytext=(0, 10), textcoords='offset points',
                ha='center', va='bottom', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
            )
            self.perturb_annotations.append(ann)
        
        # Scale y-axis for perturbations
        if plot_values:
            y_min, y_max = min(plot_values), max(plot_values)
            padding = max(0.0001, (y_max - y_min) * 0.2)
            self.ax_perturb.set_ylim(y_min - padding, y_max + padding)
    
    def update_error_plot(self):
        """Update error visualization with improved formatting"""
        x = np.arange(len(self.error_values))
        self.error_line.set_data(x, self.error_values)
        
        self.ax_error.set_xlim(max(0, len(self.error_values) - self.window_size), 
                              max(self.window_size, len(self.error_values)))
                              
        if self.error_values:
            # Set appropriate log scale limits
            self.ax_error.set_ylim(
                max(1e-10, min(self.error_values) * 0.1),
                max(1e-2, max(self.error_values) * 2)
            )
    
    def update_stats_display(self):
        """Enhanced statistics panel"""
        # Calculate stability metrics
        stability = np.std(self.sync_stability) if self.sync_stability else 0
        recent_errors = list(self.error_values)[-100:] if self.error_values else [0]
        
        stats = [
            f"Sync Quality:   {max(0, min(10, self.sync_quality)):.2f}/10",
            f"Error (mean):   {np.mean(recent_errors):.2e}",
            f"Error (min):    {min(recent_errors):.2e}",
            f"Stability:      {stability:.2e}",
            f"Message Rate:   {self.message_rate:.2f} char/sec",
            f"Total Decoded:  {self.total_chars} chars",
            f"Runtime:        {time.time() - self.decode_start_time:.1f} sec",
            f"Window Size:    {self.window_size} steps",
            f"Data Points:    {len(self.rx_values)}"
        ]
        
        self.stats_text.set_text("\n".join(stats))
    
    def update_message_display(self):
        """Display spaces properly in the decoded message box"""
        recent_messages = self.messages[-100:]
        decoded_text = "".join(recent_messages)
            
        # Add message stats
        header = f"LATEST DECODED TEXT ({len(self.messages)} chars):\n"
        formatted = header + decoded_text
            
        self.msg_text.set_text(formatted)
