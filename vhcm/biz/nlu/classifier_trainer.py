import subprocess
import multiprocessing
import threading
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from vhcm.common.constants import *
from vhcm.common.utils.process import kill_child_proc


def send_stdout_to_client(stdout):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        TRAIN_CLASSIFIER_ROOM_GROUP,
        {
            'type': 'send.message',
            'message': stdout
        }
    )


class ClassifierTrainer(object):
    def __init__(self, script_path):
        self.script = script_path
        self.communicate_queue = None
        self.process = None
        self.listening_thread = None

    def start(self, train_type, data, sentence_length, batch, epoch, learning_rate, epsilon, activation, bot_version):
        self.communicate_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(
            target=self.train,
            args=(self.script, self.communicate_queue, train_type, data, sentence_length,
                  batch, epoch, learning_rate, epsilon, activation, bot_version,),
            daemon=True)
        self.process.start()
        self.listening_thread = threading.Thread(target=self.wait_for_stdout, args=[self.communicate_queue], daemon=True)
        self.listening_thread.start()

    def stop(self):
        try:
            if self.listening_thread.is_alive():
                self.communicate_queue.put('terminate')
            # Kill the child training process
            kill_child_proc(self.process.pid)
            self.process.terminate()
            status = True
        except Exception as e:
            print('[classifier trainer] Error: {}'.format(e))
            status = False
        finally:
            self.communicate_queue = None
            self.process = None
            self.listening_thread = None

        return status

    def is_running(self):
        return True if self.process else False

    @staticmethod
    def wait_for_stdout(communicate_queue):
        while True:
            out = communicate_queue.get()
            send_stdout_to_client(out)
            if out == 'Training process done' or out == 'Training process error' or out == 'terminate':
                break

    @staticmethod
    def train(script_path, communicate_queue, train_type, data, sentence_length,
              batch, epoch, learning_rate, epsilon, activation, bot_version):
        args = [
            'python', script_path,
            '-t', str(train_type),
            '-d', data,
            '-v', str(bot_version)
        ]
        if train_type != 3:
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
                stdout = str(output, encoding=UTF8, errors='ignore').strip()
                communicate_queue.put(stdout)
        rc = process.poll()
        return_message = 'Training process done' if rc == 0 else 'Training process error'
        communicate_queue.put(return_message)
