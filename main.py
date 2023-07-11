from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit
import sys
import time
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Pelt5ControllerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pelt5 Temp Controller")
        #self.setGeometry(100, 100, 600, 300)  # Set the fixed size of the window

        # Find the PELT-5 serial port
        ports = list(serial.tools.list_ports.comports())
        pelt_port = None
        for port in ports:
            if "PELT-5" in port.description or "pelt-v" in port.description.casefold() or "peltv" in port.description.casefold() \
                    or "pelt" in port.description.casefold():
                pelt_port = port.device
                break
        else:
            raise Exception("PELT-5 serial port not found")

        self.ser = serial.Serial(pelt_port, 9600, timeout=1)
        #self.ser = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        grid_layout = QGridLayout()

        # Desired Temperature
        desired_temp_label = QLabel("Desired Temperature (C):")
        self.desired_temp_input = QLineEdit()
        change_temp_button = QPushButton("Change Value")
        change_temp_button.clicked.connect(self.change_setpoint_temperature)
        grid_layout.addWidget(desired_temp_label, 0, 0)
        grid_layout.addWidget(self.desired_temp_input, 0, 1)
        grid_layout.addWidget(change_temp_button, 0, 2)

        # Desired Cold Derivative
        cold_derivative_label = QLabel("Desired Cold Derivative (0-999):")
        self.cold_derivative_input = QLineEdit()
        change_cold_derivative_button = QPushButton("Change Value")
        change_cold_derivative_button.clicked.connect(self.change_desired_cold_derivative)
        grid_layout.addWidget(cold_derivative_label, 1, 0)
        grid_layout.addWidget(self.cold_derivative_input, 1, 1)
        grid_layout.addWidget(change_cold_derivative_button, 1, 2)

        # Desired Cold Reset
        cold_reset_label = QLabel("Desired Cold Reset (0-999 for Pelt5):")
        self.cold_reset_input = QLineEdit()
        change_cold_reset_button = QPushButton("Change Value")
        change_cold_reset_button.clicked.connect(self.change_desired_cold_reset)
        grid_layout.addWidget(cold_reset_label, 2, 0)
        grid_layout.addWidget(self.cold_reset_input, 2, 1)
        grid_layout.addWidget(change_cold_reset_button, 2, 2)

        # Desired Cold Gain
        cold_gain_label = QLabel("Desired Cold Gain (0-199 for Pelt5):")
        self.cold_gain_input = QLineEdit()
        change_cold_gain_button = QPushButton("Change Value")
        change_cold_gain_button.clicked.connect(self.change_desired_cold_gain)
        grid_layout.addWidget(cold_gain_label, 3, 0)
        grid_layout.addWidget(self.cold_gain_input, 3, 1)
        grid_layout.addWidget(change_cold_gain_button, 3, 2)

        # Desired Heat Derivative
        heat_derivative_label = QLabel("Desired Heat Derivative (0-999 for Pelt5):")
        self.heat_derivative_input = QLineEdit()
        change_heat_derivative_button = QPushButton("Change Value")
        change_heat_derivative_button.clicked.connect(self.change_desired_heat_derivative)
        grid_layout.addWidget(heat_derivative_label, 4, 0)
        grid_layout.addWidget(self.heat_derivative_input, 4, 1)
        grid_layout.addWidget(change_heat_derivative_button, 4, 2)

        # Desired Heat Reset
        heat_reset_label = QLabel("Desired Heat Reset (0-999 for Pelt5):")
        self.heat_reset_input = QLineEdit()
        change_heat_reset_button = QPushButton("Change Value")
        change_heat_reset_button.clicked.connect(self.change_desired_heat_reset)
        grid_layout.addWidget(heat_reset_label, 5, 0)
        grid_layout.addWidget(self.heat_reset_input, 5, 1)
        grid_layout.addWidget(change_heat_reset_button, 5, 2)

        # Desired Heat Gain
        heat_gain_label = QLabel("Desired Heat Gain (0-199 for Pelt5):")
        self.heat_gain_input = QLineEdit()
        change_heat_gain_button = QPushButton("Change Value")
        change_heat_gain_button.clicked.connect(self.change_desired_heat_gain)
        grid_layout.addWidget(heat_gain_label, 6, 0)
        grid_layout.addWidget(self.heat_gain_input, 6, 1)
        grid_layout.addWidget(change_heat_gain_button, 6, 2)

        self.desired_temp_input.setText("1")
        self.cold_derivative_input.setText("1")
        self.cold_reset_input.setText("1")
        self.cold_gain_input.setText("1")
        self.heat_derivative_input.setText("1")
        self.heat_reset_input.setText("1")
        self.heat_gain_input.setText("1")

        layout.addLayout(grid_layout)
        self.set_default_button = QPushButton("Set Default Values")
        self.set_default_button.clicked.connect(self.set_default_values)
        layout.addWidget(self.set_default_button)

        self.set_default_button_2 = QPushButton("Set Default Values 2")
        self.set_default_button_2.clicked.connect(self.set_default_values_2)
        layout.addWidget(self.set_default_button_2)

        # Feed Profile Row
        feed_profile_button = QPushButton("Feed Profile from Spreadsheet")
        interval_label = QLabel("Interval:")
        interval_input = QLineEdit()
        start_spreadsheet_row_button = QPushButton("Start Spreadsheet Row")
        layout.addWidget(feed_profile_button)
        layout.addWidget(interval_label)
        layout.addWidget(interval_input)
        layout.addWidget(start_spreadsheet_row_button)

        # Graph
        canvas = self.plot_graph()
        layout.addWidget(canvas)

        # Log Text Field
        log_textfield = QTextEdit()
        log_textfield.setText("Application Started Successfully.\n")
        layout.addWidget(log_textfield)

        self.show()

    def plot_graph(self):
        figure = plt.figure()
        ax = figure.add_subplot(111)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Temperature (°C)")
        ax.set_xlim(0, 40000)
        ax.set_ylim(0, 100)
        # Add your dummy data here
        x = [0, 10000, 20000, 30000, 40000]
        y = [25, 50, 75, 80, 90]
        ax.plot(x, y)
        canvas = FigureCanvas(figure)
        return canvas

    def change_setpoint_temperature(self):
        temperature = float(self.desired_temp_input.text())
        command = f'T+{temperature:.2f}'
        reply = self.send_command(command)
        if len(reply) > 0:
            setpoint = float(reply.split(',')[1])
            if setpoint == temperature:
                print('Setpoint temperature changed successfully.')
        time.sleep(1)

    def change_desired_cold_derivative(self):
        derivative = float(self.cold_derivative_input.text())
        command = f'd {derivative:.1f}'
        self.send_command(command)
        print('Desired cold derivative set successfully.')
        time.sleep(1)

    def change_desired_cold_reset(self):
        reset = float(self.cold_reset_input.text())
        command = f'R+{reset:.1f}'
        self.send_command(command)
        print('Desired cold reset set successfully.')
        time.sleep(1)

    def change_desired_cold_gain(self):
        gain = float(self.cold_gain_input.text())
        command = f'G {gain:.1f}'
        self.send_command(command)
        print('Desired cold gain set successfully.')
        time.sleep(1)

    def change_desired_heat_derivative(self):
        derivative = float(self.heat_derivative_input.text())
        command = f'D {derivative:.1f}'
        self.send_command(command)
        print('Desired heat derivative set successfully.')
        time.sleep(1)

    def change_desired_heat_reset(self):
        reset = float(self.heat_reset_input.text())
        command = f'r+{reset:.1f}'
        self.send_command(command)
        print('Desired heat reset set successfully.')
        time.sleep(1)

    def change_desired_heat_gain(self):
        gain = float(self.heat_gain_input.text())
        command = f'g {gain:.1f}'
        self.send_command(command)
        print('Desired heat gain set successfully.')
        time.sleep(1)

    def set_default_values(self):
        self.desired_temp_input.setText("0")
        self.cold_derivative_input.setText("0")
        self.cold_reset_input.setText("0")
        self.cold_gain_input.setText("0")
        self.heat_derivative_input.setText("0")
        self.heat_reset_input.setText("0")
        self.heat_gain_input.setText("0")
        self.change_setpoint_temperature()
        self.change_desired_cold_derivative()
        self.change_desired_cold_reset()
        self.change_desired_cold_gain()
        self.change_desired_heat_derivative()
        self.change_desired_heat_reset()
        self.change_desired_heat_gain()

    def set_default_values_2(self):
        self.desired_temp_input.setText("1")
        self.cold_derivative_input.setText("1")
        self.cold_reset_input.setText("1")
        self.cold_gain_input.setText("1")
        self.heat_derivative_input.setText("1")
        self.heat_reset_input.setText("1")
        self.heat_gain_input.setText("1")
        self.change_setpoint_temperature()
        self.change_desired_cold_derivative()
        self.change_desired_cold_reset()
        self.change_desired_cold_gain()
        self.change_desired_heat_derivative()
        self.change_desired_heat_reset()
        self.change_desired_heat_gain()

    def send_command(self, command):
        command += '\r\n'  # Append <CR><LF> to the command string
        self.ser.write(command.encode())  # Send the command
        time.sleep(0.1)  # Wait for the reply
        reply = self.ser.readline().decode().strip()  # Read the reply
        return reply

    def closeEvent(self, event):
        # Close the serial port on window close
        self.ser.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Pelt5ControllerWindow()
    window.show()
    sys.exit(app.exec_())
