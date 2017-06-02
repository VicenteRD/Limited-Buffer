import logging
import random
import time
import sys

from threading import Thread, Semaphore

BUFFER_SIZE = 1000
PRODUCER_COUNT = 3 * BUFFER_SIZE
CONSUMER_COUNT = 1.5 * BUFFER_SIZE

logger = logging.getLogger()


class LimitedBuffer:

    def __init__(self, size):
        self._size = size
        self._used = 0

        self._empty_semaphore = Semaphore(self._size)
        self._full_semaphore = Semaphore(0)

    def add_item(self):
        self._empty_semaphore.acquire()

        self._used += 1

        self._full_semaphore.release()

    def remove_item(self):
        self._full_semaphore.acquire()

        self._used -= 1

        self._empty_semaphore.release()

    def current_size(self):
        if self._used < 0 or self._used > self._size:
            exit(-1)
        return str(self._used).zfill(4)


class ProducerThread(Thread):

    def __init__(self, limited_buffer, number, production_time):
        self._production_time = production_time

        self._buffer = limited_buffer

        super(ProducerThread, self).__init__()
        self.name = 'P' + str(number).zfill(4)

    def produce(self):
        self._buffer.add_item()

    def run(self):
        while True:
            time.sleep(self._production_time)
            self.produce()

            logger.log(logging.INFO, '  (> :-: )>  | ' +
                       self._buffer.current_size() + ' |           ')


class ConsumerThread(Thread):
    def __init__(self, limited_buffer, number, consumption_time):
        self._consumption_time = consumption_time

        self._buffer = limited_buffer

        super(ConsumerThread, self).__init__()
        self.name = 'C' + str(number).zfill(4)

    def consume(self):
        self._buffer.remove_item()

    def run(self):
        while True:
            time.sleep(self._consumption_time)
            self.consume()

            logger.log(logging.INFO, '             | ' +
                       self._buffer.current_size() + ' |  <( :-: <)')


def init_logging():
    logger_format = logging.Formatter(
        fmt='[%(threadName)s] %(message)s'
    )
    logger_handler = logging.StreamHandler(sys.stdout)
    logger_handler.setFormatter(logger_format)
    logger.addHandler(logger_handler)
    logger.setLevel(logging.INFO)

if __name__ == '__main__':

    buffer = LimitedBuffer(BUFFER_SIZE)

    init_logging()

    producers = []
    consumers = []

    for i in range(int(PRODUCER_COUNT)):
        producer = ProducerThread(buffer, len(producers), random.randint(2, 10))

        producers.append(producer)
        producer.start()

    for i in range(int(CONSUMER_COUNT)):
        consumer = ConsumerThread(buffer, len(consumers), random.randint(2, 10))

        consumers.append(consumer)
        consumer.start()
