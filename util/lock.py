# -*- coding: utf-8 -*-
import time
import random
import threading
import multiprocessing


class Lock(object):
    is_lock = False
    def __new__(cls, key=None, expires=3, timeout=1):
        """
        实现单例模式
        :param cls:
        :param key:
        :param expires:
        :param timeout:
        :return:
        """
        if key is None:
            if not hasattr(cls, '_instance'):
                cls._instance = super(Lock, cls).__new__(cls, key, expires, timeout)

            return cls._instance
        else:
            if not hasattr(cls, '_instances'):
                cls._instances = {}
            if key not in cls._instances:
                cls._instances[key] = super(Lock, cls).__new__(cls, key, expires, timeout)

            return cls._instances[key]

    def __init__(self, key=None, expires=3, timeout=1):
        """
        Distributed locking if required, using Redis SETNX and GETSET.

        Usage::

            with Lock('my_lock'):
                print "Critical section"

        :param  expires     We consider any existing lock older than
                            ``expires`` seconds to be invalid in order to
                            detect crashed clients. This value must be higher
                            than it takes the critical section to execute.
        :param  timeout     If another client has already obtained the lock,
                            sleep for a maximum of ``timeout`` seconds before
                            giving up. A value of 0 means we never wait.
        """

        self.key = key
        self.timeout = timeout
        self.expires = expires
        super(Lock, self).__init__()

    def _lock(self):
        self.start_time = time.time()
        self.is_lock = True
        print"%s %s" % (self.start_time, 'locked')

    def _unlock(self):
        self.is_lock = False
        self.start_time = None
        print "%s %s" % (time.time(), 'unlocked')

    # TODO: 如果需要支持分布式，需要考虑利用redis或者分布式文件锁
    def __enter__(self):
        print "%s %s" % (threading.current_thread().name, ' enter')
        if self.is_lock:
            print "%s %s" % (threading.current_thread().name, ' islocked')
            start_time = self.start_time or time.time()
            incre = self.timeout / 3.0   # try 3 times
            while time.time() < start_time + self.timeout:  # not yet timeout
                print "%s %s: %s - %s" % (threading.current_thread().name, ' wait for lock', time.time(), start_time + self.timeout)
                if time.time() > start_time + self.expires:  # check if previous locker is dead
                    print "%s %s: %s" % (time.time(), 'expired', start_time + self.expires - time.time())
                    self._unlock()
                time.sleep(incre)
                if not self.is_lock:
                    self._lock()
                    return
            print "%s %s %s" % (threading.current_thread().name, time.time(), 'timeout')
            raise LockAcquireTimeout('无法获取锁：获取超时！')
        else:
            self._lock()

    def __exit__(self, exc_type, exc_value, traceback):
        print "%s %s: %s" % (threading.current_thread().name, ' exit', time.time() - self.start_time)
        self._unlock()


class LockAcquireTimeout(BaseException):
    pass


class LockTimeout(BaseException):
    pass


from multiprocessing import Value, Array, Process
from renderutil import day_str
import random
def incr_order_no(pre_no=None):
    if pre_no is None:
        return Array('i', [int(day_str()), 0])
    time.sleep(0.1*random.random())
    pre_no[0] = int(day_str())
    pre_no[1] += 1
    new_no = '%s%s' % (pre_no[0], pre_no[1])
    print multiprocessing.current_process(), pre_no[:], new_no
    return pre_no


if __name__ == "__main__":
    init_no = incr_order_no()
    processes = [Process(target=incr_order_no, args=(init_no,)) for i in xrange(8)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    # import threading
    # import random
    # counter = 0
    # def incr():
    #     global counter
    #     r = random.randint(6, 10)
    #     print "%s %s %s %s %s" % (threading.current_thread().name, "wait:", r, " active:", threading.active_count())
    #     with Lock(timeout=6):
    #         time.sleep(r)
    #         counter += 1
    #         print "%s %s %s %s %s" % (threading.current_thread().name, "counter:", counter, " active:", threading.active_count())
    #
    # threads = [threading.Thread(target=incr, name="thread-%s" % x) for x in xrange(2)]
    # for t in threads:
    #     t.start()
    # time.sleep(2)
    # t = threading.Thread(target=incr, name="thread-check-expired------")
    # t.start()
    # t.join()

    print '------------over'