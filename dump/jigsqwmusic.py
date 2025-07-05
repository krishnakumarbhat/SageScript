import librosa

y, sr = librosa.load('/home/pope/Desktop')
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
print("Tempo:", tempo)
print("Beat frames:", beats)
