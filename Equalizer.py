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
        self._original_signal = None
        self._signal_fft = None
        self._signal_ifft = None
        self._signal_stft = None
        self._signal_istft = None
        self._n_time_segments = None
        self._signal_zxx = None
        self._mode = 'fft' # or 'stft'
        self._signal_stft_freqs = None
        self._sampling_rate = None
        self._signal_frequencies = None
        self._signal_amplitudes = None
        self._signal_phases = None
        self._duration = None
        self._number_of_samples = None
        self._signal_sound = None 
        self._stream = None 
        self._signal_spectrogram = None
        self._components_data = None
        self.original_signal_frequency_plot = None
        self.original_signal_plot = None
        self.equalized_signal_plot = None
        self.original_signal_spectrogram = None
        self.equalized_signal_spectrogram = None

    @property
    def original_signal(self):
        return self._original_signal

    @original_signal.setter
    def original_signal(self, value):
        self._original_signal = value
        

    @property
    def signal_fft(self):
        self._signal_fft  = self.signal_amplitudes * np.exp(self.signal_phases * 1j)
        return self._signal_fft

    @signal_fft.setter
    def signal_fft(self, value):
        self._signal_fft = value
    

    @property
    def signal_ifft(self):
        self._signal_ifft = ifft(self.signal_fft).real
        return self._signal_ifft

    @property
    def number_of_samples(self):
        self._number_of_samples = len(self.original_signal)
        return self._number_of_samples

    @property
    def duration(self):
        self._duration = self.number_of_samples / self.sampling_rate
        return self._duration
    
    @property
    def sampling_rate(self):
        return self._sampling_rate
    
    @sampling_rate.setter
    def sampling_rate(self, value):
        self._sampling_rate = value

    @property
    def signal_frequencies(self):
        self._signal_frequencies = fftfreq(self.number_of_samples, 1 / self.sampling_rate)
        return self._signal_frequencies


    @property
    def signal_amplitudes(self):
        return self._signal_amplitudes

    @signal_amplitudes.setter
    def signal_amplitudes(self, value):
        self._signal_amplitudes = value

    @property
    def signal_phases(self):
        return self._signal_phases

    @signal_phases.setter
    def signal_phases(self, value):
        self._signal_phases = value

    @property
    def spectrogram(self):
       self._signal_spectrogram = spectrogram(self.signal_ifft,fs = self.sampling_rate)
       return self._signal_spectrogram

    @property
    def components_data(self):
        return self._components_data
    
    @components_data.setter
    def components_data(self, value):
        self._components_data = value


    def equalize(self, window_type, equalizing_factor,freqs_range = None, slice_name = None):
        if slice_name is not None:
            for slice in self.components_data:
                if slice[0] == slice_name:
                    freqs_indices = slice[1]
                    time_range = slice[2]
                    window = 0
                    window_length = 0
                    if window_type == 'hamming':
                        window = windows.hamming(window_length) * equalizing_factor


        if freqs_range is not None:
            f_start = freqs_range[0]
            f_end = freqs_range[1]
            # get bins corresponding to the frequencies using formula f/f_s = k/N
            k_start = int((f_start / self.sampling_rate) * self.number_of_samples)
            k_end = int((f_end / self.sampling_rate) * self.number_of_samples)
            # create hamming window for wolf
            window_length = k_end - k_start
            window = 0
            if window_type == 'hamming':
                window = windows.hamming(window_length) * equalizing_factor
            elif window_type == 'hanning':
                window = windows.hann(window_length) * equalizing_factor
            elif window_type == 'gussian':
                window = windows.gaussian(window_length) * equalizing_factor
            elif window_type == 'rectangle':
                window =  equalizing_factor

            self.signal_amplitudes[k_start:k_end] = window * self.signal_amplitudes[k_start:k_end]
            # for negative part
            temp_f_start = f_start
            f_start = -f_end
            f_end = -temp_f_start
            k_start = int(self.number_of_samples - (-f_start / self.sampling_rate) * self.number_of_samples)
            k_end = int(self.number_of_samples - (-f_end / self.sampling_rate) * self.number_of_samples)
            self.signal_amplitudes[k_start:k_end] = window * self.signal_amplitudes[k_start:k_end]

    def import_signal(self):
        pass
    
    def open(self,file):
        file = wave.open(file, "rb")
        nframes = file.getnframes()
        data = file.readframes(nframes)
        self.original_signal = np.frombuffer(data, dtype=np.int16)
        self.sampling_rate = file.getframerate()
        self.signal_fft  = fft(self.original_signal)
        self.signal_amplitudes = np.abs(self.signal_fft)
        self.signal_phases = np.angle(self.signal_fft)

        
