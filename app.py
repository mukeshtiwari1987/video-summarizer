import gradio as gr
import whisper
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from moviepy import VideoFileClip

def transcribe_and_summarize(video_path):
    # Extract audio from video
    clip = VideoFileClip(str(video_path))
    audio_path = "temp.mp3"
    clip.audio.write_audiofile(audio_path)
    clip.close()

    # Transcribe audio
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
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

interface = gr.Interface(fn=transcribe_and_summarize, inputs="video", outputs="text")
interface.launch()