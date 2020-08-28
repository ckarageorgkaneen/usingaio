import threading
import sys

from queue import Queue
from attr import attrs, attrib


# Example 2-2. ThreadBot programming for table service
class ThreadBot(threading.Thread):
    # A ThreadBot is a subclass of a thread
    def __init__(self):
        # The target function of the thread is the manage_table() method,
        # defined later in the file.
        super().__init__(target=self.manage_table)
        # This bot is going to be waiting tables and will need to be
        # responsible for some cutlery. Each bot keeps track of the cutlery
        # that it took from the kitchen here. (The Cutlery class will be
        # defined later.)
        self.cutlery = Cutlery(knives=0, forks=0)
        # The bot will also be assigned tasks. They will be added to this task
        # queue, and the bot will perform them during its main processing loop,
        # next.
        self.tasks = Queue()

    def manage_table(self):
        # The primary routine of this bot is this infinite loop. If you need to
        # shut down a bot, you have to give them the shutdown task.
        while True:
            task = self.tasks.get()
            if task == 'prepare table':
                # There are only three tasks defined for this bot. This one,
                # prepare table, is what the bot must do to get a new table
                # ready for service. For our test, the only requirement is to
                # get sets of cutlery from the kitchen and place them on the
                # table. clear table is used when a table is to be cleared:
                # the bot must return the used cutlery back to the kitchen.
                # shutdown just shuts down the bot.
                kitchen.give(to=self.cutlery, knives=4, forks=4)
            elif task == 'clear table':
                self.cutlery.give(to=kitchen, knives=4, forks=4)
            elif task == 'shutdown':
                return


# Example 2-3. Definition of the Cutlery object

# attrs , which is an open source Python library that has nothing to do with
# threads or asyncio , is a really wonderful library for making class creation
# easy. Here, the @attrs decorator will ensure that this Cutlery class will get
# all the usual boilerplate code (like __init__() ) automatically set up.
@attrs
class Cutlery:
    # The attrib() function provides an easy way to create attributes,
    # including defaults, which you might normally have handled as keyword
    # arguments in the __init__() method.
    knives = attrib(default=0)
    forks = attrib(default=0)
    # lock = attrib(threading.Lock())

    # This method is used to transfer knives and forks from one Cutlery object
    # to another. Typically, it will be used by bots to obtain cutlery from the
    # kitchen for new tables, and to return the cutlery back to the kitchen
    # after a table is cleared.
    def give(self, to: 'Cutlery', knives=0, forks=0):
        self.change(-knives, -forks)
        to.change(knives, forks)

    # This is a very simple utility function for altering the inventory data
    # in the object instance.
    def change(self, knives, forks):
        # with self.lock:
        self.knives += knives
        self.forks += forks


# We’ve defined kitchen as the identifier for the kitchen inventory of
# cutlery. Typically, each of the bots will obtain cutlery from this
# location. It is also required that they return cutlery to this store when a
# table is cleared.
kitchen = Cutlery(knives=100, forks=100)
# This script is executed when testing. For our test, we’ll be using 10
# ThreadBots.
bots = [ThreadBot() for i in range(10)]

for bot in bots:
    # We get the number of tables as a command-line parameter, and then give
    # each bot that number of tasks for preparing and clearing tables in the
    # restaurant.
    for i in range(int(sys.argv[1])):
        bot.tasks.put('prepare table')
        bot.tasks.put('clear table')
    # The shutdown task will make the bots stop (so that bot.join() a bit
    # further down will return). The rest of the script prints diagnostic
    # messages and starts up the bots.
    bot.tasks.put('shutdown')
print('Kitchen inventory before service:', kitchen)
for bot in bots:
    bot.start()
for bot in bots:
    bot.join()
print('Kitchen inventory after service:', kitchen)
