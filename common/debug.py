import os
from datetime import datetime
from utils import create_or_append_file

"""
for printing and saving debug messages
"""
# program layered as follows:
# interface -> validation ->io_q -> fsm -> algo
DEBUG_VALIDATION = "v"
DEBUG_IO_QUEUE = "q"
DEBUG_INTERFACE = "i"
DEBUG_STATES = "s"
DEBUG_MIDDLEWARE = "m"
DEBUG_OTHERS = "o"
DEBUG_ALGO = "a"
DEBUG_TIMER = "t"
DEBUG_COMMON = "c" # refering to amap and robot

# change this to enable/disable types of debug messages
DEBUG_SETTING = {
    "enabled_types":[
    DEBUG_VALIDATION,
    #DEBUG_IO_QUEUE,
    DEBUG_INTERFACE,
    DEBUG_COMMON,
    DEBUG_STATES,
    DEBUG_MIDDLEWARE,
    #DEBUG_OTHERS,
    #DEBUG_TIMER,
    #DEBUG_ALGO
    ],
    "save_file":False,
}


def debug(message,type):
    "if save_file is turned on, file will be saved to hour-minute-second(debug).txt"
    if (not hasattr(debug,"started")):
        now = datetime.now()
        debug.file_name = "{}-{}-{}(debug).txt".format(now.hour,now.minute,now.second)
        debug.started = True
    if (type not in DEBUG_SETTING['enabled_types']):
        return
    msg = "[{}]: {}".format(type,message)
    print(msg)
    if (DEBUG_SETTING.get("save_file")):
        file_name = debug.file_name
        create_or_append_file(file_name,msg)