from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pyqtgraph as pg
import sys
from pathlib import Path

from PyQt5.uic import loadUiType

from Equalizer import Signal
import SignalViewer as sv

ui, _ = loadUiType('main.ui')


class MainApp(QMainWindow, ui):
    _show_hide_flag = True

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1450, 900)

        # Objects : signal
        self.signal = Signal()
        self.original_signal_plot = sv.PlotSignal()
        self.equalized_signal_plot = sv.PlotSignal()

        # initiate sliders frames status
        self.uniform_sliders_frame.setVisible(True)
        self.animals_sliders_frame.setVisible(False)
        self.music_sliders_frame.setVisible(False)
        self.ecg_sliders_frame.setVisible(False)

        self.play_pause_status = True

        # original signal
        self.original_plot_widget = pg.PlotWidget(self.original_graphics_view)
        self.graphics_view_layout1 = QHBoxLayout(self.original_graphics_view)
        self.graphics_view_layout1.addWidget(self.original_plot_widget)
        self.original_graphics_view.setLayout(self.graphics_view_layout1)
        self.original_plot_widget.setObjectName("original_plot_widget")

        self.original_signal_viewer = sv.SignalViewerLogic(self.original_plot_widget)
        self.original_signal_viewer.view.setLabel("bottom", text="Frequency (Hz)")
        self.original_signal_viewer.view.setLabel("left", text="Amplitude (mV)")
        self.original_signal_viewer.view.setTitle("Original Signal")

        self.original_signal_viewer.signal = self.original_signal_plot

        # equalized signal
        self.equalized_plot_widget = pg.PlotWidget(self.equalized_graphics_view)
        self.graphics_view_layout1 = QHBoxLayout(self.equalized_graphics_view)
        self.graphics_view_layout1.addWidget(self.equalized_plot_widget)
        self.equalized_graphics_view.setLayout(self.graphics_view_layout1)
        self.equalized_plot_widget.setObjectName("equalized_plot_widget")

        self.equalized_signal_viewer = sv.SignalViewerLogic(self.equalized_plot_widget)
        self.equalized_signal_viewer.view.setLabel("bottom", text="Frequency (Hz)")
        self.equalized_signal_viewer.view.setLabel("left", text="Amplitude (mV)")
        self.equalized_signal_viewer.view.setTitle("Equalized Signal")

        self.equalized_signal_viewer.signal = self.equalized_signal_plot

        # original signal spectrogram
        self.original_spectro_plot_widget = pg.PlotWidget(self.original_spectro_graphics_view)
        self.graphics_view_layout2 = QHBoxLayout(self.original_spectro_graphics_view)
        self.graphics_view_layout2.addWidget(self.original_spectro_plot_widget)
        self.original_spectro_graphics_view.setLayout(self.graphics_view_layout2)
        self.original_spectro_plot_widget.setObjectName("original_spectro_plot_widget")

        self.original_spectro_viewer = sv.SignalViewerLogic(self.original_spectro_plot_widget)
        self.original_spectro_viewer.view.setLabel("bottom", text="Frequency (Hz)")
        self.original_spectro_viewer.view.setLabel("left", text="Amplitude (mV)")
        self.original_spectro_viewer.view.setTitle("Spectrogram for Original Signal")

        # frequency plot
        self.frequency_plot_widget = pg.PlotWidget(self.frequency_graphics_view)
        self.graphics_view_layout3 = QHBoxLayout(self.frequency_graphics_view)
        self.graphics_view_layout3.addWidget(self.frequency_plot_widget)
        self.frequency_graphics_view.setLayout(self.graphics_view_layout3)
        self.frequency_plot_widget.setObjectName("frequency_plot_widget")

        self.frequency_signal_viewer = sv.SignalViewerLogic(self.frequency_plot_widget)
        self.frequency_signal_viewer.view.setLabel("bottom", text="Frequency (Hz)")
        self.frequency_signal_viewer.view.setLabel("left", text="Amplitude (mV)")
        self.frequency_signal_viewer.view.setTitle("Frequency Signal")

        # equalized signal spectrogram
        self.equalized_spectro_plot_widget = pg.PlotWidget(self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout = QHBoxLayout(self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout.addWidget(self.equalized_spectro_plot_widget)
        self.equalized_spectro_graphics_view.setLayout(self.graphics_view_mixer_layout)
        self.equalized_spectro_plot_widget.setObjectName("equalized_spectro_plot_widget")

        self.equalized_spectro_viewer = sv.SignalViewerLogic(self.equalized_spectro_plot_widget)
        self.equalized_spectro_viewer.view.setLabel("bottom", text="Frequency (Hz)")
        self.equalized_spectro_viewer.view.setLabel("left", text="Amplitude (mV)")
        self.equalized_spectro_viewer.view.setTitle("Spectrogram for Equalized Signal")

        # ------------------------------- signals and slots --------------------------------------
        self.show_hide_btn.clicked.connect(self.show_hide_spectro_widget)

        self.speed_slider.sliderPressed.connect(lambda: self.change_slider_cursor(self.speed_slider))
        self.speed_slider.sliderReleased.connect(lambda: self.reset_slider_cursor(self.speed_slider))

        self.mode_comboBox.currentTextChanged.connect(self.change_sliders_for_modes)

        self.open_btn.clicked.connect(self.open_signal)

        # self.play_pause_btn.clicked.connect()
        # self.stop_btn.clicked.connect()
        # self.replay_btn.clicked.connect()
        # self.reset_view_btn.clicked.connect()
        # self.zoom_in_btn.clicked.connect()
        # self.zoom_out_btn.clicked.connect()
        # self.speed_slider.valueChanged.connect()
        #
        # self.window_comboBox.currentTextChanged.connect()

    def open_signal(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Signal to Equalizer', '',
                                                   'wav Files (*.wav)', options=options)
        self.signal.import_signal(file_name, "stft")
        self.original_signal_viewer.add_signal()
        self.equalized_signal_viewer.add_signal()

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
            self.original_spectro_frame.setVisible(False)
            self.equalized_spectro_frame.setVisible(False)
            self.show_hide_btn.setIcon(QIcon('icons/eye-crossed copy.svg'))
            self._show_hide_flag = False
        else:
            self.original_spectro_frame.setVisible(True)
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

# ----------------------------------- for loop for create sliders -----------------------------------

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
