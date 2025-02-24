import gradio as gr
import whisper
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from moviepy import VideoFileClip
import numpy as np
from scipy.signal import resample
from moviepy.audio.io import AudioFileClip

def transcribe_and_summarize(video_path):
    # Extract audio from video
    clip = VideoFileClip(str(video_path))
    audio_path = "temp.mp3"
    clip.audio.write_audiofile(audio_path)
    clip.close()

    # Transcribe audio
    audio_array = load_and_resample(audio_path)
    model = whisper.load_model("base")
    result = model.transcribe(audio_array)
    transcript = result["text"]

    # Summarize transcript
    parser = PlaintextParser.from_string(transcript, Tokenizer("english"))
    document = parser.doc
    summarizer = LexRankSummarizer(Stemmer("english"))
    summary = summarizer(document, 5)  # 5 sentences
    summary_text = ' '.join(str(sentence) for sentence in summary)

    # Clean up
    import os
    os.remove(audio_path)

    return summary_text

def load_and_resample(audio_path, target_sr=16000):
    audio_clip = AudioFileClip(audio_path)
    audio_array = audio_clip.to_soundarray()
    sampling_rate = audio_clip.fps

    # Convert to mono if stereo
    if audio_array.shape[0] > 1:
        audio_array = np.mean(audio_array, axis=0)

    # Resample if necessary
    if sampling_rate != target_sr:
        new_length = int(len(audio_array) * (target_sr / sampling_rate))
        audio_array = resample(audio_array, new_length)

    return audio_array

interface = gr.Interface(fn=transcribe_and_summarize, inputs="video", outputs="text")
interface.launch(share=True,server_name='0.0.0.0')