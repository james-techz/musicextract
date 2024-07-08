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
        downbeat_conf = request.json.get('downbeat_conf', {})
        downbeat_conf_defaults = {
            'beats_per_bar': 4,
            'min_bpm': 60,
            'max_bpm': 120,
            'num_tempi': 60,
            'transition_lambda': 100,
            'observation_lambda': 16,
            'threshold': 0.1,
            'correct': True,
            'fps': 100,
        }
        downbeat_conf_final = downbeat_conf_defaults | downbeat_conf

        tempo_conf = request.json.get('tempo_conf', {})
        tempo_conf_defaults = {            
            'method': 'comb',
            'min_bpm': 60,
            'max_bpm': 120,
            'hist_buffer': 6,
            'fps': 100,
            'act_smooth': 0.14,
            'hist_smooth': 7,
            'alpha': 0.79,
        }
        tempo_conf_final = tempo_conf_defaults | tempo_conf

        if action == 'extract_music_info':
            if 'wav_file' not in request.json:
                return {"error_message": "'wav_file' not found or invalid"}, 400

            wav_file_path = os.sep.join([DATA_DIR, request.json['wav_file']])
            result = request.json

            
            downbeat_act = RNNDownBeatProcessor()(wav_file_path)
            downbeat_proc = DBNDownBeatTrackingProcessor(
                **downbeat_conf_final
            )

            beat_act = RNNBeatProcessor()(wav_file_path)
            tempo_proc = TempoEstimationProcessor(
                **tempo_conf_final
            )

            key_proc = CNNKeyRecognitionProcessor()

            result = {
                "downbeat_conf": downbeat_conf_final,
                "downbeat": downbeat_proc(downbeat_act).tolist(),
                "tempo_conf": tempo_conf_final,
                "tempo": tempo_proc(beat_act).tolist(), 
                "key": key_proc(wav_file_path).tolist(),
            }
            return result
        else:
            return {"error_message": "'action' is not defined or invalid"}
