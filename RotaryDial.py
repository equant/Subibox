class RotaryDial:

    keypadMatrix = [
        ["a", "b", "c",      "2"],
        ["d", "e", "f",      "3"],
        ["g", "h", "i",      "4"],
        ["j", "k", "l",      "5"],
        ["m", "n", "o",      "6"],
        ["p", "q", "r", "s", "7"],
        ["t", "u", "v",      "8"],
        ["w", "x", "y", "z", "9"],
        ["DELETE"]
    ]

    readlineString      = ""

    def rotaryNumberToList(self, readlineString, searchList):

        newList = []

        if len(searchList) > 0: 
            for searchString in searchList:
                for character in RotaryDial.keypadMatrix[ int(readlineString)-2 ]:
                    newList.append( searchString + character )
        else:
            for character in RotaryDial.keypadMatrix[ int(readlineString)-2 ]:
                newList.append( character )

        return newList
