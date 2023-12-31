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
f = wave.open(r"signal_files/musics.wav", "rb")
# instantiate PyAudio
p = pyaudio.PyAudio()
# open stream
stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                channels=f.getnchannels(),
                rate=f.getframerate(),
                output=True)
# read data
data = f.readframes(chunk)
nchannels = f.getnchannels()
sound = np.frombuffer(data, dtype=np.int16)
SAMPLING_RATE = f.getframerate()
N = f.getnframes()
duration = N / SAMPLING_RATE
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

# channels = np.asarray(np.split(sound,nchannels,axis=0),dtype=np.int16)

###################################################### editing sound  ################################


t = np.linspace(0, duration, N, endpoint=False)
# # show signal in time domain
# plt.figure(figsize=(8, 6))
# plt.plot(t, sound)
# #plt.show()
# # convert the signal to frequency domain
# sound_fft = fft(sound)

# fft_length = len(sound_fft)
# sound_frequencies = fftfreq(fft_length, 1 / SAMPLING_RATE)
# sound_amplitudes = np.abs(sound_fft)
# sound_phases = np.angle(sound_fft)
# # show the amplitude spectrum
# plt.figure(figsize=(8, 6))
# plt.plot(sound_frequencies, 20 * np.log10(sound_amplitudes))
# #plt.show()
# # show the spectrogram to analyze the sound and see how frequencies and amplitudes change over time
# # zxx is the square magnitude of STFT (Short-Time Fourier Transform)
# f_spectro, t_spectro, zxx = spectrogram(sound, fs=SAMPLING_RATE)
# # use gouraud shading to smooth the colors of the spectrogram

# plt.pcolormesh(t_spectro, f_spectro[:20], zxx[:20,:], shading='gouraud')
# plt.xlabel('Time (Seconds)')
# plt.ylabel('Frequency (Hz)')
# plt.title('Spectrogram of the sound')
# plt.show()

##################################################### processing part ###############################

freqs, times, sxx = stft(sound, fs=SAMPLING_RATE)

freq_components = [
    # ('flute', [i for i in range(1, 4)], [1, 3.5]),
    # ('flute', [i for i in range(1, 4)], [4, 7]),
    ('guitar', [i for i in range(1, 4)], [7.5, 9]),
    # ('piano', [i for i in range(0, 9)], [0, 4.5]),
    # ('piano', [0, 3, 5, 6, 7, 8, 9], [0, 4.5]),
    # ('trumpet', [i for i in range(4, 18)], [5.5, 7.5]),
]
for animal_tuple in freq_components:
    n_start = int(animal_tuple[2][0] * times.shape[0] / duration)
    n_end = int(animal_tuple[2][1] * times.shape[0] / duration)
    if n_end < 0:
        n_end = -1
    for i in animal_tuple[1]:
        sxx[i, n_start:n_end] = 0
print(freqs)

_, modified_sound = istft(sxx, fs=SAMPLING_RATE)

modified_channels = np.array(np.split(modified_sound, nchannels, axis=0), dtype=np.int16)
############################### remove wolf sound #############################
# for poistive part
# f_start = 320
# f_end = 904
# # get bins corresponding to the frequencies using formula f/f_s = k/N
# k_start = int((f_start / SAMPLING_RATE) * fft_length)
# k_end = int((f_end / SAMPLING_RATE) * fft_length)
# # create hamming window for wolf
# hamming_length = k_end - k_start
# p = 0.01
# hamming_window = windows.hamming(hamming_length) * p
# sound_amplitudes[k_start:k_end] = hamming_window * sound_amplitudes[k_start:k_end]
# # for negative part
# temp_f_start = f_start
# f_start = -f_end
# f_end = -temp_f_start
# k_start = int(fft_length - (-f_start / SAMPLING_RATE) * fft_length)
# k_end = int(fft_length - (-f_end / SAMPLING_RATE) * fft_length)
# sound_amplitudes[k_start:k_end] = hamming_window * sound_amplitudes[k_start:k_end]
# ############################################################################

# sound_mod = sound_amplitudes * np.exp(1j * sound_phases)
# ###############################################################
# # show the amplitude spectrum

# plt.figure(figsize=(8, 6))
# plt.plot(sound_frequencies, 20 * np.log10(sound_amplitudes))
# plt.show()

# convert the signal to time domain
# manipulated_sound = ifft(sound_mod).real

# show signal in time domain
# plt.figure(figsize=(8, 6))
# plt.plot(t, manipulated_sound)
# plt.show()

# write the signal in wav file
bitrate = 16

with wave.open("output_music_mode.wav", "wb") as out_file:
    out_file.setframerate(SAMPLING_RATE)
    out_file.setnchannels(nchannels)
    out_file.setsampwidth(bitrate // 8)
    for channel in modified_channels:
        out_file.writeframes(channel.tobytes())
