from collections import UserList

class Matrix(UserList):
    def __init__(self, width, length, fill_with = None):
        filler = fill_with or (lambda: 0,)
        self.data = [([filler[0](*filler[1:])] * width).copy() for _ in range(length)]
