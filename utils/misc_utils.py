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