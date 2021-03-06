from common.debug import debug,DEBUG_STATES

class StateMachine(object):
    """
    Interface specification for State Machine
    """
    _state = None # BaseState object
    _map_ref = None
    _robot_ref = None

    def set_next_state(self,st):
        self._state = st
        debug("state changed to {}".format(st),DEBUG_STATES)

    def get_map_ref(self):
        return self._map_ref

    def get_robot_ref(self):
        return self._robot_ref

    def reset(self):
        raise NotImplementedError()

    def send_command(self,msg):
        raise NotImplementedError()