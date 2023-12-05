import pyaudio
import wave
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import stft, istft
from scipy.signal import windows, spectrogram
import matplotlib.pyplot as plt
import pyqtgraph as pg

class Player(object):
    def __init__(self, signal):
        self._signal = signal
        self._pyaudio = pyaudio.PyAudio()
        self._stream = None
        self._chunk = 1024
        self._is_playing = True
        self._data = None
        self._current_index = 0
        if signal.mode == 'fft':
            self._data = np.array(signal.signal_ifft ,dtype=np.int16)
        elif signal.mode == 'stft':
            self._data = np.array(signal.signal_istft ,dtype=np.int16)
        else:
            raise ValueError('Invalid signal mode')
        
        self._current_bytes = None
        
    @property
    def data(self):
        return self._data
    
    @property
    def current_index(self):
        return self._current_index
    
    @current_index.setter
    def current_index(self,value):
        self._current_index = value
    
    @property
    def signal(self):
        return self._signal
    
    @signal.setter
    def signal(self,value):
        self._signal = value

    @property
    def is_playing(self):
        return self._is_playing
    @is_playing.setter
    def is_playing(self,value):
        self._is_playing = value
    @property  
    def pyaudio(self):
        return self._pyaudio
    @pyaudio.setter
    def pyaudio(self,value):
        self._pyaudio = value
    @property
    def stream(self):
        return self._stream
    @stream.setter
    def stream(self,value):
        self._stream = value
    @property
    def chunk(self):
        return self._chunk
    @chunk.setter
    def chunk(self,value):
        self._chunk = value
    @property
    def current_bytes(self):
        return self._current_bytes
    @current_bytes.setter
    def current_bytes(self,value):
        self._current_bytes = value


    def play(self):
        self.is_playing= True
        if self.stream is not None:
            self.stop()
        self.stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(self.signal.sample_width),
                                        channels=self.signal.nchannels,
                                        rate=self.signal.sampling_rate,
                                        output=True)
        while self.is_playing:
            self.advance()
            

    def resume(self):
        self.is_playing= True

    def pause(self):
        self.is_playing= False

    def replay(self):
        if self.stream is not None:
            self.stop()
    def stop(self):
        self.pause()
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()
        

    def advance(self):
        start = self.current_index
        end = self.current_index + self.chunk
        if end >= len(self.data)-1:
            self.current_bytes = self.data[start:].tobytes()
            self.current_index = len(self.data)-1
            self.stream.write(self.current_bytes)
            self.stop()
        else:
            self.current_bytes = self.data[start:end].tobytes()
            self.current_index = end
            self.stream.write(self.current_bytes)
            

class Signal(object):
    def __init__(self):
        self._original_signal = None
        self._signal_fft = None
        self._signal_ifft = None
        self._signal_stft = None
        self._signal_istft = None
        self._n_time_segments = None
        self._signal_zxx = None
        self._signal_stft_freqs = None
        self._mode = 'fft' # or 'stft'
        self._nchannels = 1 # monophonic sound or stereo sound
        self._sound_type = 'monophonic' # mono or stereo
        self._sampling_rate = None
        self._signal_frequencies = None
        self._signal_amplitudes = None
        self._signal_phases = None
        self._duration = None
        self._number_of_samples = None
        self._sample_width = None
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
        self._signal_fft  = self.signal_amplitudes * np.exp( self.signal_phases * 1j)
        return self._signal_fft

    @signal_fft.setter
    def signal_fft(self, value):
        self._signal_fft = value
    

    @property
    def signal_ifft(self):
        self._signal_ifft = ifft(self.signal_fft).real
        return self._signal_ifft
    @property
    def signal_istft(self):
        _, self._signal_istft = istft(self.signal_zxx)
        return self._signal_istft
    @property
    def number_of_samples(self):
        self._number_of_samples = len(self.original_signal)/self.nchannels
        return self._number_of_samples
    @property
    def signal_stft_freqs(self):
        self._signal_stft_freqs =self.signal_stft[0]
        return self._signal_stft_freqs
    @property
    def duration(self):
        self._duration = self.number_of_samples / self.sampling_rate
        return self._duration
    @property
    def sample_width(self):
        return self._sample_width
    @sample_width.setter
    def sample_width(self, value):
        self._sample_width = value
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

    @property
    def nchannels(self):
        return self._nchannels
    
    @nchannels.setter
    def nchannels(self, value):
        if value == 1:
            self._sound_type = 'monophonic'
        elif value == 2:
            self._sound_type = 'stereo'
        else:
            raise ValueError('Invalid value')
        self._nchannels = value
    @property
    def sound_type(self):
        return self._sound_type
    @sound_type.setter
    def sound_type(self, value):
        raise ValueError('read-only property')
    @property
    def mode(self):
        return self._mode
    @mode.setter
    def mode(self, value):
        self._mode = value
    @property
    def signal_stft(self):
        return self._signal_stft
    @signal_stft.setter
    def signal_stft(self, value):
        self._signal_stft = value
    @property
    def n_time_segments(self):
        return self._n_time_segments
    @n_time_segments.setter
    def n_time_segments(self, value):
        self._n_time_segments = value
    @property
    def signal_zxx(self):
        return self._signal_zxx
    @signal_zxx.setter
    def signal_zxx(self, value):
        self._signal_zxx = value


    def equalize(self, window_type, equalizing_factor,freqs_range = None, slice_name = None):
        # apply stft
        if slice_name is not None:
            for slice in self.components_data:
                if slice[0] == slice_name:
                    freqs_indices = slice[1]
                    time_range = slice[2]
                    window = 0
                    window_length = len(freqs_indices)
                    if window_type == 'hamming':
                        window = windows.hamming(window_length) * equalizing_factor
                    elif window_type == 'hanning':
                        window = windows.hann(window_length) * equalizing_factor
                    elif window_type == 'gaussian':
                        window = windows.gaussian(window_length) * equalizing_factor
                    elif window_type == 'rectangle':
                        window = np.ones(window_length)*equalizing_factor
                    else:
                        raise ValueError('Unknown window')
                    
                    n_start = int(time_range[0]* self.n_time_segments/self.duration)
                    n_end = int(time_range[1]* self.n_time_segments/self.duration)
                    if n_end < 0 : n_end = -1
                    for i in freqs_indices:
                        self.signal_zxx[i, n_start:n_end] *= window[i]
        # apply fft
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
            else:
                raise ValueError('Unknown window')

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
    
    def open(self,file,mode= 'fft'):
        file = wave.open(file, "rb")
        nframes = file.getnframes()
        data = file.readframes(nframes)
        self.original_signal = np.frombuffer(data, dtype=np.int16)
        self.sampling_rate = file.getframerate()
        self.sample_width = file.getsampwidth()
        
        if mode == 'fft':
            self.mode = 'fft'
            sig_fft = fft(self.original_signal)
            self.signal_amplitudes = np.abs(sig_fft)
            self.signal_phases = np.angle(sig_fft)
           
        elif mode == 'stft':
            self.mode = 'stft'
            sig_fft = fft(self.original_signal)
            self.signal_amplitudes = np.abs(sig_fft)
            self.signal_phases = np.angle(sig_fft)
            self.signal_stft = stft(self.original_signal,fs=self.sampling_rate)
            self.signal_zxx = self.signal_stft[2]
            self.n_time_segments = len(self.signal_stft[1])
            
        else:
            raise ValueError('Invalid mode')
        
            
sig = Signal()
sig.open(r"signal_files/animals.wav", mode='stft')
p = Player(sig)
p.play()
p.stop()
        
