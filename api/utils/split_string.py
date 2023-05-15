def splitString(string, delimiter=","):
    if delimiter in string:
        return string.split(delimiter)
    else:
        return [string]
