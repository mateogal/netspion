from termcolor import colored


def title(string):
    return colored(string, "yellow", attrs=["bold", "blink"]).rjust(70)


def warning(string):
    return colored(string, "yellow", attrs=["bold"])


def success(string):
    return colored(string, "green", attrs=["bold"])


def text(string):
    return colored(string, "green")


def fail(string):
    return colored(string, "red", attrs=["bold"])


def info(string):
    return colored(string, "blue", attrs=["bold"])
