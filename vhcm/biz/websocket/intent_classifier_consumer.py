import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from vhcm.biz.nlu.intent_classifier_trainer import IntentClassifierTrainer

trainer = IntentClassifierTrainer()


class IntentClassifierConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = 'trainer'
        self.room_group_name = self.room_name + "_intentClassifier"

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("DISCONNECTED CODE: ", close_code)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']

        if command == 'start':
            data = 'C:/Users/Tewi/Desktop/train_data.pickle'
            sentence_length = text_data_json['sentence_length']
            batch = text_data_json['batch']
            epoch = text_data_json['epoch']
            learning_rate = text_data_json['learning_rate']
            epsilon = text_data_json['epsilon']
            activation = text_data_json['activation']

            trainer.start(data, sentence_length, batch, epoch, learning_rate, epsilon, activation)
        elif command == 'stop':
            trainer.stop()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_message',
                'message': command
            }
        )

    # Receive message from room group
    def send_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
