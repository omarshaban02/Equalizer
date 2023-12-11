import wfdb
import numpy as np
from scipy.fft import fft, ifft
import matplotlib.pyplot as plt
from scipy.signal import windows, spectrogram

# Function to load and manipulate ECG signal
def load_manipulate_save_ecg(record_name, target_frequency=11, output_csv_name=None):
    # Load the ECG record
    record = wfdb.rdrecord(record_name)
    ecg_signal = record.p_signal[:1300, 0]
    fs = record.fs

    t_ecg = np.arange(0, len(ecg_signal) / fs, 1 / fs)
    plt.figure(figsize=(12, 4))
    plt.plot(t_ecg, ecg_signal, label='Original ECG')
    plt.title(f'ECG Signal - {record_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

    # Perform FFT
    fft_result = fft(ecg_signal)

    # Calculate frequencies
    n = len(fft_result)
    frequencies = np.fft.fftfreq(n, 1 / fs)
    amplitudes = np.abs(fft_result)
    phase = np.angle(fft_result)

    # plt.figure(figsize=(8, 6))
    # plt.plot(frequencies, amplitudes)
    # plt.title('FFT of Original ECG Signal')
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Amplitude')
    # plt.show()

    # Remove a specific frequency range (e.g., 0 to 50 Hz)
    # freq_to_remove = np.where((np.abs(frequencies) >= 0) & (np.abs(frequencies) <= 60))[0]
    # fft_result[freq_to_remove] = 0

    # f_start = 20
    # f_end = 100
    # # get bins corresponding to the frequencies using formula f/f_s = k/N
    # k_start = int((f_start / 125) * n)
    # k_end = int((f_end / 125) * n)
    # # create hamming window for wolf
    # hamming_length = k_end - k_start
    # p = 0
    # hamming_window = windows.hamming(hamming_length) * p
    # amplitudes[k_start:k_end] = hamming_window * amplitudes[k_start:k_end]
    # # for negative part
    # temp_f_start = f_start
    # f_start = -f_end
    # f_end = -temp_f_start
    # k_start = int(n - (-f_start / 125) * n)
    # k_end = int(n - (-f_end / 125) * n)
    # amplitudes[k_start:k_end] = hamming_window * amplitudes[k_start:k_end]
    # fft_result = amplitudes * np.exp(1j * phase)

    # plt.figure(figsize=(8, 6))
    # plt.plot(frequencies, amplitudes)
    # plt.title('FFT of equlized ECG Signal')
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Amplitude')
    # plt.show()

    f_spectro, t_spectro, zxx = spectrogram(ecg_signal, fs=125)
    # use gouraud shading to smooth the colors of the spectrogram

    # plt.pcolormesh(t_spectro, f_spectro[:20], zxx[:20, :], shading='gouraud')
    # plt.xlabel('Time (Seconds)')
    # plt.ylabel('Frequency (Hz)')
    # plt.title('Spectrogram of the ecg')
    # plt.show()

   # # Perform IFFT
    manipulated_ecg = ifft(fft_result).real

    # Plot the original and manipulated ECG signals in the time domain
    t_ecg = np.arange(0, len(ecg_signal) / fs, 1 / fs)

    plt.figure(figsize=(12, 4))
    # plt.plot(t_ecg, ecg_signal, label='Original ECG')
    plt.plot(t_ecg, manipulated_ecg, label=f'Manipulated ECG from {0} to {0}')
    plt.title(f'ECG Signal - {record_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

    # Save the manipulated ECG signal to new files
    if output_csv_name:
        data_to_save = np.column_stack((t_ecg, manipulated_ecg))
        np.savetxt(f"{output_csv_name}.csv", data_to_save, delimiter=",", header="Time (s),Amplitude", comments="")

# Replace 'your_record_name' with the actual record name, e.g., '100', '102', etc.
# Set 'output_csv_name' to save the manipulated ECG signal to new files.
load_manipulate_save_ecg(r'Arrhythmia Database P-Wave Annotations\100', target_frequency=11, output_csv_name='manipulated_record')
