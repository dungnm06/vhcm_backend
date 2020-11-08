import subprocess
import multiprocessing
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from vhcm.common.constants import *
from vhcm.common.utils.process import kill_child_proc


def send_stdout_to_client(stdout):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        WEBSOCKET_ROOM + TRAIN_CLASSIFIER_ROOM_GROUP,
        {
            'type': 'send_message',
            'message': stdout
        }
    )


class ClassifierTrainer(object):
    def __init__(self, script_path):
        self.script = script_path
        self.communicate_queue = None
        self.process = None
        self.listening_process = None

    def start(self, train_type, data, sentence_length, batch, epoch, learning_rate, epsilon, activation):
        self.communicate_queue = multiprocessing.JoinableQueue()
        self.process = multiprocessing.Process(
            target=self.train,
            args=(self.script, self.communicate_queue, train_type, data, sentence_length, batch, epoch, learning_rate, epsilon, activation,),
            daemon=True)
        self.process.start()
        self.listening_process = multiprocessing.Process(
            target=self.wait_for_stdout,
            args=(self.communicate_queue,),
            daemon=True)
        self.listening_process.start()

    def stop(self):
        status = False
        try:
            self.listening_process.terminate()
            # Kill the child training process
            kill_child_proc(self.process.pid)
            self.process.terminate()
            status = True
        except Exception:
            # TODO: Implement force close processes
            status = False
        finally:
            self.communicate_queue = None
            self.process = None
            self.listening_process = None

        return status

    def is_running(self):
        return True if self.process else False

    @staticmethod
    def wait_for_stdout(communicate_queue):
        while True:
            out = communicate_queue.get()
            send_stdout_to_client(out)

    @staticmethod
    def train(script_path, communicate_queue, train_type, data, sentence_length, batch, epoch, learning_rate, epsilon, activation):
        # console_log = open('C:/Users/Tewi/Desktop/log.txt', 'w', buffering=1)
        args = [
            'python', os.path.join(PROJECT_ROOT, script_path),
            '-t', str(train_type),
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
            args.extend(['-a', activation])
        print(args)

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
