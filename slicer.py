import os, re, csv, ast
import subprocess as sp
from pydub import AudioSegment
from pydub.silence import detect_silence


if os.name == "nt":
	FFMPEG_BIN = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
	AudioSegment.converter = FFMPEG_BIN
else:
	FFMPEG_BIN = "ffmpeg"

print "Slicer 1.0"

#Create necessary folders if they don't exist
necessary_folders = ["Original_track", "Original_track/slices", "Result", "Video"]

for folder in necessary_folders:
	if not os.path.exists(folder):
		os.makedirs(folder)

#Convert .al to .wav
cmd = '{} -y -loglevel fatal -f alaw -ar 8000 -i Original_track/original.al Original_track/original.wav'.format(FFMPEG_BIN)
sp.call(cmd)
#Open original .wav file and slice it to the 160-length pieces
original = AudioSegment.from_file("Original_track/original.wav", format="wav")

iter = 0
for i in range(0, len(original), 160):
	iter += 1
	orig_slice = original[i:i+160]
	orig_slice.export("Original_track/slices/{}.wav".format(iter), format="wav")

#Open existent .csv file, reading dict data {filenumber: timestart}
li = []
with open('tick_based_scale.csv', 'rb') as f:
	reader = csv.reader(f)
	for row in reader:
		li = row

#We know full length of future audio, so let's create silent track with that length
track = AudioSegment.silent(duration=ast.literal_eval(li[-1]).items()[0][1])

#Now we have tick-based timestamps and qualitative pieces of original file. Let's combine them!
for i in range(0, len(li)):
	for key in ast.literal_eval(li[i]):
		try:
			sound = AudioSegment.from_file("Original_track/slices/{}.wav".format(i+1), format="wav")
			timestart = ast.literal_eval(li[i])[key]
			track = track.overlay(sound, position=timestart)
		except IOError:
			continue
track.export("Result/Final.wav", format="wav")
print("Final Audio done")

#Now we have Final audio. Let's combine it with video from folder "Video"
audio_name = "Result/Final.wav"
video_name = [f for f in os.listdir("Video")]
video_name = video_name[0]
result_name = os.path.splitext(video_name)[0]
cmd = '{} -y -loglevel fatal -i {} -i Video/{} -c:a pcm_s16le Result/{}.mov'.format(FFMPEG_BIN, audio_name, video_name, result_name)
sp.call(cmd)
print("Video done")