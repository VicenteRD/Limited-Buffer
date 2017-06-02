import logging
import random
import time
import sys

from threading import Thread, Semaphore

BUFFER_SIZE = 1000
PRODUCER_COUNT = 1.5 * BUFFER_SIZE
CONSUMER_COUNT = 1.5 * BUFFER_SIZE

PROD_MIN = 2
CONS_MIN = 2
PROD_MAX = PROD_MIN + 8
CONS_MAX = CONS_MIN + 8

LOG_LEVEL = logging.DEBUG

logger = logging.getLogger()


class LimitedBuffer:

    def __init__(self, size):
        self._size = size
        self._used = 0

        # Sempahore to check if producers can act
        self._empty_semaphore = Semaphore(self._size)
        # Semaphore to check if consumers can act
        self._full_semaphore = Semaphore(0)
        logger.log(logging.DEBUG, 'empty_semaphore starting value: ' +
                   str(self._empty_semaphore._value))
        logger.log(logging.DEBUG, 'full_semaphore starting value: ' +
                   str(self._full_semaphore._value))

    def add_item(self):
        logger.log(logging.DEBUG, 'Reached empty_semaphore check (acquire).')
        self._empty_semaphore.acquire()
        logger.log(logging.DEBUG, 'empty_semaphore: ' +
                   str(self._empty_semaphore._value))

        self._used += 1

        logger.log(logging.DEBUG, 'Signaling full_semaphore (release).')
        self._full_semaphore.release()
        logger.log(logging.DEBUG, 'full_semaphore: ' +
                   str(self._full_semaphore._value))

    def remove_item(self):
        logger.log(logging.DEBUG, 'Reached full_semaphore check (acquire).')
        self._full_semaphore.acquire()
        logger.log(logging.DEBUG, 'full_semaphore: ' +
                   str(self._full_semaphore._value))

        self._used -= 1

        logger.log(logging.DEBUG, 'Signaling empty_semaphore (release).')
        self._empty_semaphore.release()
        logger.log(logging.DEBUG, 'empty_semaphore: ' +
                   str(self._empty_semaphore._value))

    def current_size(self):
        # Probably shouldn't have a sanity check here, but it works!
        if self._used < 0 or self._used > self._size:
            exit(-1)
        return str(self._used).zfill(4)


class ProducerThread(Thread):

    def __init__(self, limited_buffer, number, production_time):
        self._production_time = production_time

        self._buffer = limited_buffer

        super(ProducerThread, self).__init__()
        self.name = 'P' + str(number).zfill(4)
        logger.log(logging.DEBUG, 'Initialized ' + self.name + ' with time: ' +
                   str(self._production_time))

    def produce(self):
        logger.log(logging.DEBUG, 'Producing item.')
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
        logger.log(logging.DEBUG, 'Initialized ' + self.name + ' with time: ' +
                   str(self._consumption_time))

    def consume(self):
        logger.log(logging.DEBUG, 'Consuming item.')
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
    logger.setLevel(LOG_LEVEL)

if __name__ == '__main__':

    init_logging()

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
