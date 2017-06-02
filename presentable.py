import random
import time
import sys

from threading import Thread, Semaphore

BUFFER_SIZE = 1000
PRODUCER_COUNT = 1.5 * BUFFER_SIZE
CONSUMER_COUNT = 1.5 * BUFFER_SIZE

PROD_MIN = 15
CONS_MIN = 15
PROD_MAX = PROD_MIN + 5
CONS_MAX = CONS_MIN + 5


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

if __name__ == '__main__':

    buffer = LimitedBuffer(BUFFER_SIZE)

    producers = []
    consumers = []

    for i in range(int(PRODUCER_COUNT)):
        producer = ProducerThread(buffer, len(producers),
                                  random.randint(PROD_MIN, PROD_MAX))
        producers.append(producer)
        producer.start()

    for i in range(int(CONSUMER_COUNT)):
        consumer = ConsumerThread(buffer, len(consumers),
                                  random.randint(CONS_MIN, CONS_MAX))
        consumers.append(consumer)
        consumer.start()
