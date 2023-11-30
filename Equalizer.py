import pyaudio
import wave
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import stft, istft
from scipy.signal import windows, spectrogram
import matplotlib.pyplot as plt
import pyqtgraph as pg


class Signal(object):
    def __init__(self):
        self.original_signal = np.ndarray([])
        self.signal_fft = np.ndarray([])
        self.signal_ifft = np.ndarray([])
        self.signal_frequencies = np.ndarray([])
        self.signal_amplitudes = np.ndarray([])
        self.signal_phases = np.ndarray([])
        self.signal_sound = None
        self.signal_spectrogram = None
        self.sampling_frequency = None
        self.duration = None
        self.nsamples = None
        self.components_data = np.ndarray([])
        self.signal_plot = pg.PlotDataItem()
        self.original_signal_plot = pg.PlotDataItem()
        self.equalized_signal_plot = pg.PlotDataItem()
        self.original_signal_spectrogram = pg.PlotDataItem()
        self.equalized_signal_spectrogram = pg.PlotDataItem()

    def equalize(self, window_type, frequencies, equalizing_factor):
        pass

    def import_signal(self):
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def replay(self):
        pass

    def change_speed(self, speed_factor):
        pass
