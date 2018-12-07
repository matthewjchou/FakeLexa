#FakeLexa
import speech_recognition as sr
#import pydub
import os
import requests
import json

'''
#Convert M4A to WAV
audio_files = os.listdir('Audio')
for audio_file in audio_files:
	dot_index = audio_file.find('.')
	if audio_file[dot_index + 1] is 'm':
		sound = pydub.AudioSegment.from_mp3(audio_file)
		sound.export(wav_file, format="wav")
		print('dying here?')
		os.remove(audio_file)
'''
app_id = '15dd4592'
app_key = '02514b6fd9e0d3d35a272afc004c73a4'

def remove_nondescript(word_list):
	ignore_words = ['it', 'is', 'a', 'him', 'her', 'be', 'the', 'of', 'are', 'to', 'and', 'such']
	for index, word in enumerate(word_list):
		if word in ignore_words:
			del word_list[index]
	return word_list

def present_tense_change(word):
	length = len(word)
	if word[length - 2:] == 'ed':
		newWord = word[:length - 2]
		return newWord
	else:
		return word

def check_part_of_speech(word):
	word = word.lower()
	with open('parts_speech\\verbs.txt', 'r') as v:
		verb_list = v.readlines()
		if word + '\n' in verb_list:
			v.close()
			return 'v'
		v.close()	

	with open('parts_speech\\nouns.txt', 'r') as n:
		noun_list = n.readlines()
		if word + '\n' in noun_list:
			n.close()
			return 'n'
		n.close()

	with open('parts_speech\\adjectives.txt', 'r') as a:
		adjective_list = a.readlines()
		if word + '\n' in adjective_list:
			a.close()
			return 'a'
		a.close()

	url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/en/' + word.lower()
	r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
	if (r.status_code is not requests.codes.ok):
		print(word)
		#raise Exception('Something broke')
		return
	json_text = json.dumps(r.json(), sort_keys=True, indent=4)
	#print(json_text + '\n')
	json_parsed = json.loads(json_text)

	with open('parts_speech\\' + (json_parsed['results'][0]['lexicalEntries'][0]['lexicalCategory']).lower() + 's.txt', 'a') as j:
		j.write(word + '\n')



recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True;
audio_file = sr.AudioFile('Audio\\HarvardSentences.wav')
with audio_file as source:
	try:
		recognizer.adjust_for_ambient_noise(source, duration=0.5);
		audio = recognizer.record(source)
	except:
		print('nope, not having it')

transcribed_audio = recognizer.recognize_google(audio, show_all=True)

unparsed_json = json.dumps(transcribed_audio, sort_keys=True, indent=4)
print(unparsed_json)
parsed_json = json.loads(unparsed_json)
likely_transcript = parsed_json['alternative'][0]['transcript']
confidence = round(parsed_json['alternative'][0]['confidence'], 4)

if parsed_json['alternative'][0]['confidence'] >= 0.80:
	print('Final Text: ' + likely_transcript + '\nConfidence: ' + str(confidence))
else:
	print('Poor audio:\nBest guess: ' + likely_transcript + '\nConfidence: ' + str(confidence))

'''
Split the string, find the verbs, do action (NLTK? Maybe?)
'''
string_list = likely_transcript.split()
string_list = remove_nondescript(string_list)
print(string_list)

for index, words in enumerate(string_list):
	string_list[index] = present_tense_change(words)

print(string_list)
for words in string_list:
	#Fails on jumped <-- definitely caused by the 'ed' past tense
	print(check_part_of_speech(words))

