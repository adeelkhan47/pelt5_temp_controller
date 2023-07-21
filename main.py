import json
import sys
import time

import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, \
    QPushButton, QTextEdit, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def read_response(ser):
    response = ser.readline().decode('utf-8').strip()
    return response


class Pelt5ControllerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        with open("default_values.json") as file:
            self.data = json.load(file)
        self.setWindowTitle("Pelt5 Temp Controller")
        # self.setGeometry(100, 100, 600, 300)  # Set the fixed size of the window
        # self.setFixedSize(800,1500)  # Set the fixed size of the window

        # Find the PELT-5 serial port

        self.ser = None
        self.port = 9600
        self.x_axis = []
        self.y_axis = []
        self.y_axis_2 = []
        self.x = 0
        self.y = 20
        self.y2 = 0
        ports = list(serial.tools.list_ports.comports())
        self.pelt_port = []
        for port in ports:
            if port.device:
                self.pelt_port.append(port.device)
        # self.ser = None
        self.ser = serial.Serial(self.pelt_port[1], 9600, timeout=1)
        self.init_ui()
        self.timer = QTimer()

        self.timer.timeout.connect(self.get_temperature)
        self.timer.start(1000)

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

        # Desired Heat Gain
        port_label = QLabel("Port")
        self.port_input = QComboBox()  # Change this line
        self.port_input.addItems(self.pelt_port)  # Add this line to load the list of strings into the dropdown
        port_button = QPushButton("Change Value")
        port_button.clicked.connect(self.change_port)
        grid_layout.addWidget(port_label, 7, 0)
        grid_layout.addWidget(self.port_input, 7, 1)
        grid_layout.addWidget(port_button, 7, 2)

        self.desired_temp_input.setText("20")
        self.cold_derivative_input.setText("1")
        self.cold_reset_input.setText("1")
        self.cold_gain_input.setText("1")
        self.heat_derivative_input.setText("1")
        self.heat_reset_input.setText("1")
        self.heat_gain_input.setText("1")
        # self.port_input.se(self.pelt_port[0])

        layout.addLayout(grid_layout)
        self.set_default_button = QPushButton("Reset PID Parameters for Probe in Liquid")
        self.set_default_button.clicked.connect(self.set_default_values)
        layout.addWidget(self.set_default_button)

        self.set_default_button_2 = QPushButton("Reset PID Parameters for Probe on Plate Surface")
        self.set_default_button_2.clicked.connect(self.set_default_values_2)
        layout.addWidget(self.set_default_button_2)

        # Feed Profile Row
        feed_profile_button = QPushButton("Feed Profile from Spreadsheet")
        self.interval_label = QLabel("Interval:")
        self.interval_input = QLineEdit()
        self.interval_input.setText("5")
        start_spreadsheet_row_button = QPushButton("Start Spreadsheet Row")
        layout.addWidget(feed_profile_button)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_input)
        layout.addWidget(start_spreadsheet_row_button)

        # Graph
        self.canvas = self.plot_graph()
        layout.addWidget(self.canvas)

        # Log Text Field
        self.log_textfield = QTextEdit()
        self.log_textfield.setText("Application Started Successfully.\n")
        layout.addWidget(self.log_textfield)
        self.show()

    def get_temperature(self):
        command = '?'
        self.ser.write((command + '\r\n').encode('utf-8'))
        response = self.ser.readline().decode('utf-8').strip()
        read_temp = 0
        if response:
            _, _, _, read_temp = response.split(',')
            print(f'Current temperature: {read_temp}°C')

        self.y2 = float(read_temp)
        self.x_axis.append(self.x)
        self.y_axis.append(self.y)
        self.y_axis_2.append(self.y2)
        self.x = self.x+1
        self.update_graph()

    def update_graph(self):
        self.ax.clear()
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        val = 300
        if self.interval_input.text():
            val = int(self.interval_input.text())*60
        self.ax.set_xlim(0, val)
        self.ax.set_ylim(0, 50)
        self.ax.plot(self.x_axis, self.y_axis, color='blue', label='Set Temperature ')  # First line
        self.ax.plot(self.x_axis, self.y_axis_2, color='red', label='Measured Temperature')
        self.ax.legend()
        self.canvas.draw()

    def plot_graph(self):
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        val = 300
        if self.interval_input.text():
            val = int(self.interval_input.text()) * 60
        self.ax.set_xlim(0, val)
        self.ax.set_ylim(0, 50)
        # Add your dummy data here

        self.ax.plot(self.x_axis, self.x_axis)
        canvas = FigureCanvas(self.figure)
        return canvas

    def change_setpoint_temperature(self):
        temperature = float(self.desired_temp_input.text())
        self.y = float(self.desired_temp_input.text())
        command = f'T+{temperature:.2f}'
        reply = self.send_command(command)
        if len(reply) > 0:
            setpoint = float(reply.split(',')[1])
            if setpoint == temperature:
                self.log_textfield.append("Setpoint temperature changed successfully.")
                print('Setpoint temperature changed successfully.')
        time.sleep(1)

    def change_desired_cold_derivative(self):
        derivative = float(self.cold_derivative_input.text())
        command = f'd {derivative:.1f}'
        self.send_command(command)
        self.log_textfield.append("Desired cold derivative set successfully.")
        print('Desired cold derivative set successfully.')
        time.sleep(1)

    def change_desired_cold_reset(self):
        reset = float(self.cold_reset_input.text())
        command = f'R+{reset:.1f}'
        self.send_command(command)

        self.log_textfield.append("Desired cold reset set successfully.")
        print('Desired cold reset set successfully.')
        time.sleep(1)

    def change_desired_cold_gain(self):
        gain = float(self.cold_gain_input.text())
        command = f'G {gain:.1f}'
        self.send_command(command)
        self.log_textfield.append("Desired cold gain set successfully.")
        print('Desired cold gain set successfully.')
        time.sleep(1)

    def change_desired_heat_derivative(self):
        derivative = float(self.heat_derivative_input.text())
        command = f'D {derivative:.1f}'
        self.send_command(command)
        self.log_textfield.append("Desired heat derivative set successfully.")
        print('Desired heat derivative set successfully.')
        time.sleep(1)

    def change_desired_heat_reset(self):
        reset = float(self.heat_reset_input.text())
        command = f'r+{reset:.1f}'
        self.send_command(command)
        self.log_textfield.append("Desired heat reset set successfully.")
        print('Desired heat reset set successfully.')
        time.sleep(1)

    def change_desired_heat_gain(self):
        gain = float(self.heat_gain_input.text())
        command = f'g {gain:.1f}'
        self.send_command(command)
        self.log_textfield.append("Desired heat gain set successfully.")
        print('Desired heat gain set successfully.')
        time.sleep(1)

    def change_port(self):
        self.port = self.port_input.currentText()
        self.ser = serial.Serial(self.port, 9600, timeout=1)
        time.sleep(1)

    def set_default_values(self):
        self.desired_temp_input.setText(str(self.data["liquid"]["new_setpoint"]))
        self.cold_derivative_input.setText(str(self.data["liquid"]["new_cold_derivative"]))
        self.cold_reset_input.setText(str(self.data["liquid"]["new_cold_reset"]))
        self.cold_gain_input.setText(str(self.data["liquid"]["new_cold_gain"]))
        self.heat_derivative_input.setText(str(self.data["liquid"]["new_heat_derivative"]))
        self.heat_reset_input.setText(str(self.data["liquid"]["new_heat_reset"]))
        self.heat_gain_input.setText(str(self.data["liquid"]["new_heat_gain"]))
        self.change_setpoint_temperature()
        self.change_desired_cold_derivative()
        self.change_desired_cold_reset()
        self.change_desired_cold_gain()
        self.change_desired_heat_derivative()
        self.change_desired_heat_reset()
        self.change_desired_heat_gain()

    def set_default_values_2(self):
        self.desired_temp_input.setText(str(self.data["plate_surface"]["new_setpoint"]))
        self.cold_derivative_input.setText(str(self.data["plate_surface"]["new_cold_derivative"]))
        self.cold_reset_input.setText(str(self.data["plate_surface"]["new_cold_reset"]))
        self.cold_gain_input.setText(str(self.data["plate_surface"]["new_cold_gain"]))
        self.heat_derivative_input.setText(str(self.data["plate_surface"]["new_heat_derivative"]))
        self.heat_reset_input.setText(str(self.data["plate_surface"]["new_heat_reset"]))
        self.heat_gain_input.setText(str(self.data["plate_surface"]["new_heat_gain"]))
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

    def closeEvent(self, event):
        # Stop the timer when the window is closing to avoid unnecessary operations.
        self.timer.stop()
        # Close the serial port on window close
        self.ser.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Pelt5ControllerWindow()
    window.show()
    sys.exit(app.exec_())
