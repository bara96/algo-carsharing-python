import numpy as np


def console_log(message, color='red', newline=False):
    """
    Print a colored console message
    :param message:
    :param color:
    :param newline:
    """
    nl = ''
    if newline:
        nl = '\n'
    if color == 'red':
        print("{}\033[91m{}\033[0m".format(nl, message))
    elif color == 'green':
        print("{}\033[92m{}\033[0m".format(nl, message))
    elif color == 'yellow':
        print("{}\033[93m{}\033[0m".format(nl, message))
    elif color == 'blue':
        print("{}\033[94m{}\033[0m".format(nl, message))
    else:
        print("\033[0m{}{}".format(nl, message))


def toArray(obj):
    data = list(obj.items())
    return np.array(data)


def parse_response(response):
    """
    Parse a response into json
    :param response:
    """
    import json
    res = json.dumps(response, indent=2, sort_keys=True)
    print(res)
    return res
