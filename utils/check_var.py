def check_vars(varList):
    for var in varList:
        if not var:
            print("Required variables are empty")
            return 0

    return 1