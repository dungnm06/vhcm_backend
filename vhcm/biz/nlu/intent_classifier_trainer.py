import subprocess
import multiprocessing
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from vhcm.common.constants import *
from vhcm.common.utils.process import kill_child_proc
import vhcm.common.config.config_manager as config


def send_stdout_to_client(stdout):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        WEBSOCKET_ROOM + INTENT_CLASSIFIER_ROOM_GROUP,
        {
            'type': 'send_message',
            'message': stdout
        }
    )


class IntentClassifierTrainer(object):
    def __init__(self):
        self.communicate_queue = None
        self.process = None
        self.listening_process = None

    def start(self, data, sentence_length, batch, epoch, learning_rate, epsilon, activation):
        self.communicate_queue = multiprocessing.JoinableQueue()
        self.process = multiprocessing.Process(
            target=self.train,
            args=(self.communicate_queue, data, sentence_length, batch, epoch, learning_rate, epsilon, activation,),
            daemon=True)
        self.process.start()
        self.listening_process = multiprocessing.Process(
            target=self.wait_for_stdout,
            args=(self.communicate_queue,),
            daemon=True)
        self.listening_process.start()

    def stop(self):
        self.listening_process.terminate()
        # Kill the child training process
        kill_child_proc(self.process.pid)
        self.process.terminate()

    @staticmethod
    def wait_for_stdout(communicate_queue):
        while True:
            out = communicate_queue.get()
            send_stdout_to_client(out)

    @staticmethod
    def train(communicate_queue, data, sentence_length, batch, epoch, learning_rate, epsilon, activation):
        # console_log = open('C:/Users/Tewi/Desktop/log.txt', 'w', buffering=1)
        args = [
            'python', os.path.join(PROJECT_ROOT, config.CONFIG_LOADER.get_setting_value(config.CLASSIFIER_TRAINER_SCRIPT)),
            '-t', '1',
            '-d', data
        ]
        if sentence_length:
            args.extend(['-sl', str(sentence_length)])
        if batch:
            args.extend(['-b', str(batch)])
        if epoch:
            args.extend(['-e', str(epoch)])
        if learning_rate:
            args.extend(['-lr', str(learning_rate)])
        if epsilon:
            args.extend(['-eps', str(epsilon)])
        if activation:
            args.extend(['-sl', activation])

        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                stdout = output.decode(UTF8).strip()
                communicate_queue.put(stdout)
                # console_log.write(stdout)
                # console_log.flush()
        rc = process.poll()
        # console_log.close()
