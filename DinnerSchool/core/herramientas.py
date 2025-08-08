
def getChoiceLabel(choices, value):
    for val, label in choices:
        if val == value:
            return label
    return None  # Si no lo encuentra