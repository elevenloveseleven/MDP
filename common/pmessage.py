import json

class ValidationException(Exception):
    pass

class PMessage():
    _type = None
    _msg = None

    # for type
    T_COMMAND = "cmd"
    T_STATE_CHANGE = "stc"
    T_ROBOT_MOVE = "rm"
    T_MAP_UPDATE = "mu"
    T_SET_ROBOT_POS = "setrobotpos" # msg should be like 1,2
    T_CALLIBRATE = "callibrate"
    #TODO: for simulation only
    T_LOAD_MAP = "loadmap" # msg should be map path

    # for msg
    M_MOVE_INSTRUCTIONS = M_MOVE_FORWARD,M_TURN_LEFT,M_TURN_RIGHT,M_TURN_BACK = ["mf",
                                                                                 "tl",
                                                                                 "tr",
                                                                                 "tb"]
    M_OTHER_INSTRUCTIONS = M_START_EXPLORE,M_END_EXPLORE,M_START_FASTRUN,M_RESET,M_CALIBRATE,M_GET_SENSOR = ["explore",
                                                                                                "endexplore",
                                                                                                "run",
                                                                                                "reset",
                                                                                                "calibrate",
                                                                                                "sense"]
    M_VALID_COMMAND_MSGS = M_MOVE_INSTRUCTIONS + M_OTHER_INSTRUCTIONS

    M_CALLIBRATE_FRONT = "cfront"
    M_CALLIBRATE_LEFT = "cleft"
    M_CALLIBRATE_RIGHT = "cright"

    def render_msg(self):
        "return message formatted in JSON"
        return json.dumps({"type":self._type,"msg":self._msg})

    def __unicode__(self):
        return self.render_msg()

    def __str__(self):
        return self.render_msg()

    def __init__(self,**kwargs):
        """
        can either initialize via json by passing in `json_str`,
        or pass in `type` and `msg`
        """
        json_str = kwargs.get("json_str")
        if (json_str):
            obj = json.loads(json_str)
            PMessage.validate(obj['type'],obj['msg'])
            self._type = obj['type']
            self._msg = obj['msg']
        else:
            PMessage.validate(kwargs.get("type"),kwargs.get("msg"))
            self._type = kwargs.get("type")
            self._msg = kwargs.get("msg")

    @staticmethod
    def load_messages_from_json(json_str):
        "json_str may be a concatenation of json, return a list of PMessage"
        import re
        json_pattern = re.compile(r'{[^{}]+}')
        json_strs = json_pattern.findall(json_str)
        return [PMessage(json_str=js) for js in json_strs]

    def equals(self,a_msg):
        return self._type==a_msg._type and self._msg==a_msg._msg

    def get_type(self):
        return self._type

    def get_msg(self):
        return self._msg

    def is_map_update(self):
        return self.get_type()==self.T_MAP_UPDATE

    @staticmethod
    def validate(type,msg):
        if (type==PMessage.T_COMMAND):
            if (msg not in PMessage.M_VALID_COMMAND_MSGS):
                raise ValidationException("{} is not a valid command".format(msg))
        elif(type==PMessage.T_ROBOT_MOVE):
            if (msg not in PMessage.M_MOVE_INSTRUCTIONS):
                raise ValidationException("{} is not a valid robot move".format(msg))
        elif(type==PMessage.T_STATE_CHANGE):
            return
        elif(type==PMessage.T_MAP_UPDATE):
            try:
                values = map(int,msg.strip().split(","))
                a = values[4]
            except:
                raise ValidationException("{} is not a valid map update".format(msg))
        elif(type==PMessage.T_SET_ROBOT_POS):
            try:
                values = map(int,msg.strip().split(","))
            except:
                raise ValidationException("{} is not a valid robot position".format(msg))
            if (len(values)!=2):
                raise ValidationException("{} is not a valid robot position".format(msg))
        elif(type==PMessage.T_LOAD_MAP):
            return
        else:
            raise ValidationException("{} is not a valid message type".format(type))