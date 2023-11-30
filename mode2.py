import pyaudio
import wave
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import stft, istft
from scipy.signal import windows, spectrogram
import matplotlib.pyplot as plt

# define stream chunk
chunk = 1024

# open a wav format music
f = wave.open(r"signal_files/animals.wav", "rb")
# instantiate PyAudio
p = pyaudio.PyAudio()
# open stream
stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                channels=f.getnchannels(),
                rate=f.getframerate(),
                output=True)
# read data
data = f.readframes(chunk)

sound = np.frombuffer(data, dtype=np.int16)
SAMPLING_RATE = f.getframerate()
# play stream
while data:
    stream.write(data)
    data = f.readframes(chunk)
    sound = np.append(sound, np.frombuffer(data, dtype=np.int16))

# stop stream
stream.stop_stream()
stream.close()

# close PyAudio
p.terminate()

###################################################### editing sound  ################################

N = len(sound)
duration = N / SAMPLING_RATE
t = np.linspace(0, duration, N, endpoint=False)
# show signal in time domain
plt.figure(figsize=(8, 6))
plt.plot(t, sound)
plt.show()
# convert the signal to frequency domain
sound_fft = fft(sound)

fft_length = len(sound_fft)
sound_frequencies = fftfreq(fft_length, 1 / SAMPLING_RATE)
sound_amplitudes = np.abs(sound_fft)
sound_phases = np.angle(sound_fft)
# show the amplitude spectrum
plt.figure(figsize=(8, 6))
plt.plot(sound_frequencies, 20 * np.log10(sound_amplitudes))
plt.show()
# show the spectrogram to analyze the sound and see how frequencies and amplitudes change over time
# zxx is the square magnitude of STFT (Short-Time Fourier Transform)
f_spectro, t_spectro, zxx = spectrogram(sound, fs=SAMPLING_RATE)
# use gouraud shading to smooth the colors of the spectrogram

plt.pcolormesh(t_spectro, f_spectro[:20], zxx[:20, :], shading='gouraud')
plt.xlabel('Time (Seconds)')
plt.ylabel('Frequency (Hz)')
plt.title('Spectrogram of the sound')
plt.show()

##################################################### processing part ###############################
freqs, times, sxx = stft(sound, fs=SAMPLING_RATE)

n_start = int(5 * 2575 / duration)
n_end = int(7 * 2575 / duration)
components_indices = [i for i in range(6, 15)]
for i in components_indices:
    sxx[i, n_start:] *= 0
print(freqs)
_, signal_modified = istft(sxx, fs=SAMPLING_RATE)

############################### remove wolf sound #############################
# for poistive part
f_start = 320
f_end = 904
# get bins corresponding to the frequencies using formula f/f_s = k/N
k_start = int((f_start / SAMPLING_RATE) * fft_length)
k_end = int((f_end / SAMPLING_RATE) * fft_length)
# create hamming window for wolf
hamming_length = k_end - k_start
p = 0.01
hamming_window = windows.hamming(hamming_length) * p
sound_amplitudes[k_start:k_end] = hamming_window * sound_amplitudes[k_start:k_end]
# for negative part
temp_f_start = f_start
f_start = -f_end
f_end = -temp_f_start
k_start = int(fft_length - (-f_start / SAMPLING_RATE) * fft_length)
k_end = int(fft_length - (-f_end / SAMPLING_RATE) * fft_length)
sound_amplitudes[k_start:k_end] = hamming_window * sound_amplitudes[k_start:k_end]
############################################################################

sound_mod = sound_amplitudes * np.exp(1j * sound_phases)
###############################################################
# show the amplitude spectrum

plt.figure(figsize=(8, 6))
plt.plot(sound_frequencies, 20 * np.log10(sound_amplitudes))
plt.show()

# convert the signal to time domain
manipulated_sound = ifft(sound_mod).real

# show signal in time domain
plt.figure(figsize=(8, 6))
plt.plot(t, manipulated_sound)
plt.show()
# write the signal in wav file
wav.write("output_sound.wav", SAMPLING_RATE, signal_modified.astype(np.int16))