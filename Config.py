import os
import configparser

configFile = readFromConfig()
configFile.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))


def readFromConfig(section, parameter):
    value = configFile.get(section, parameter)

    isString = isinstance(value, str)

    if isString:
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            return value
    else:
        return value
