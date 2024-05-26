import logging
from flask import Flask, jsonify, request, Response
from flask_cors import CORS # type: ignore
from opentts_client import OpenTTSClient
from google.cloud import speech

app = Flask(__name__)
CORS(app)

open_tts_client = OpenTTSClient("http://localhost:5500")

logging.basicConfig(level=logging.DEBUG)

# Load Google Cloud Speech client
client = speech.SpeechClient.from_service_account_file('key.json')
@app.route('/')
@app.route('/api/voices', methods=['GET'])
def get_available_voices():
    try:
        available_voices = open_tts_client.get_available_voices()
        return jsonify(available_voices)
    except Exception as e:
        app.logger.error(f"Error fetching voices: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tts', methods=['POST'])
def convert_text_to_speech():
    try:
        data = request.json
        app.logger.info(f"Received TTS request data: {data}")
        voice = data.get('voice')
        text = data.get('text')
        if not voice or not text:
            return jsonify({"error": "Voice and text are required"}), 400
        audio_data = open_tts_client.speak_text(voice=voice, text=text)

        if isinstance(audio_data, str):
            audio_data = audio_data.encode('utf-8')

        app.logger.info(f"Audio data type: {type(audio_data)}, length: {len(audio_data)}")

        response = Response(audio_data, mimetype='audio/wav')
        response.headers['Content-Disposition'] = 'attachment; filename="output.wav"'
        response.headers['Content-Type'] = 'audio/wav'
        return response
    except Exception as e:
        app.logger.error(f"Error in TTS conversion: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    logging.debug('Received transcription request')

    # Log the request files and form
    logging.debug(f'Request files: {request.files}')
    logging.debug(f'Request form: {request.form}')

    if 'audio_file' not in request.files:
        logging.debug('No audio file provided')
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio_file']
    if file.filename == '':
        logging.debug('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    language_code = request.form.get('language')
    if not language_code:
        logging.debug('Language not specified')
        return jsonify({'error': 'Language not specified'}), 400

    audio_content = file.read()
    logging.debug('Read audio content successfully')
    audio = speech.RecognitionAudio(content=audio_content)

    # Configuring transcription
    config = speech.RecognitionConfig(
        enable_automatic_punctuation=True,
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code,
        model="default"
    )

    try:
        response = client.recognize(config=config, audio=audio)
    except Exception as e:
        logging.error(f'Error during transcription: {e}')
        return jsonify({'error': str(e)}), 500

    transcription = ''
    for result in response.results:
        transcription += result.alternatives[0].transcript

    if not transcription:
        logging.debug('No transcription available')
        return jsonify({'error': 'No transcription available'}), 500

    logging.debug(f'Transcription successful: {transcription}')
    return jsonify({'transcription': transcription}), 200

if __name__ == '__main__':
    app.run(debug=True)
