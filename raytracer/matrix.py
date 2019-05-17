from collections import UserList

class Matrix(UserList):
    def __init__(self, width, length):
        self.data = [([0] * width).copy() for _ in range(length)]
