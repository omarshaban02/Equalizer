import scipy.io.wavfile as wav
import numpy as np
from scipy.fft import fft,rfft,rfftfreq,fftfreq,ifft
import matplotlib.pyplot as plt

samplerate = 44100
freq = np.array([
    10,20,30,40,50,60,70,100
   
])

duration = 5
t = np.linspace(0., duration, samplerate * duration, endpoint = False)
# amplitude = np.iinfo(np.int16).max
amplitude = 7e6
data = 0
for i in range(len(freq)):
    sin = np.cos(2. * np.pi * freq[i] * t)
    data += amplitude * sin

wav.write("example.wav", samplerate, data.astype(np.int32))
rate, d = wav.read("example.wav")




fft_result = fft(d)

n = len(fft_result)
frequencies = np.fft.fftfreq(n, 1 / rate)

################################ removing unwanted frequencies
# for poistive part
f_start = 320
f_end = 904
# get bins corresponding to the frequencies using formula f/f_s = k/N
k_start = int((f_start/SAMPLING_RATE) * fft_length) 
k_end = int((f_end/SAMPLING_RATE )* fft_length)
# create hamming window for wolf
hamming_length = k_end-k_start 
p = 0.01
hamming_window = windows.hamming(hamming_length)*p
sound_amplitudes[k_start:k_end] = hamming_window * sound_amplitudes[k_start:k_end]
# for negative part
temp_f_start = f_start
f_start = -f_end
f_end = -temp_f_start
k_start = int(fft_length - (-f_start/SAMPLING_RATE) * fft_length)
k_end = int(fft_length - (-f_end/SAMPLING_RATE )* fft_length)
sound_amplitudes[k_start:k_end] = hamming_window * sound_amplitudes[k_start:k_end]
############################################################################

sound_mod = sound_amplitudes * np.exp( 1j * sound_phases )
###############################################################
magnitudes = np.abs(fft_result)
print(fft_result.shape)
############### show the signal in time domain
manipulated_data = ifft(fft_result).real


plt.figure(figsize=(8, 4))
plt.plot(frequencies, magnitudes)

plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('Frequency Spectrum')
plt.grid()
plt.show()
plt.plot(t[:100], manipulated_data[:100])

plt.xlabel('Time (Sec)')
plt.ylabel('Amplitude')
plt.title('Signal in time domain')
plt.grid()
plt.show()

# for s in sin:
#     plt.plot(t, s)
# plt.show()
