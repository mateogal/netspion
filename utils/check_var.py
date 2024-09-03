from . import string_format as sf


def check_vars(varList):
    msg = ""
    for var in varList:
        if var["value"] == "":
            msg += f"{var['name']}, "
    if msg != "":
        print(sf.fail(f"{msg}variables are empty."))
        return 0
    else:
        return 1
