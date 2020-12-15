import json
import os
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from vhcm.biz.nlu.classifier_trainer import ClassifierTrainer
import vhcm.common.config.config_manager as config
from vhcm.common.constants import TRAIN_CLASSIFIER_ROOM_GROUP, PROJECT_ROOT, TRAIN_DATA_FOLDER, NEW_LINE, BOT_VERSION_FILE_PATH
from vhcm.models import train_data as train_data_model
from vhcm.biz.nlu.vhcm_chatbot import is_bot_ready, system_bot_version, TURN_OFF_NEXT_STARTUP
from vhcm.common.utils.files import ZIP_EXTENSION

# Response types
SEND_MESSAGE = 'message'
TRAIN_START_FAILED = 'start_failed'
PROCESS_RUNNING_STATUS = 'running_status'
TRAIN_PROCESS_STOP_STATUS = 'stop_status'
SEND_TURN_OFF_STATUS = 'turn_off_status'


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
            if is_bot_ready():
                self.send_response(
                    TRAIN_START_FAILED,
                    NEW_LINE.join(['Chatbot is running, for training first send a turnoff chatbot signal then restart server.',
                                   'Or use the separate training script provided.',
                                   'TRAINING PROCESS NOT STARTED.'])
                )
            else:
                data_id = text_data_json['data']
                train_data = train_data_model.TrainData.objects.filter(id=data_id).first()
                if not train_data:
                    self.send_response(TRAIN_START_FAILED, 'Train data not existed')
                    return
                # train_data_zip = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + train_data.filename + ZIP_EXTENSION)
                # unzip(train_data_zip, output=os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER))
                train_data_filepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + train_data.filename + ZIP_EXTENSION)
                if not os.path.exists(train_data_filepath):
                    self.send_response(TRAIN_START_FAILED, 'Train data not existed')
                    return
                train_type = text_data_json['type']
                sentence_length = text_data_json['sentence_length']
                batch = text_data_json['batch']
                epoch = text_data_json['epoch']
                learning_rate = text_data_json['learning_rate']
                epsilon = text_data_json['epsilon']
                activation = text_data_json['activation']
                version = train_data.id

                self.trainer.start(train_type, train_data_filepath, sentence_length, batch, epoch, learning_rate, epsilon, activation, version)
        elif command == 'stop':
            status = self.trainer.stop()
            # Send status to WebSocket
            self.send_response(TRAIN_PROCESS_STOP_STATUS, status)

        elif command == 'check_status':
            status = self.is_process_running()
            self.send_response(PROCESS_RUNNING_STATUS, status)

        elif command == 'turn_off_bot':
            if system_bot_version[TURN_OFF_NEXT_STARTUP]:
                self.send_response(TURN_OFF_NEXT_STARTUP, 'Already sent an signal to turn off chatbot next startup')
            else:
                system_bot_version[TURN_OFF_NEXT_STARTUP] = False
                version_file_path = os.path.join(PROJECT_ROOT, BOT_VERSION_FILE_PATH)
                with open(version_file_path, 'w') as f:
                    json.dump(system_bot_version, f, indent=4)
                self.send_response(TURN_OFF_NEXT_STARTUP, 'Sent an signal to turn off chatbot on next start up sucessfully')

    # Receive message from trainer service
    def send_message(self, event):
        message = event['message']
        if message == 'Training process done' or message == 'Training process error':
            self.trainer.stop()
        # Send message to WebSocket
        self.send_response(SEND_MESSAGE, message)

    def send_response(self, datatype, data=None):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': datatype,
            'data': data
        }))

    # Check if train process running
    def is_process_running(self):
        return self.trainer.is_running()
