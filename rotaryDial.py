from threading import Timer 

class RotaryDial:

    keypadMatrix = [
        [" "],
        ["a", "b", "c", "2"],
        ["d", "e", "f", "3"],
        ["g", "h", "i", "4"],
        ["j", "k", "l", "5"],
        ["m", "n", "o", "6"],
        ["p", "r", "s", "7"],
        ["t", "u", "v", "8"],
        ["w", "x", "y", "9"],
        ["DELETE"]
    ]

    readlineString      = ""

    def appendNumberToList(self, readlineString, searchList):

        newList = []

        if len(searchList) > 0: 
            for searchString in searchList:
                for character in RotaryDial.keypadMatrix[ int(readlineString)-1 ]:
                    newList.append( searchString + character )
        else:
            for character in RotaryDial.keypadMatrix[ int(readlineString)-1 ]:
                newList.append( character )

        return newList
