import json

import qzig.value as value
import qzig.state as state
import qzig.status as status


class QZigEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is value.ValuePermission:
            return obj.value
        if type(obj) is value.ValueStatus:
            return obj.value
        if type(obj) is state.StateType:
            return obj.value
        if type(obj) is state.StateStatus:
            return obj.value
        if type(obj) is value.ValueNumberType:
            return obj.__dict__
        if type(obj) is value.ValueStringType:
            return obj.__dict__
        if type(obj) is status.StatusType:
            return obj.value
        if type(obj) is status.StatusLevel:
            return obj.value
        # if type(obj) is value.ValueSetType:
        #    return obj.__dict__
        # if type(obj) is value.ValueBlobType:
        #    return obj.__dict__
        # if type(obj) is value.ValueXmlType:
        #    return obj.__dict__
        # return json.JSONEncoder.default(self, obj)
