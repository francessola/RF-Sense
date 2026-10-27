import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow,
                             QWidget, QVBoxLayout, QLabel,
                             QPushButton, QHBoxLayout, QSpinBox,
                             QDoubleSpinBox, QFrame, QGridLayout)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.fft import rfft, rfftfreq
from pathlib import Path
from PyQt6.QtCore import QTimer

# Locate RF-Sense project directory 
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import interference detection functions
from src.interference_detector import (detect_peaks, classify_frequency)
from src.signal_generator import generate_signal
from src.noise_simulator import generate_noise
from src.spectrum_analyzer import analyze_spectrum

class RFSenseWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Random generators for static and live analysis
        self.static_rng_seed = 42
        self.live_rng = np.random.default_rng()

        # Track elapsed simulated time in Live Mode
        self.live_time = 0.0

        # Rolling buffer for live signal analysis
        self.live_buffer = np.array([])
        self.live_buffer_size = 1000

        # Spectrum Waterfall history
        self.waterfall_history = []
        self.waterfall_max_rows = 100

        # Common frequency grid for Waterfall
        self.waterfall_frequencies = np.linspace(0,100,201)

        # Track the sample rate used by the live buffer
        self.previous_sample_rate = None

        # Timer for simulated live signal updates
        self.live_timer = QTimer(self)
        self.live_timer.setInterval(200)

        # Update the signal whenever the timer fires
        self.live_timer.timeout.connect(self.analyze_signal)

        self.setWindowTitle("RF-Sense | Signal Analysis")
        self.resize(1000,650)

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main window background
        central_widget.setObjectName("mainBackground")
        central_widget.setStyleSheet("""
                QWidget#mainBackground {
                    background-color: #0B111B;
                    }
                    """)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Header layout
        header_layout = QHBoxLayout()

        # Application header
        title = QLabel("RF-Sense")
        title.setStyleSheet("""
            color: #E6EDF3;
            font-size: 26px;
            font-weight: bold;
            padding-top: 8px;
        """)

        description = QLabel("  RF-Signal Analysis & Interference Detection")
        description.setStyleSheet("""
            color: #AAB8C8;
            font-size: 12px;
        """)

        # Add title to header
        header_layout.addWidget(title)

        # Push status indicator to the right
        header_layout.addStretch()

        # Mode status indicator
        self.mode_indicator = QLabel("● STATIC MODE")
        self.mode_indicator.setStyleSheet("""
                QLabel {
                background-color: #202A36;
                color: #AAB8C8;
                border: 1px solid #39495A;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: bold;
                }
        """)

        # Add indicator to header
        header_layout.addWidget(self.mode_indicator)

        # Add header to main layout
        layout.addLayout(header_layout)
        layout.addWidget(description)

        #Signal configuration
        config_layout = QHBoxLayout()

        # Frequency
        frequency_label = QLabel("Frequency (Hz):")
        self.frequency_input = QDoubleSpinBox()
        self.frequency_input.setRange(1.0, 400.0)
        self.frequency_input.setValue(10.0)

        # Amplitude
        amplitude_label = QLabel("Amplitude:")
        self.amplitude_input = QDoubleSpinBox()
        self.amplitude_input.setRange(0.0, 10.0)
        self.amplitude_input.setValue(1.0)

        # Sample rate
        sample_rate_label = QLabel("Sample Rate (Hz):")
        self.sample_rate_input = QSpinBox()
        self.sample_rate_input.setRange(100, 10000)
        self.sample_rate_input.setValue(1000)

        # Noise level
        noise_label = QLabel("Noise Level:")

        self.noise_input = QDoubleSpinBox()
        self.noise_input.setRange(0.0, 5.0)
        self.noise_input.setSingleStep(0.1)
        self.noise_input.setDecimals(2)
        self.noise_input.setValue(0.3)

        # Interference frequency
        interference_label = QLabel("Interference Frequency (Hz):")

        self.interference_frequency_input = QDoubleSpinBox()
        self.interference_frequency_input.setRange(1.0, 400.0)
        self.interference_frequency_input.setDecimals(1)
        self.interference_frequency_input.setSingleStep(1.0)
        self.interference_frequency_input.setValue(30.0)

        # Interference amplitude 
        interference_amplitude_label = QLabel("Interference Amplitude:")

        self.interference_amplitude_input = QDoubleSpinBox()
        self.interference_amplitude_input.setRange(0.0,10.0)
        self.interference_amplitude_input.setDecimals(2)
        self.interference_amplitude_input.setSingleStep(0.1)
        self.interference_amplitude_input.setValue(0.8)

        # Add controls to horizontal layout
        config_layout.addWidget(frequency_label)
        config_layout.addWidget(self.frequency_input)

        config_layout.addWidget(amplitude_label)
        config_layout.addWidget(self.amplitude_input)

        config_layout.addWidget(sample_rate_label)
        config_layout.addWidget(self.sample_rate_input)

        config_layout.addWidget(noise_label)
        config_layout.addWidget(self.noise_input)

        config_layout.addWidget(interference_label)
        config_layout.addWidget(self.interference_frequency_input)

        config_layout.addWidget(interference_amplitude_label)
        config_layout.addWidget(self.interference_amplitude_input)

        # Style signal configuration inputs
        input_style = """
            QSpinBox, QDoubleSpinBox {
                background-color: #202A36;
                color: #E6EDF3;
                border: 1px solid #39495A;
                border-radius: 6px;
                padding: 5px 8px;
                min-height: 22px;
            }

            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #4DB8FF;
            }

            QSpinBox:hover, QDoubleSpinBox:hover {
                background-color: #2B3949;
            }
        """

        for input_widget in [
            self.frequency_input,
            self.amplitude_input,
            self.sample_rate_input,
            self.noise_input,
            self.interference_frequency_input,
            self.interference_amplitude_input
        ]:
            input_widget.setStyleSheet(input_style)
        
        # Add configuration layout to main layout
        layout.addLayout(config_layout)

        # Button layout
        button_layout = QHBoxLayout()

        # Buttons
        self.analyze_button = QPushButton("Analyze Signal")
        self.analyze_button.clicked.connect(self.analyze_signal)
        clear_button = QPushButton("Clear Results")
        clear_button.clicked.connect(self.clear_results)

        # Add buttons to horizontal layout
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(clear_button)

        # Live Mode buttons
        self.start_live_button = QPushButton("Start Live")
        self.stop_live_button = QPushButton("Stop Live")

        # Stop is unavailable until Live Mode starts
        self.stop_live_button.setEnabled(False)

        button_layout.addWidget(self.start_live_button)
        button_layout.addWidget(self.stop_live_button)

        # Connect Live Mode buttons
        self.start_live_button.clicked.connect(self.start_live)
        self.stop_live_button.clicked.connect(self.stop_live)

        # Primary action button
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #2563A6;
                color: #FFFFFF;
                border: 1px solid #3B82D0;
                border-radius: 8px;
                padding: 9px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #3278C4;
            }

            QPushButton:pressed {
                background-color: #1B4D85;
            }

            QPushButton:disabled {
                background-color: #20242B;
                color: #687482;
                border: 1px solid #2B333D;
                }
        """)

        # Secondary action buttons
        secondary_button_style = """
            QPushButton {
                background-color: #202A36;
                color: #E6EDF3;
                border: 1px solid #39495A;
                border-radius: 8px;
                padding: 9px;
            }

            QPushButton:hover {
                background-color: #2B3949;
            }

            QPushButton:pressed {
                background-color: #18222E;
            }

            QPushButton:disabled {
                background-color: #20242B;
                color: #687482;
                border: 1px solid #2B333D;
            }
        """     

        clear_button.setStyleSheet(secondary_button_style)
        self.start_live_button.setStyleSheet(secondary_button_style)
        self.stop_live_button.setStyleSheet(secondary_button_style)

        # Add horizontal layout to main layout
        layout.addLayout(button_layout)

        # Dark theme colors
        self.bg_color = "#151B23"
        self.text_color = "#E6EDF3"
        self.grid_color = "#303B49"

        # Create separate figures for each graph
        self.time_figure = Figure(figsize=(8,3), facecolor=self.bg_color)
        self.fft_figure = Figure(figsize=(8,3), facecolor=self.bg_color)

        # Create Waterfall figure
        self.waterfall_figure = Figure(figsize=(8,3), facecolor=self.bg_color)
        self.waterfall_canvas = FigureCanvasQTAgg(self.waterfall_figure)
        self.waterfall_ax = self.waterfall_figure.add_subplot(111)

        # Create separate canvases
        self.time_canvas = FigureCanvasQTAgg(self.time_figure)
        self.fft_canvas = FigureCanvasQTAgg(self.fft_figure)

        # Create axes
        self.time_ax = self.time_figure.add_subplot(111)
        self.fft_ax = self.fft_figure.add_subplot(111)

        # Configure dark plot appearance
        for ax in [self.time_ax, self.fft_ax, self.waterfall_ax]:
            ax.set_facecolor(self.bg_color)
            ax.tick_params(colors=self.text_color)

            ax.xaxis.label.set_color(self.text_color)
            ax.yaxis.label.set_color(self.text_color)
            ax.title.set_color(self.text_color) 

            for spine in ax.spines.values():
                spine.set_color(self.grid_color)

            ax.grid(
                True,
                color=self.grid_color,
                linestyle="--",
                alpha=0.5
            )

        # Create reusable plot lines
        self.time_line, = self.time_ax.plot([], [], color="#4DB8FF")
        self.fft_line, = self.fft_ax.plot([], [], color="#4DB8FF")

        # Configure plot titles and labels
        self.time_ax.set_title("Time Domain Signal")
        self.time_ax.set_xlabel("Time (s)")
        self.time_ax.set_ylabel("Amplitude")

        self.fft_ax.set_title("Frequency Spectrum (FFT)")
        self.fft_ax.set_xlabel("Frequency (Hz)")
        self.fft_ax.set_ylabel("Amplitude")

        self.waterfall_ax.set_title("Spectrum Waterfall")
        self.waterfall_ax.set_xlabel("Frequency (Hz)")
        self.waterfall_ax.set_ylabel("Time History")

        # Leave room for plot titles and axis labels
        self.time_figure.subplots_adjust(
        left=0.09, right=0.97, top=0.85, bottom=0.22
        )
        self.fft_figure.subplots_adjust(
        left=0.09, right=0.97, top=0.85, bottom=0.22
        )
        self.waterfall_figure.subplots_adjust(
            left=0.09,
            right=0.97,
            top=0.85,
            bottom=0.22
        )

        # Create rounded cards
        self.time_card = QFrame()
        self.fft_card = QFrame()
        self.waterfall_card = QFrame()

        for card in [self.time_card, self.fft_card, self.waterfall_card]:
            card.setObjectName("plotCard")
            card.setStyleSheet("""
            QFrame#plotCard {
            background-color: #151B23;
            border: 1px solid #303B49;
            border-radius: 12px;
            }
            """)

        # Put each canvas inside its own card
        time_card_layout = QVBoxLayout(self.time_card)
        time_card_layout.setContentsMargins(12,12,12,12)
        time_card_layout.addWidget(self.time_canvas)

        fft_card_layout = QVBoxLayout(self.fft_card)
        fft_card_layout.setContentsMargins(12,12,12,12)
        fft_card_layout.addWidget(self.fft_canvas)

        waterfall_card_layout = QVBoxLayout(self.waterfall_card)
        waterfall_card_layout.setContentsMargins(12,12,12,12)
        waterfall_card_layout.addWidget(self.waterfall_canvas)

        # Prevent canvas widgets from displaying their own borders
        self.time_canvas.setStyleSheet(
            "background-color: #151B23; border: none;"
        )
        self.fft_canvas.setStyleSheet(
            "background-color: #151B23; border: none;"
        )
        self.waterfall_canvas.setStyleSheet(
            "background-color: #151B23; border: none;"
        )

        # Results card
        self.results_card = QFrame()
        self.results_card.setObjectName("resultsCard")

        self.results_card.setStyleSheet("""
            QFrame#resultsCard {
                background-color: #151B23;
                border: 1px solid #303B49;
                border-radius: 12px;
            }
        """)

        # Layout inside the card
        results_layout = QVBoxLayout(self.results_card)
        results_layout.setContentsMargins(20, 14, 20, 14)
        results_layout.setSpacing(8)

        # Results title
        results_title = QLabel("Analysis Results")
        results_title.setStyleSheet("""
            color: #E6EDF3;
            font-size: 15px;
            font-weight: bold;
            border: none;
        """)

        # Results text
        self.results_label = QLabel("No analysis performed yet.")
        self.results_label.setStyleSheet("""
            color: #AAB8C8;
            font-size: 12px;
            border: none;
        """)

        self.results_label.setWordWrap(True)

        # Keep results at the top of the card
        results_layout.addWidget(results_title)
        results_layout.addWidget(self.results_label)

        # Prevent results tect from stretching vertically
        results_layout.addStretch()

        # Dashboard grid layout
        dashboard_grid = QGridLayout()
        dashboard_grid.setSpacing(12)

        # Remove previous fixes height restriction
        self.waterfall_card.setMinimumHeight(0)
        self.waterfall_card.setMaximumHeight(16777215)

        # Organize dashboard cards
        dashboard_grid.addWidget(self.time_card, 0,0)
        dashboard_grid.addWidget(self.fft_card, 0,1)
        dashboard_grid.addWidget(self.waterfall_card, 1,0)
        dashboard_grid.addWidget(self.results_card, 1,1)

        # Even space distributed
        dashboard_grid.setRowStretch(0,1)
        dashboard_grid.setRowStretch(1,1)
        dashboard_grid.setColumnStretch(0,1)
        dashboard_grid.setColumnStretch(1,1)

        # Add dashboard to main layout
        layout.addLayout(dashboard_grid, 1)

    def analyze_signal(self):
        # Clear old Waterfall during Static Analysis
        if not self.live_timer.isActive():
            self.waterfall_history = []

            self.waterfall_ax.clear()
            self.waterfall_ax.set_facecolor(self.bg_color)

            self.waterfall_ax.set_title("Spectrum Waterfall", color=self.text_color)
            self.waterfall_ax.set_xlabel("Frequency (Hz)", color=self.text_color)
            self.waterfall_ax.set_ylabel("History (s)", color=self.text_color)

            self.waterfall_ax.tick_params(colors=self.text_color)
            self.waterfall_ax.set_xlim(0,100)
            self.waterfall_ax.grid(False)
            self.waterfall_canvas.draw_idle()

        # Read signal parameters
        frequency = self.frequency_input.value()
        amplitude = self.amplitude_input.value()
        sample_rate = self.sample_rate_input.value()
        noise_level = self.noise_input.value()
        interference_frequency = self.interference_frequency_input.value()
        interference_amplitude = self.interference_amplitude_input.value()

        # Select signal duration based on analysis mode
        if self.live_timer.isActive():
            duration = 0.2
            time = np.arange(0, duration, 1 / sample_rate) + self.live_time
            self.live_time += duration
        else:
            duration = 1.0
            time = np.arange(0, duration, 1 / sample_rate)

        # Generate expected signal using the backend
        _, expected_signal = generate_signal(frequency, amplitude, sample_rate, duration,
                                             start_time=self.live_time - duration if self.live_timer.isActive() else 0.0)

        # Keep the generated signal aligned with Live Mode time
        if self.live_timer.isActive():
            expected_signal = amplitude + np.sin(2 * np.pi * frequency * time)

        # Simulated interference 
        interference = interference_amplitude * np.sin(2 * np.pi * interference_frequency * time)

        # Select the random generator based on analysis mode
        if self.live_timer.isActive():
            rng = self.live_rng
        else:
            rng = np.random.default_rng(self.static_rng_seed)

        # Generate Gaussian noise using the backend
        noise = generate_noise(noise_level, len(time), rng)

        # Combined signal
        signal = expected_signal + interference + noise

        # Update rolling buffer during Live Mode
        if self.live_timer.isActive():

            # Reset buffer when sample rate changes
            if self.previous_sample_rate != sample_rate:
                self.live_buffer = np.array([])
                self.previous_sample_rate = sample_rate

            # Keep approximately one second of samples
            self.live_buffer_size = sample_rate

            # Add new samples to the buffer
            self.live_buffer = np.concatenate((self.live_buffer, signal))

            # Keep only the most recent samples
            self.live_buffer = self.live_buffer[-self.live_buffer_size:]

        # Select the signal used for FFT analysis
        if self.live_timer.isActive():
            fft_signal = self.live_buffer
        else:
            fft_signal = signal

        # Analyze frequency spectrum using the backend
        fft_frequencies, fft_amplitudes = analyze_spectrum(fft_signal, sample_rate)

        # Save spectrum history for Waterfall
        if self.live_timer.isActive():

            # Interpolate FFT onto a consistent frequency grid
            waterfall_spectrum = np.interp(
                self.waterfall_frequencies,
                fft_frequencies,
                fft_amplitudes
            )
            self.waterfall_history.append(waterfall_spectrum)

            # Keep only the most recent spectra
            if len(self.waterfall_history) > self.waterfall_max_rows:
                self.waterfall_history.pop(0)

        # Calculate adaptive threshold
        noise_floor = np.median(fft_amplitudes[1:])
        threshold = 5 * noise_floor

        # Detect frequency peaks
        peaks = detect_peaks(fft_amplitudes, threshold)

        # Classify detected frequencies
        detected_signals = []

        for peak in peaks:
            detected_frequency = fft_frequencies[peak]
            detected_amplitude = fft_amplitudes[peak]

            classification = classify_frequency(detected_frequency, frequency, 1.0)
            detected_signals.append((detected_frequency, detected_amplitude, classification))

        # Update the existing time-domain line
        self.time_line.set_data(time, signal)

        # Adjust axes to the updated signal
        self.time_ax.relim()

        # Re-enable vertical autoscaling
        self.time_ax.set_autoscaley_on(True)
        self.time_ax.autoscale_view(scalex=False, scaley=True)

        # Set the time range 
        self.time_ax.set_xlim(time[0], time[-1])

        # Restore title and labels
        self.time_ax.set_title("Time Domain Signal")
        self.time_ax.set_xlabel("Time (s)")
        self.time_ax.set_ylabel("Amplitude")

        # Update the existing frequency-domain line
        self.fft_line.set_data(fft_frequencies, fft_amplitudes)

        # Adjust FFT axes
        self.fft_ax.relim()
        self.fft_ax.autoscale_view()

        # Display the frequency range of interest
        self.fft_ax.set_xlim(0,100)

        # Keep the FFT amplitude scale stable during Live Mode
        if self.live_timer.isActive():
            max_amplitude = max(1.0, amplitude + interference_amplitude + 0.5)
            self.fft_ax.set_ylim(0, max_amplitude)

        # Remove markers from the previous analysis
        for marker in self.fft_ax.collections[:]:
            marker.remove()

        # Highlight and classify detected peaks
        for peak in peaks:
            detected_frequency = fft_frequencies[peak]
            detected_amplitude = fft_amplitudes[peak]

            classification = classify_frequency(detected_frequency, frequency, 1.0)

            if classification == "Expected Signal":
                color = "green"
            else:
                color = "red"

            self.fft_ax.scatter(
                detected_frequency,
                detected_amplitude,
                color=color,
                marker="x",
                s=70
            )

        self.fft_ax.set_title("Frequency Spectrum (FFT)")
        self.fft_ax.set_xlabel("Frequency (Hz)")
        self.fft_ax.set_ylabel("Amplitude")

        # Focus on the first 100 Hz
        self.fft_ax.set_xlim(0, 100)

        # Update Spectrum Waterfall
        if self.live_timer.isActive() and self.waterfall_history:
            waterfall_data = np.array(self.waterfall_history)
            self.waterfall_ax.clear()
            self.waterfall_ax.imshow(
                waterfall_data,
                aspect="auto",
                origin="lower",
                extent=[0,100,0,len(self.waterfall_history) * 0.2],
                cmap="inferno",
                interpolation="nearest",
                vmin=0,
                vmax=max(1.0, amplitude, interference_amplitude)
            )

            # Restore dark theme
            self.waterfall_ax.set_facecolor(self.bg_color)
            self.waterfall_ax.set_title("Spectrum Waterfall", color=self.text_color)
            self.waterfall_ax.set_xlabel("Frequency (Hz)", color=self.text_color)
            self.waterfall_ax.set_ylabel("History (s)", color=self.text_color)
            self.waterfall_ax.tick_params(colors=self.text_color)
            self.waterfall_ax.grid(False)

            # Redraw Waterfall canvas
            self.waterfall_canvas.draw_idle()

        # Update both canvases
        self.time_canvas.draw_idle()
        self.fft_canvas.draw_idle()

        # Display analysis parameters 
        results = (
            f"Frequency: {frequency} Hz\n"
            f"Amplitude: {amplitude}\n"
            f"Sample Rate: {sample_rate} Hz\n"
            f"Noise Level: {noise_level}\n"
            f"Interference Frequency: {interference_frequency} Hz\n"
            f"Interference Amplitude: {interference_amplitude}\n"
        )

        # Display detected signals
        results += "\nDetected Signals:\n"

        if len(detected_signals) == 0:
            results += "No significant peaks detected.\n"
        else:
            for detected_frequency, detected_amplitude, classification in detected_signals:
                results += (
                    f"{detected_frequency:.2f} Hz | "
                    f"Amplitude: {detected_amplitude:.3f} | "
                    f"{classification}\n"
                )

        # Display rolling buffer information
        if self.live_timer.isActive():
            buffer_samples = len(self.live_buffer)
            buffer_capacity = self.live_buffer_size
            buffer_duration = buffer_samples / sample_rate

            # Calculate FFT frequency resolution
            fft_resolution = sample_rate / len(fft_signal)

            results += (
                f"\nLive Buffer: {buffer_samples}/{buffer_capacity} samples"
                f"\nBuffer Duration: {buffer_duration:.2f} s"
                f"\nFFT Resolution: {fft_resolution:.2f} Hz"
            )

        self.results_label.setText(results)

    def clear_results(self):
        # Stop Live Mode if it is running
        if self.live_timer.isActive():
            self.stop_live()

        # Clear plotted signal data
        self.time_line.set_data([],[])
        self.fft_line.set_data([],[])

        # Remove detected peak markers
        for marker in self.fft_ax.collections[:]:
            marker.remove()

        # Reset plot axes
        self.time_ax.set_xlim(0,1)
        self.time_ax.set_ylim(-1,1)

        self.fft_ax.set_xlim(0,100)
        self.fft_ax.set_ylim(0,1)

        # Clear Waterfall history
        self.waterfall_history = []

        # Clear Waterfall visualization
        self.waterfall_ax.clear()

        # Restore Waterfall appearance
        self.waterfall_ax.set_facecolor(self.bg_color)
        self.waterfall_ax.set_title("Spectrum Waterfall", color=self.text_color)
        self.waterfall_ax.set_xlabel("Frequency (Hz)", color=self.text_color)
        self.waterfall_ax.set_ylabel("History (s)", color=self.text_color)

        self.waterfall_ax.tick_params(colors=self.text_color)
        self.waterfall_ax.set_xlim(0,100)
        self.waterfall_ax.grid(False)

        # Refresh Waterfall canvas
        self.waterfall_canvas.draw_idle()

        # Redraw both graphs
        self.time_canvas.draw_idle()
        self.fft_canvas.draw_idle()

        # Reset results
        self.results_label.setText("No analysis performed yet.")

    def start_live(self):

        self.live_time = 0.0

        # Clear previous live samples
        self.live_buffer = np.array([])
        self.previous_sample_rate = None

        # Reset Waterfall history
        self.waterfall_history = []

        # Start the timer
        self.live_timer.start()

        # Update button states
        self.start_live_button.setEnabled(False)
        self.stop_live_button.setEnabled(True)
        print("Live Mode Started")

        # Disable static analysis during Live Mode
        self.analyze_button.setEnabled(False)

        # Update mode indicator to LIVE
        self.mode_indicator.setText("● LIVE MODE")
        self.mode_indicator.setStyleSheet("""
                QLabel {
                background-color: #153A32;
                color: #54D6A0;
                border: 1px solid #287F66;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: bold;
                }
        """)

    def stop_live(self):
        # Stop the timer
        self.live_timer.stop()

        # Update button states
        self.start_live_button.setEnabled(True)
        self.stop_live_button.setEnabled(False)
        print("Live Mode Stopped")

        # Enable static analysis again
        self.analyze_button.setEnabled(True)

        # Update mode indicator to STATIC
        self.mode_indicator.setText("● STATIC MODE")
        self.mode_indicator.setStyleSheet("""
                QLabel {
                background-color: #202A36;
                color: #AAB8C8;
                border: 1px solid #39495A;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: bold;}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RFSenseWindow()
    window.showMaximized()
    sys.exit(app.exec())