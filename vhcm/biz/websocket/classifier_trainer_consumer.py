import json
import os
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from vhcm.biz.nlu.classifier_trainer import ClassifierTrainer
import vhcm.common.config.config_manager as config
from vhcm.common.constants import TRAIN_CLASSIFIER_ROOM_GROUP, PROJECT_ROOT, TRAIN_DATA_FOLDER
from vhcm.common.utils.files import PICKLE_EXTENSION
from vhcm.models import train_data as train_data_model


class ClassifierConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trainer = None
        self.room_name = None
        self.room_group_name = None

    def connect(self):
        self.room_name = TRAIN_CLASSIFIER_ROOM_GROUP
        self.room_group_name = self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        script_path = config.config_loader.get_setting_value(config.CLASSIFIER_TRAINER_SCRIPT)
        script_path = os.path.join(PROJECT_ROOT, script_path)
        print(script_path)
        self.trainer = ClassifierTrainer(script_path)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("DISCONNECTED CODE: ", close_code)
        if self.is_process_running() and close_code != 1000:
            self.trainer.stop()

    def close(self, code=None):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        self.trainer.stop()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']

        if command == 'start':
            data_id = text_data_json['data']
            train_data = train_data_model.TrainData.objects.filter(id=data_id).first()
            if not train_data:
                self.send(text_data=json.dumps({
                    'type': 'start_failed',
                    'data': None
                }))
                return
            train_data_filepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + train_data.filename + PICKLE_EXTENSION)
            train_type = text_data_json['type']
            sentence_length = text_data_json['sentence_length']
            batch = text_data_json['batch']
            epoch = text_data_json['epoch']
            learning_rate = text_data_json['learning_rate']
            epsilon = text_data_json['epsilon']
            activation = text_data_json['activation']

            self.trainer.start(train_type, train_data_filepath, sentence_length, batch, epoch, learning_rate, epsilon, activation)
        elif command == 'stop':
            status = self.trainer.stop()
            # Send status to WebSocket
            self.send(text_data=json.dumps({
                'type': 'stop_status',
                'data': status
            }))

        elif command == 'check_status':
            status = self.is_process_running()
            self.send(text_data=json.dumps({
                'type': 'running_status',
                'data': status
            }))

    # Receive message from room group
    def send_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'message',
            'data': message
        }))

    # Check if train process running
    def is_process_running(self):
        return self.trainer.is_running()
