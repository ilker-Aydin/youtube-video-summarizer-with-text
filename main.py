import yt_dlp as youtube_dl
import speech_recognition as sr
from os import path
from pydub import AudioSegment
from pydub.utils import which
from transformers import pipeline
import wave
import json
from vosk import Model, KaldiRecognizer


# FFmpeg ve FFprobe yollarını ayarla
AudioSegment.converter = r"C:\Users\salda\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin\ffmpeg"  # veya "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffmpeg = r"C:\Users\salda\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin\ffmpeg"     # veya "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\salda\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin\ffprobe"
print("FFmpeg:", which("ffmpeg"))
print("FFprobe:", which("ffprobe"))
# FFmpeg ve FFprobe yollarını ayarla
'''
AudioSegment.converter = "C:/ffmpeg/ffmpeg-n7.0-latest-win64-lgpl-shared-7.0/bin/ffmpeg"  # veya "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "C:/ffmpeg/ffmpeg-n7.0-latest-win64-lgpl-shared-7.0/bin/ffmpeg"     # veya "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmpeg/ffmpeg-n7.0-latest-win64-lgpl-shared-7.0/bin/ffprobe"   # veya "C:/ffmpeg/bin/ffprobe.exe"
'''
video_url = input("input url: ")
video_bilgisi = youtube_dl.YoutubeDL().extract_info(url=video_url, download=False)

file_name = "gelen.mp3"

settings = {
    'format': 'bestaudio[ext=m4a]/bestaudio',
    'keepvideo': False,
    'outtmpl': file_name
}


with youtube_dl.YoutubeDL(settings) as ydl:
    ydl.download([video_bilgisi['webpage_url']])

print(f"İndirme tamamlandı... {file_name}")



src = "gelen.mp3"
dst = "test.wav"

# MP3 dosyasını yükle
sound = AudioSegment.from_file(src)
if sound.channels > 1:
    sound = sound.set_channels(1)
# WAV formatında kaydet
sound.export(dst, format="wav")


def ses_dosyasini_metne_donustur_vosk(dosya_yolu):
    model = Model(r"C:\Users\salda\Documents\vosk-model-small-tr-0.3")  # Vosk model yolunu burada belirtin
    wf = wave.open(dosya_yolu, "rb")

    if wf.getnchannels() != 1:
        raise ValueError("WAV dosyası mono olmalıdır.")  # Vosk mono ses dosyalarını işler

    recognizer = KaldiRecognizer(model, wf.getframerate())
    results = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            results.append(result['text'])

    final_result = json.loads(recognizer.FinalResult())
    results.append(final_result['text'])

    return " ".join(results)


print(f"{file_name} dosyası başarıyla wav dosyasına dönüştürüldü.")
text = ses_dosyasini_metne_donustur_vosk(dosya_yolu="test.wav")

# Metni bir .txt dosyasına kaydet
with open("metin_dosyasi.txt", "w", encoding="utf-8") as f:
    f.write(text)

print(f"{file_name} dosyası başarıyla wav dosyasına dönüştürüldü ve metin 'metin_dosyasi.txt' dosyasına kaydedildi.")
x= len("metin_dosyası.txt")
print(x)

def summarize_large_text(text, chunk_size=1000, overlap=100, max_length=150):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summaries = []

    # Splitting text into chunks with overlap
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunk_length = len(chunk)
        effective_max_length = min(max_length, chunk_length // 3)

        summary = summarizer(chunk, max_length=effective_max_length, clean_up_tokenization_spaces=False)[0]['summary_text']
        summaries.append(summary)

    return " ".join(summaries)

# Read and summarize the text in chunks
with open("metin_dosyasi.txt", "r", encoding="utf-8") as f:
    text = f.read()

summary_text = summarize_large_text(text)

# Save the summarized text
with open("ozet_dosyasi.txt", "w", encoding="utf-8") as f:
    f.write(summary_text)

print("Özet 'ozet_dosyasi.txt' dosyasına kaydedildi.")


