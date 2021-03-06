"""
Min queue to be used in A* algo
"""
from abc import ABCMeta,abstractmethod
import os

class BaseQueue(object):
    """
    abstract class for defining custom queue
    """
    __metaclass__ = ABCMeta

    _list = None

    def __init__(self,*args,**kwargs):
        self._list = []

    @abstractmethod
    def dequeue(self):
        "return and remove a queue item, raise exception if queue is empty"
        pass

    @abstractmethod
    def peek(self):
        "return a queue item, raise exception if queue is empty"
        pass

    def enqueue(self,item):
        if (not (item in self._list)):
            self._list.append(item)

    def is_empty(self):
        return len(self._list)==0

class SimpleQueue(BaseQueue):
    def peek(self):
        if (self.is_empty()):
            raise Exception("queue is empty, cannot call peek")
        return self._list[0]

    def dequeue(self):
        if (self.is_empty()):
            raise Exception("queue is empty, cannot call dequeue")
        item = self._list[0]
        del self._list[0]
        return item

class MinQueue(BaseQueue):
    """
    No duplicated allowed in the queue
    """
    _key_func = None # function used to sort the list

    def __init__(self,*args,**kwargs):
        super(MinQueue,self).__init__(*args,**kwargs)
        if (not kwargs.get("key")):
            raise Exception("`key` must be passed in to create MinQueue")
        self._key_func = kwargs.get("key")

    def dequeue(self):
        return self.dequeue_min()

    def dequeue_min(self):
        self._list.sort(key=self._key_func)
        min = self._list[0]
        del self._list[0]
        return min

    def peek(self):
        self._list.sort(key=self._key_func)
        return self._list[0]

def get_or_exception(kwargs,key,err_msg=""):
    "return kwargs[key], raise exception if it gives none"
    value = kwargs.get(key)
    if (not value):
        err = err_msg if err_msg else "Parameter {} cannot be None".format(key)
        raise Exception(err)
    return value

def create_or_append_file(file_name,content,overwrite=True):
    "create file and write content if first time calling, append content to file if not"
    # update static var: file_list
    if (not hasattr(create_or_append_file,"file_list")):
        create_or_append_file.file_list = [file_name]
    else:
        if (not file_name in create_or_append_file.file_list):
            create_or_append_file.file_list.append(file_name)
    # write or append file
    if (file_name in create_or_append_file.file_list):
        with open(file_name,"a") as f:
            f.write(content+"\n")
    else:
        with open(file_name,"w") as f:
            f.write(content+"\n")


# unused
def synchronized(lock):
    """ Synchronization decorator. """

    def wrap(f):
        def newFunction(*args, **kw):
            lock.acquire()
            print("lock acquired for {}".format(f))
            try:
                return f(*args, **kw)
            finally:
                lock.release()
                print("lock released for {}".format(f))
        return newFunction
    return wrap