import os
from pydub import AudioSegment
from pydub.silence import detect_silence
import subprocess as sp
import re
import csv


if os.name == "nt":
	FFMPEG_BIN = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
	AudioSegment.converter = FFMPEG_BIN
else:
	FFMPEG_BIN = "ffmpeg"

print "Syncer 2.2"

if not os.path.exists("Result"):
	os.makedirs("Result")

if not os.path.exists("Wav"):
	os.makedirs("Wav")


iter = 0
for wave in os.listdir("Audio"):
	iter += 1
	if wave.endswith(".al"):
		digit = re.findall('\d+', wave.split('.')[0])[-1]
		cmd = '{} -y -loglevel fatal -f alaw -ar 8000 -i Audio/{}  Wav/{}.wav'.format(FFMPEG_BIN, wave, digit)
		print iter, '-> to wav'
		sp.call(cmd)
print 'Converting from alaw to wav finished'


output = AudioSegment.silent(duration = len(os.listdir("Wav")) * 160 + 20000)

gaps = -1
iter = 0
iter_timestart = []
start = int(os.listdir("Wav")[0].split('.')[0])
previous = start
for wave in os.listdir("Wav"):
	iter += 1
	if wave.endswith(".wav"):
		sound = AudioSegment.from_file("Wav/{}".format(wave), format="wav")
		wave = int(re.findall('\d+', wave.split('.')[0])[-1])
		tick = wave - start
		timestart = tick * 40
		iter_timestart.append(iter : timestart)
		if wave - previous != 4:
			gaps += 1
			print "Gap time in milliseconds: ", timestart
		previous = wave
		output = output.overlay(sound, position=timestart)
		print iter, '-> to Sum.wav'

tick_based_scale = open('tick_based_scale.csv', 'wb')
wr = csv.writer(tick_based_scale, dialect='excel')
wr.writerow(iter_timestart)

sil = detect_silence(output, min_silence_len=5000, silence_thresh=-26)
output = output[:int(sil[0][0])]
output.export("Result/Sum.wav", format="wav")

print "Sum.wav is ready. Gaps found:", gaps