import pyaudio  
import wave  
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft, ifft,fftfreq
import matplotlib.pyplot as plt
#define stream chunk   
chunk = 1024  
  
#open a wav format music  
f = wave.open(r"signal_files/animals.wav","rb")  
#instantiate PyAudio  
p = pyaudio.PyAudio()  
#open stream  
stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                channels = f.getnchannels(),  
                rate = f.getframerate(),  
                output = True)  
#read data  
data = f.readframes(chunk)  

sound = np.frombuffer(data, dtype=np.int16)
SAMPLING_RATE = f.getframerate()
#play stream  
while data:  
    stream.write(data)  
    data = f.readframes(chunk)
    sound  = np.append(sound,np.frombuffer(data, dtype=np.int16))
    
    

#stop stream  
stream.stop_stream()  
stream.close()  
  
#close PyAudio  
p.terminate()  

###################################################### editing sound  ################################
N = len(sound)
duration = N/SAMPLING_RATE
t = np.linspace(0,duration,N)
# show signal in time domain
plt.figure(figsize=(8,6))
plt.plot(t,sound)
plt.show()
# convert the signal to frequency domain
sound_fft = fft(sound)
fft_length = len(sound_fft)
sound_frequencies = fftfreq(fft_length, 1 / SAMPLING_RATE)
sound_amplitudes = np.abs(sound_fft)
sound_phases = np.angle(sound_fft)
# show the amplitude spectrum
plt.figure(figsize=(8,6))
plt.plot(sound_frequencies,sound_amplitudes)
plt.show()
##################################################### processing part ###############################


############################### remove wolf sound #############################
# for poistive part
f_start = 320
f_end = 904
n_start = int((f_start/SAMPLING_RATE) * fft_length)
n_end = int((f_end/SAMPLING_RATE )* fft_length)
sound_amplitudes[n_start:n_end] = 0
# for negative part
temp_f_start = f_start
f_start = -f_end
f_end = -temp_f_start
n_start = int(fft_length - (-f_start/SAMPLING_RATE) * fft_length)
n_end = int(fft_length - (-f_end/SAMPLING_RATE )* fft_length)
sound_amplitudes[n_start:n_end] = 0
############################################################################

sound_mod = sound_amplitudes * np.exp( 1j * sound_phases )
###############################################################
# show the amplitude spectrum

plt.figure(figsize=(8,6))
plt.plot(sound_frequencies,sound_amplitudes)
plt.show()

# convert the signal to time domain
manipulated_sound = ifft(sound_mod).real

# show signal in time domain
plt.figure(figsize=(8,6))
plt.plot(t,manipulated_sound)
plt.show()
# write the signal in wav file
wav.write("output_sound.wav",SAMPLING_RATE,manipulated_sound.astype(np.int16))
