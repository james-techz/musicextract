from flask_restful import Resource
from flask import request
import os
from fsapi_utils import require_token, os_exception_handle, DATA_DIR
from madmom.features.beats import RNNBeatProcessor
from madmom.features.downbeats import RNNDownBeatProcessor, DBNDownBeatTrackingProcessor
from madmom.features.tempo import TempoEstimationProcessor
from madmom.features.key import CNNKeyRecognitionProcessor

class MusicExtract(Resource):

    @require_token
    @os_exception_handle
    def post(self):
        action = request.json.get('action', '')
        if action == 'extract_music_info':
            if 'wav_file' not in request.json:
                return {"error_message": "'wav_file' not found or invalid"}, 400

            wav_file_path = os.sep.join([DATA_DIR, request.json['wav_file']])
            result = request.json

            beat_act = RNNBeatProcessor()(wav_file_path)
            downbeat_act = RNNDownBeatProcessor()(wav_file_path)
            downbeat_proc = DBNDownBeatTrackingProcessor(beats_per_bar=[4], fps=60)
            tempo_proc = TempoEstimationProcessor(fps=60)
            key_proc = CNNKeyRecognitionProcessor()

            result = {
                "downbeat": downbeat_proc(downbeat_act).tolist(),
                "tempo": tempo_proc(beat_act).tolist(), 
                "key": key_proc(wav_file_path).tolist(),
            }
            return result
        else:
            return {"error_message": "'action' is not defined or invalid"}
