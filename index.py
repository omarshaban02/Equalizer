from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer

import pyqtgraph as pg
import numpy as np
import pandas as pd
import sys
from pathlib import Path
from res_rc import *  # Import the resource module

from PyQt5.uic import loadUiType
import urllib.request



ui, _ = loadUiType('main.ui')



class MainApp(QMainWindow, ui):

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1450, 900)


        self.original_plot_widget = pg.PlotWidget(self.original_graphics_view)
        self.graphics_view_layout1 = QHBoxLayout(self.original_graphics_view)
        self.graphics_view_layout1.addWidget(self.original_plot_widget)
        self.original_graphics_view.setLayout(self.graphics_view_layout1)
        self.original_plot_widget.setObjectName("original_plot_widget")
        self.original_plot_widget.setBackground((25, 35, 45))
        self.original_plot_widget.showGrid(x=True, y=True)
        self.original_plot_widget.setLabel("bottom", text = "Frequency (Hz)")
        self.original_plot_widget.setLabel("left", text = "Amplitude (mV)")
        self.original_plot_widget.setTitle("Original Signal")

        self.equalized_plot_widget = pg.PlotWidget(self.equalized_graphics_view)
        self.graphics_view_layout1 = QHBoxLayout(self.equalized_graphics_view)
        self.graphics_view_layout1.addWidget(self.equalized_plot_widget)
        self.equalized_graphics_view.setLayout(self.graphics_view_layout1)
        self.equalized_plot_widget.setObjectName("equalized_plot_widget")
        self.equalized_plot_widget.setBackground((25, 35, 45))
        self.equalized_plot_widget.showGrid(x=True, y=True)
        self.equalized_plot_widget.setLabel("bottom", text = "Frequency (Hz)")
        self.equalized_plot_widget.setLabel("left", text = "Amplitude (mV)")
        self.equalized_plot_widget.setTitle("Equalized Signal")


        self.orignal_spectro_plot_widget = pg.PlotWidget(self.orignal_spectro_graphics_view)
        self.graphics_view_layout2 = QHBoxLayout(self.orignal_spectro_graphics_view)
        self.graphics_view_layout2.addWidget(self.orignal_spectro_plot_widget)
        self.orignal_spectro_graphics_view.setLayout(self.graphics_view_layout2)
        self.orignal_spectro_plot_widget.setObjectName("orignal_spectro_plot_widget")
        self.orignal_spectro_plot_widget.setBackground((25, 35, 45))
        self.orignal_spectro_plot_widget.showGrid(x=True, y=True)
        self.orignal_spectro_plot_widget.setLabel("bottom", text = "Frequency (Hz)")
        self.orignal_spectro_plot_widget.setLabel("left", text = "Amplitude (mV)")
        self.orignal_spectro_plot_widget.setTitle("Spectrogram for Original Signal")

        self.frequency_plot_widget = pg.PlotWidget(self.frequency_graphics_view)
        self.graphics_view_layout3 = QHBoxLayout(self.frequency_graphics_view)
        self.graphics_view_layout3.addWidget(self.frequency_plot_widget)
        self.frequency_graphics_view.setLayout(self.graphics_view_layout3)
        self.frequency_plot_widget.setObjectName("frequency_plot_widget")
        self.frequency_plot_widget.setBackground((25, 35, 45))
        self.frequency_plot_widget.showGrid(x=True, y=True)
        self.frequency_plot_widget.setLabel("bottom", text = "Frequency (Hz)")
        self.frequency_plot_widget.setLabel("left", text = "Amplitude (mV)")
        self.frequency_plot_widget.setTitle("Frequency Signal")

        self.equalized_spectro_plot_widget = pg.PlotWidget(self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout = QHBoxLayout(self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout.addWidget(self.equalized_spectro_plot_widget)
        self.equalized_spectro_graphics_view.setLayout(self.graphics_view_mixer_layout)
        self.equalized_spectro_plot_widget.setObjectName("equalized_spectro_plot_widget")
        self.equalized_spectro_plot_widget.setBackground((25, 35, 45))
        self.equalized_spectro_plot_widget.showGrid(x=True, y=True)
        self.equalized_spectro_plot_widget.setLabel("bottom", text = "Frequency (Hz)")
        self.equalized_spectro_plot_widget.setLabel("left", text = "Amplitude (mV)")
        self.equalized_spectro_plot_widget.setTitle("Spectrogram for Equalized Signal")


        self.speed_slider.sliderPressed.connect(lambda: self.change_slider_cursor(self.speed_slider))
        self.speed_slider.sliderReleased.connect(lambda: self.reset_slider_cursor(self.speed_slider))
        self.add_sliders()


        # self.open_btn.clicked.connect(self.open_signal_file)

    def add_sliders(self):
        frame = self.findChild(QWidget, 'sliders_frame')

        layout = QVBoxLayout()

        num_sliders = 5

        for i in range(num_sliders):
            slider = QSlider()
            slider.setOrientation(Qt.Vertical)  # You can set it to Vertical if needed
            slider.setMinimum(0)
            slider.setMaximum(100)

            # Add the slider to the layout
            layout.addWidget(slider)

        # Set the layout for the frame
        frame.setLayout(layout)




    def change_slider_cursor(self, slider):
        if self.signal or self.mixed_signal:
            slider.setCursor(Qt.ClosedHandCursor)
        else:
            QMessageBox.critical(None, "Error", "No signal found", QMessageBox.Ok)

    def reset_slider_cursor(self, slider):
        slider.setCursor(Qt.OpenHandCursor)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('qss/darkStyle.qss').read_text())
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
