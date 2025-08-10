
def getChoiceLabel(choices, value):
    for val, label in choices:
        if val == value:
            return label
    return None  # Si no lo encuentra

def getChoiceValue(choices, value):
    for val, lbl in choices:
        if lbl == value:
            return val
    return None  # Si no lo encuentra