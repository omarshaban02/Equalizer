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

    _show_hide_flag = True
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1450, 900)

        self.uniform_sliders_frame.setVisible(True)
        self.animals_sliders_frame.setVisible(False)
        self.music_sliders_frame.setVisible(False)
        self.ecg_sliders_frame.setVisible(False)

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

        self.show_hide_btn.clicked.connect(self.show_hide_spectro_widget)

        self.speed_slider.sliderPressed.connect(lambda: self.change_slider_cursor(self.speed_slider))
        self.speed_slider.sliderReleased.connect(lambda: self.reset_slider_cursor(self.speed_slider))

        self.mode_comboBox.currentTextChanged.connect(self.change_sliders_for_modes)


    def change_sliders_for_modes(self, text):
        if text == "Uniform Mode":
            self.uniform_sliders_frame.setVisible(True)
            self.animals_sliders_frame.setVisible(False)
            self.music_sliders_frame.setVisible(False)
            self.ecg_sliders_frame.setVisible(False)
        if text == "Animal Mode":
            self.uniform_sliders_frame.setVisible(False)
            self.animals_sliders_frame.setVisible(True)
            self.music_sliders_frame.setVisible(False)
            self.ecg_sliders_frame.setVisible(False)
        if text == "Musical Mode":
            self.uniform_sliders_frame.setVisible(False)
            self.animals_sliders_frame.setVisible(False)
            self.music_sliders_frame.setVisible(True)
            self.ecg_sliders_frame.setVisible(False)
        if text == "ECG Mode":
            self.uniform_sliders_frame.setVisible(False)
            self.animals_sliders_frame.setVisible(False)
            self.music_sliders_frame.setVisible(False)
            self.ecg_sliders_frame.setVisible(True)


    def show_hide_spectro_widget(self):
        if self._show_hide_flag:
            self.orignal_spectro_frame.setVisible(False)
            self.equalized_spectro_frame.setVisible(False)
            self.show_hide_btn.setIcon(QIcon('icons/eye-crossed copy.svg'))
            self._show_hide_flag = False
        else:
            self.orignal_spectro_frame.setVisible(True)
            self.equalized_spectro_frame.setVisible(True)
            self.show_hide_btn.setIcon(QIcon('icons/eye copy.svg'))
            self._show_hide_flag = True

    def change_slider_cursor(self, slider):
        slider.setCursor(Qt.ClosedHandCursor)

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











#########################for loop for creat sliders#########################################################

 # # self.open_btn.clicked.connect(self.open_signal_file)
 #
 #        self.sliders_frame = self.findChild(QFrame, 'sliders_frame')
 #        self.slider_list = []
 #        self.add_sliders(5)
 #
 #
 #        self.slider_list[0].sliderPressed.connect(lambda: self.change_slider_cursor(self.slider_list[0]))
 #        self.slider_list[0].sliderReleased.connect(lambda: self.reset_slider_cursor(self.slider_list[0]))
 #        self.slider_list[1].sliderPressed.connect(lambda: self.change_slider_cursor(self.slider_list[1]))
 #        self.slider_list[1].sliderReleased.connect(lambda: self.reset_slider_cursor(self.slider_list[1]))
 #        self.slider_list[2].sliderPressed.connect(lambda: self.change_slider_cursor(self.slider_list[2]))
 #        self.slider_list[2].sliderReleased.connect(lambda: self.reset_slider_cursor(self.slider_list[2]))
 #        self.slider_list[3].sliderPressed.connect(lambda: self.change_slider_cursor(self.slider_list[3]))
 #        self.slider_list[3].sliderReleased.connect(lambda: self.reset_slider_cursor(self.slider_list[3]))
 #        self.slider_list[4].sliderPressed.connect(lambda: self.change_slider_cursor(self.slider_list[4]))
 #        self.slider_list[4].sliderReleased.connect(lambda: self.reset_slider_cursor(self.slider_list[4]))
 #
 #
 #    def add_sliders(self,number_of_sliders):
 #        layout = QHBoxLayout(self.sliders_frame)
 #
 #        for i in range(number_of_sliders):
 #            # Create a slider
 #            slider = QSlider(Qt.Vertical, self)
 #            slider.setCursor(Qt.OpenHandCursor)
 #            slider.setObjectName(f'slider_{i}')
 #            self.slider_list.append(slider)
 #
 #
 #            # Add the slider to the layout
 #            layout.addWidget(slider)
 #
 #        # Set the layout for the sliders_frame
 #        self.sliders_frame.setLayout(layout)
