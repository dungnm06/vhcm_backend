import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from vhcm.biz.nlu.classifier_trainer import ClassifierTrainer
import vhcm.common.config.config_manager as config
from vhcm.common.constants import WEBSOCKET_ROOM, TRAIN_CLASSIFIER_ROOM_GROUP


class ClassifierConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.trainer = None
        self.room_name = WEBSOCKET_ROOM
        self.room_group_name = self.room_name + TRAIN_CLASSIFIER_ROOM_GROUP

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        script_path = config.CONFIG_LOADER.get_setting_value(config.CLASSIFIER_TRAINER_SCRIPT)
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
        self.trainer.stop()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']

        if command == 'start':
            data = 'C:/Users/Tewi/Desktop/train_data.pickle'
            train_type = text_data_json['type']
            sentence_length = text_data_json['sentence_length']
            batch = text_data_json['batch']
            epoch = text_data_json['epoch']
            learning_rate = text_data_json['learning_rate']
            epsilon = text_data_json['epsilon']
            activation = text_data_json['activation']

            self.trainer.start(train_type, data, sentence_length, batch, epoch, learning_rate, epsilon, activation)
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


# train_service_consumer = ClassifierConsumer()
