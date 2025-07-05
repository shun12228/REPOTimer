from google.cloud import texttospeech
import os

def synthesize_text(text, filename="output.mp3", credential_path=None):
    if credential_path:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    print(f"音声ファイルを生成しました: {filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("使い方: python synthesize.py 'テキスト' 出力ファイル名.mp3 [認証JSONパス]")
        exit(1)
    text = sys.argv[1]
    filename = sys.argv[2]
    credential_path = sys.argv[3] if len(sys.argv) > 3 else None
    synthesize_text(text, filename, credential_path)
