from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pyqtgraph as pg
import sys
from pathlib import Path
import numpy as np

from PyQt5.uic import loadUiType

from Equalizer import Signal
import SignalViewer as sv

ui, _ = loadUiType('main.ui')


def plot_spectrogram(widget, sxx):
    # Plot Spectrogram
    img = pg.ImageItem()
    img.setImage(sxx)
    widget.addItem(img)

    # Set colormap
    colormap = pg.colormap.get('viridis')
    img.setColorMap(colormap)


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
        self.sliders_frames = {
            "Uniform Mode": self.uniform_sliders_frame,
            "Animal Mode": self.animals_sliders_frame,
            "Musical Mode": self.music_sliders_frame,
            "ECG Mode": self.ecg_sliders_frame
        }

        for sliders_frame in self.sliders_frames:
            self.sliders_frames[sliders_frame].setVisible(False)
        self.sliders_frames["Uniform Mode"].setVisible(True)

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
        self.original_spectro_plot_widget.setBackground((25, 35, 45))
        self.original_spectro_plot_widget.setLabel("bottom", text="Frequency (Hz)")
        self.original_spectro_plot_widget.setLabel("left", text="Amplitude (mV)")
        self.original_spectro_plot_widget.setTitle("Spectrogram for Original Signal")

        self.original_spectro_plot_item = pg.ImageItem()
        self.original_spectro_plot_item.setLookupTable(pg.colormap.get("viridis"))

        # frequency plot
        self.frequency_plot_widget = pg.PlotWidget(self.frequency_graphics_view)
        self.graphics_view_layout3 = QHBoxLayout(self.frequency_graphics_view)
        self.graphics_view_layout3.addWidget(self.frequency_plot_widget)
        self.frequency_graphics_view.setLayout(self.graphics_view_layout3)
        self.frequency_plot_widget.setObjectName("frequency_plot_widget")
        self.frequency_plot_widget.showGrid(x=True, y=True)
        self.frequency_plot_widget.setBackground((25, 35, 45))
        self.frequency_plot_widget.setLabel("bottom", text="Frequency (Hz)")
        self.frequency_plot_widget.setLabel("left", text="Amplitude (mV)")
        self.frequency_plot_widget.setTitle("Frequency Signal")

        self.frequency_plot_item = pg.PlotDataItem()

        # equalized signal spectrogram
        self.equalized_spectro_plot_widget = pg.PlotWidget(self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout = QHBoxLayout(self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout.addWidget(self.equalized_spectro_plot_widget)
        self.equalized_spectro_graphics_view.setLayout(self.graphics_view_mixer_layout)
        self.equalized_spectro_plot_widget.setObjectName("equalized_spectro_plot_widget")
        self.equalized_spectro_plot_widget.setBackground((25, 35, 45))
        self.equalized_spectro_plot_widget.setLabel("bottom", text="Frequency (Hz)")
        self.equalized_spectro_plot_widget.setLabel("left", text="Amplitude (mV)")
        self.equalized_spectro_plot_widget.setTitle("Spectrogram for Equalized Signal")

        self.equalized_spectro_plot_item = pg.ImageItem()
        self.equalized_spectro_plot_item.setLookupTable(pg.colormap.get("viridis"))

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

        # self.window_comboBox.currentTextChanged.connect()

        self.uniform_slider_1.valueChanged.connect(lambda: self.uniform_slider('rectangle',
                                                                               self.uniform_slider_1.value(),
                                                                               (0, 2000),
                                                                               )
                                                   )
        self.uniform_slider_2.valueChanged.connect(lambda: self.uniform_slider('rectangle',
                                                                               self.uniform_slider_2.value(),
                                                                               (2000, 4000),
                                                                               )
                                                   )
        self.uniform_slider_3.valueChanged.connect(lambda: self.uniform_slider('rectangle',
                                                                               self.uniform_slider_3.value(),
                                                                               (4000, 6000),
                                                                               )
                                                   )
        self.uniform_slider_4.valueChanged.connect(lambda: self.uniform_slider('hamming',
                                                                               self.uniform_slider_4.value(),
                                                                               (6000, 8000),
                                                                               )
                                                   )
        self.uniform_slider_5.valueChanged.connect(lambda: self.uniform_slider('hamming',
                                                                               self.uniform_slider_5.value(),
                                                                               (8000, 10000),
                                                                               )
                                                   )
        self.uniform_slider_6.valueChanged.connect(lambda: self.uniform_slider('hamming',
                                                                               self.uniform_slider_6.value(),
                                                                               (10000, 12000),
                                                                               )
                                                   )
        self.uniform_slider_7.valueChanged.connect(lambda: self.uniform_slider('hamming',
                                                                               self.uniform_slider_7.value(),
                                                                               (12000, 14000),
                                                                               )
                                                   )
        self.uniform_slider_8.valueChanged.connect(lambda: self.uniform_slider('hamming',
                                                                               self.uniform_slider_8.value(),
                                                                               (14000, 16000),
                                                                               )
                                                   )
        self.uniform_slider_9.valueChanged.connect(lambda: self.uniform_slider('hamming',
                                                                               self.uniform_slider_9.value(),
                                                                               (16000, 18000),
                                                                               )
                                                   )
        self.uniform_slider_10.valueChanged.connect(lambda: self.uniform_slider('hamming',
                                                                                self.uniform_slider_10.value(),
                                                                                (18000, 20000),
                                                                                )
                                                    )

    def uniform_slider(self, w_type, value, freqs_range):
        self.signal.equalize(w_type, value / 10, freqs_range=freqs_range)

    def open_signal(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Signal to Equalizer', '',
                                                   'wav Files (*.wav)', options=options)
        self.signal.import_signal(file_name, "stft")

        self.original_signal_viewer.clear()
        self.equalized_signal_viewer.clear()
        self.frequency_plot_widget.clear()
        self.original_spectro_plot_widget.clear()
        self.equalized_spectro_plot_widget.clear()

        self.original_signal_viewer.load_dataset(self.signal)
        self.equalized_signal_viewer.load_dataset(self.signal)
        self.original_signal_viewer.add_signal()
        self.equalized_signal_viewer.add_signal()

        self.frequency_plot_item.setData(self.signal.signal_frequencies, 20 *
                                         np.log10(self.signal.signal_amplitudes[:len(self.signal.signal_frequencies)]))
        self.frequency_plot_widget.addItem(self.frequency_plot_item)

        plot_spectrogram(self.original_spectro_plot_widget, self.signal.original_signal_spectrogram)

        plot_spectrogram(self.equalized_spectro_plot_widget, self.signal.equalized_signal_spectrogram)

    def change_sliders_for_modes(self, text):
        for sliders_frame in self.sliders_frames:
            self.sliders_frames[sliders_frame].setVisible(False)
        self.sliders_frames[text].setVisible(True)

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
