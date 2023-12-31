from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pyqtgraph as pg
import sys
from pathlib import Path
import numpy as np

from PyQt5.uic import loadUiType

from Equalizer import Signal, Player, animals_slices, musics_slices
import SignalViewer as sv

ui, _ = loadUiType('main.ui')


def plot_spectrogram(widget, sxx):
    # Plot Spectrogram
    img = pg.ImageItem()
    img.setImage(np.rot90(sxx))
    widget.addItem(img)
    # widget.setYRange(0, 5 * np.log10(np.max(sxx)))

    # Set colormap
    colormap = pg.colormap.get('viridis')
    img.setColorMap(colormap)


def create_plot_widget(graphics_view, object_name="", bottom_label="", left_label="", signal_viewer_title=None,
                       signal_plot=None):
    widget = pg.PlotWidget(graphics_view)
    graphics_view_layout = QHBoxLayout(graphics_view)
    graphics_view_layout.addWidget(widget)
    graphics_view.setLayout(graphics_view_layout)
    widget.setObjectName(object_name)

    signal_viewer = sv.SignalViewerLogic(
        widget)

    signal_viewer.view.setLabel(
        "bottom", text=bottom_label)
    signal_viewer.view.setLabel(
        "left", text=left_label)
    if signal_viewer_title:
        signal_viewer.view.setTitle(signal_viewer_title)
    if signal_plot:
        signal_viewer.signal = signal_plot

    return widget, signal_viewer


def clear_widgets(widgets_list):
    for widget in widgets_list:
        widget.clear()


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

        # Smoothing Window
        self.smoothing_window = self.window_comboBox.currentText().lower()

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

        self.ranges_sliders = {
            self.uniform_slider_1: (0, 200),
            self.uniform_slider_2: (200, 400),
            self.uniform_slider_3: (400, 600),
            self.uniform_slider_4: (600, 800),
            self.uniform_slider_5: (800, 1000),
            self.uniform_slider_6: (1000, 1200),
            self.uniform_slider_7: (1200, 1400),
            self.uniform_slider_8: (1400, 1600),
            self.uniform_slider_9: (1600, 1800),
            self.uniform_slider_10: (1800, 2000),
        }
        self.ecg_sliders = {
            self.p_wave_arrhythmia_slider: (5, 10),
            self.sv_arrhythmia_slider: (5, 22),
            self.nr_arrhythmia_slider: (0, 10)
        }
        self.slices_sliders = {
            self.wolf_slider: "wolf",
            self.horse_slider: "horse",
            self.cow_slider: "cow",
            self.dolphin_slider: "dolphin",
            self.elephant_slider: "elephant",
            self.frog_slider: "frog",

            # self.trumpet_slider: "trumpet",
            self.piano_slider: "piano",
            self.xylophone_slider: "xylophone",
            self.flute_slider: "flute",
            self.chimes_slider: "chimes"
        }

        self.ecg_arrs_max_f_dict = {
            0.96: self.p_wave_arrhythmia_slider,
            1.5: self.sv_arrhythmia_slider,
            0.39: self.nr_arrhythmia_slider
        }

        # Flags
        self.play_pause_state = True
        self.original_sound_player = None
        self.equalized_sound_player = None
        self.ecg_mode_selected = False

        # original and equalized signal
        self.original_plot_widget, self.original_signal_viewer = create_plot_widget(
            self.original_graphics_view, "original_plot_widget", "Time (sec)", "Amplitude",
            "Original Signal", self.original_signal_plot
        )
        self.equalized_plot_widget, self.equalized_signal_viewer = create_plot_widget(
            self.equalized_graphics_view, "equalized_plot_widget", "Time (sec)", "Amplitude",
            "Equalized Signal", self.equalized_signal_plot
        )

        # Link both graphs
        self.original_signal_viewer.linkTo(self.equalized_signal_viewer)

        # original signal spectrogram
        self.original_spectro_plot_widget = pg.PlotWidget(
            self.original_spectro_graphics_view)
        self.graphics_view_layout2 = QHBoxLayout(
            self.original_spectro_graphics_view)
        self.graphics_view_layout2.addWidget(self.original_spectro_plot_widget)
        self.original_spectro_graphics_view.setLayout(
            self.graphics_view_layout2)
        self.original_spectro_plot_widget.setObjectName(
            "original_spectro_plot_widget")
        self.original_spectro_plot_widget.setBackground((25, 35, 45))
        self.original_spectro_plot_widget.setLabel(
            "bottom", text="Time Segment")
        self.original_spectro_plot_widget.setLabel(
            "left", text="Frequency (Hz)")
        self.original_spectro_plot_widget.setTitle(
            "Spectrogram for Original Signal")

        self.original_spectro_plot_item = pg.ImageItem()
        self.original_spectro_plot_item.setLookupTable(
            pg.colormap.get("viridis"))

        # frequency plot
        self.frequency_plot_widget = pg.PlotWidget(
            self.frequency_graphics_view)
        self.graphics_view_layout3 = QHBoxLayout(self.frequency_graphics_view)
        self.graphics_view_layout3.addWidget(self.frequency_plot_widget)
        self.frequency_graphics_view.setLayout(self.graphics_view_layout3)
        self.frequency_plot_widget.setObjectName("frequency_plot_widget")
        self.frequency_plot_widget.showGrid(x=True, y=True)
        self.frequency_plot_widget.setBackground((25, 35, 45))
        self.frequency_plot_widget.setLabel("bottom", text="Frequency (Hz)")
        self.frequency_plot_widget.setLabel("left", text="Amplitude (dB)")
        self.frequency_plot_widget.setTitle("Frequency Signal")

        self.frequency_plot_item = pg.PlotDataItem()

        # equalized signal spectrogram
        self.equalized_spectro_plot_widget = pg.PlotWidget(
            self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout = QHBoxLayout(
            self.equalized_spectro_graphics_view)
        self.graphics_view_mixer_layout.addWidget(
            self.equalized_spectro_plot_widget)
        self.equalized_spectro_graphics_view.setLayout(
            self.graphics_view_mixer_layout)
        self.equalized_spectro_plot_widget.setObjectName(
            "equalized_spectro_plot_widget")
        self.equalized_spectro_plot_widget.setBackground((25, 35, 45))
        self.equalized_spectro_plot_widget.setLabel(
            "bottom", text="Time Segment")
        self.equalized_spectro_plot_widget.setLabel(
            "left", text="Frequency (Hz)")
        self.equalized_spectro_plot_widget.setTitle(
            "Spectrogram for Equalized Signal")

        self.equalized_spectro_plot_item = pg.ImageItem()
        self.equalized_spectro_plot_item.setLookupTable(
            pg.colormap.get("viridis"))

        # ------------------------------- signals and slots --------------------------------------
        self.show_hide_btn.clicked.connect(self.show_hide_spectro_widget)

        self.speed_slider.sliderPressed.connect(
            lambda: self.change_slider_cursor(self.speed_slider))
        self.speed_slider.sliderReleased.connect(
            lambda: self.reset_slider_cursor(self.speed_slider))

        self.mode_comboBox.currentTextChanged.connect(
            self.change_sliders_for_modes)

        self.open_btn.clicked.connect(self.open_signal)

        self.play_pause_btn.clicked.connect(self.play_pause)
        self.stop_btn.clicked.connect(self.stop)
        self.replay_btn.clicked.connect(self.replay)
        self.reset_view_btn.clicked.connect(self.set_home_view)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        self.speed_slider.valueChanged.connect(
            lambda: self.change_speed(self.speed_slider.value()))
        self.speed_slider.valueChanged.connect(
            lambda: self.speed_lcd.display(self.speed_slider.value()))

        self.original_sound_btn.clicked.connect(
            self.original_sound_player_clicked)
        self.equalized_sound_btn.clicked.connect(
            self.equalized_sound_player_clicked)

        self.window_comboBox.currentTextChanged.connect(
            self.update_smoothing_window)

        # ------------------ sliders ------------------

        for range_slider in self.ranges_sliders.keys():
            range_slider.valueChanged.connect(self.equalize_by_sliders)

        for slices_slider in self.slices_sliders.keys():
            slices_slider.valueChanged.connect(self.equalize_by_sliders)

        for ecg_slider in self.ecg_sliders.keys():
            ecg_slider.valueChanged.connect(self.ecg_equalize)

    def equalized_sound_player_clicked(self):
        self.equalized_sound_player = Player(self.signal, mode='fft')
        self.equalized_sound_player.start()
        self.equalized_sound_player.join()

    def original_sound_player_clicked(self):
        if not self.original_sound_player.is_playing:
            self.original_sound_player.play()
        else:
            self.original_sound_player.pause()

    def reload_after_equalizing(self, ift):
        clear_widgets([self.equalized_signal_viewer,
                       self.frequency_plot_widget,
                       self.equalized_spectro_plot_widget])

        self.equalized_signal_viewer.load_dataset(ift)
        self.equalized_signal_viewer.add_signal()

        self.frequency_plot_item.setData(self.signal.signal_frequencies, 20 *
                                         np.log10(self.signal.signal_modified_amplitudes[
                                                  :len(self.signal.signal_frequencies)]))

        self.frequency_plot_widget.addItem(self.frequency_plot_item)

        for item in self.signal.windows_plots:
            self.frequency_plot_widget.addItem(item)

        plot_spectrogram(self.equalized_spectro_plot_widget,
                         self.signal.equalized_signal_spectrogram)

    def equalize_by_sliders(self):
        if self.sender() in self.ranges_sliders.keys():
            factor = 10 ** (self.sender().value())
            self.signal.equalize(self.smoothing_window, factor,
                                 freqs_range=self.ranges_sliders[self.sender()])
            self.reload_after_equalizing(self.signal.signal_ifft)
        elif self.sender() in self.slices_sliders.keys():
            factor = 10 ** (self.sender().value())
            self.signal.equalize(self.smoothing_window, factor,
                                 slice_name=self.slices_sliders[self.sender()])
            self.reload_after_equalizing(self.signal.signal_istft)

    def ecg_equalize(self):
        factor = 10 ** (self.sender().value())
        peak = np.round(np.max(self.signal.original_signal), 2)

        if self.sender() == self.ecg_arrs_max_f_dict[peak]:
            self.signal.equalize(self.smoothing_window, factor,
                                 freqs_range=self.ecg_sliders[self.sender()])
            self.reload_after_equalizing(self.signal.signal_ifft)

    def open_signal(self):
        options = QFileDialog.Options()
        if self.ecg_mode_selected:
            file_name, _ = QFileDialog.getOpenFileName(self, 'Open Signal to Equalizer', '',
                                                       '*.csv', options=options)
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, 'Open Signal to Equalizer', '',
                                                       '*.wav', options=options)

        if not self.ecg_mode_selected:
            self.signal.import_signal(file_name, "stft")
        else:
            self.signal.import_signal(file_name, "ecg")

        self.signal.signal_slices = animals_slices + musics_slices
        self.original_sound_player = Player(self.signal, mode='fft')
        self.original_sound_player.start()
        self.original_sound_player.pause()

        clear_widgets([self.original_signal_viewer,
                       self.equalized_signal_viewer,
                       self.frequency_plot_widget,
                       self.original_spectro_plot_widget,
                       self.equalized_spectro_plot_widget])

        self.original_signal_viewer.load_dataset(self.signal.original_signal)
        self.equalized_signal_viewer.load_dataset(self.signal.original_signal)
        self.original_signal_viewer.add_signal()
        self.equalized_signal_viewer.add_signal()

        self.play_pause_state = False
        self.play_pause_btn.setIcon(QIcon(f'icons/pause copy.svg'))

        self.frequency_plot_item.setData(self.signal.signal_frequencies, 20 *
                                         np.log10(self.signal.signal_amplitudes[:len(self.signal.signal_frequencies)]))
        self.frequency_plot_widget.addItem(self.frequency_plot_item)

        plot_spectrogram(self.original_spectro_plot_widget,
                         self.signal.original_signal_spectrogram)

        plot_spectrogram(self.equalized_spectro_plot_widget,
                         self.signal.equalized_signal_spectrogram)

    def play_pause(self):
        if self.signal.original_signal.any():
            if self.play_pause_state:
                self.original_signal_viewer.play()
                self.equalized_signal_viewer.play()
                self.play_pause_btn.setIcon(QIcon(f'icons/pause copy.svg'))
                self.play_pause_state = False
            else:
                self.original_signal_viewer.pause()
                self.equalized_signal_viewer.pause()
                self.play_pause_btn.setIcon(QIcon(f'icons/play copy.svg'))
                self.play_pause_state = True
        else:
            QMessageBox.critical(
                None, "Error", "There is no signal opened", QMessageBox.Ok)

    def replay(self):
        if self.signal.original_signal.any():
            self.original_signal_viewer.replay()
            self.equalized_signal_viewer.replay()
            self.play_pause_btn.setIcon(QIcon(f'icons/pause copy.svg'))
            self.play_pause_state = False
            self.original_signal_viewer.home_view()
            self.equalized_signal_viewer.home_view()
        else:
            QMessageBox.critical(
                None, "Error", "There is no signal opened", QMessageBox.Ok)

    def set_home_view(self):
        if self.ecg_mode_selected:
            self.original_signal_viewer.xRange = [0, 1e3]
            self.original_signal_viewer.yRange = [-2, 2]
            self.equalized_signal_viewer.xRange = [0, 1e3]
            self.equalized_signal_viewer.yRange = [-2, 2]
        else:
            self.original_signal_viewer.home_view()
            self.equalized_signal_viewer.home_view()

    def zoom_in(self):
        original_view_box = self.original_plot_widget.getViewBox()
        equalized_view_box = self.equalized_plot_widget.getViewBox()
        original_view_box.scaleBy(s=(0.9, 0.9))
        equalized_view_box.scaleBy(s=(0.9, 0.9))

    def zoom_out(self):
        original_view_box = self.original_plot_widget.getViewBox()
        equalized_view_box = self.equalized_plot_widget.getViewBox()
        original_view_box.scaleBy(s=(1.1, 1.1))
        equalized_view_box.scaleBy(s=(1.1, 1.1))

    def stop(self):
        if self.signal.original_signal.any():
            self.original_signal_viewer.replay()
            self.equalized_signal_viewer.replay()
            self.play_pause_btn.setIcon(QIcon(f'icons/play copy.svg'))
            self.play_pause_state = True
            self.original_signal_viewer.pause()
            self.equalized_signal_viewer.pause()
            self.original_signal_viewer.home_view()
            self.equalized_signal_viewer.home_view()
        else:
            QMessageBox.critical(
                None, "Error", "There is no signal opened", QMessageBox.Ok)

    def change_speed(self, new_speed):
        if new_speed:
            self.original_signal_viewer.rate = new_speed
            self.equalized_signal_viewer.rate = new_speed

    def change_sliders_for_modes(self, text):
        for sliders_frame in self.sliders_frames:
            self.sliders_frames[sliders_frame].setVisible(False)
        self.sliders_frames[text].setVisible(True)
        if text == 'ECG Mode':
            self.ecg_mode_selected = True
            self.original_signal_viewer.xRange = [0, 1e3]
            self.original_signal_viewer.yRange = [-2, 2]
            self.equalized_signal_viewer.xRange = [0, 1e3]
            self.equalized_signal_viewer.yRange = [-2, 2]
        else:
            self.ecg_mode_selected = False

        clear_widgets([self.original_signal_viewer,
                       self.equalized_signal_viewer,
                       self.frequency_plot_widget,
                       self.original_spectro_plot_widget,
                       self.equalized_spectro_plot_widget])

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

    def update_smoothing_window(self, window):
        self.smoothing_window = window.lower()
        if self.smoothing_window == "gaussian":
            pass

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
