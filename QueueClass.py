
class Queue:
    """
    Queue class for stage implementation. Should have as separate .py file.
    """
    def __init__(self):
        self.__items = []  # init the  list / queue as empty

    # Adds a new item to the back of the queue, and returns nothing:
    def enqueue(self, item, idx=None):
        """
        Enqueue the element to the back of the queue

        :param item: the element to be enqueued
        :return: No returns
        """
        if item.strip() == '':
            return
        if idx is None:
            self.__items.append(item)
        else:
            self.__items.insert(idx, item)

    # Removes and returns the front-most item in the queue.
    # Returns nothing if the queue is empty.
    def dequeue(self):
        """
        Dequeue the element from the front of the queue and return it

        :return: The object that was dequeued
        """
        if len(self.__items) <= 0:
            raise Exception('Error: Queue is empty')
        return self.__items.pop(0)

    def peek(self):
        """
        Returns the front-most item in the queue, and DOES NOT change the queue.

        :return: front-most item in the queue
        """
        if len(self.__items) <= 0:
            raise Exception('Error: Queue is empty')
        return self.__items[0]

    def is_empty(self):
        """
        Checks if queue is empty or not

        :return: True if the queue is empty, and False otherwise
        """
        return len(self.__items) == 0

    def size(self):
        """
        Returns number of items in queue

        :return: The number of items in the queue
        """
        return len(self.__items)

    #
    def clear(self):
        """
        Removes all items from the queue

        :return: None
        """
        self.__items = []

    # Returns a string representation of the queue:
    def __str__(self):
        """
        Returns string rep of queue

        :return: String representation of the queue
        """
        str_exp = ""
        for item in self.__items:
            str_exp += ('> ' + str(item))
        return str_exp