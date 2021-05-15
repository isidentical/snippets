from dataclasses import dataclass
from typing import List

from turtle import Turtle, mainloop, tracer
from turtledemo.forest import start as initialize_pen, tree as draw_tree

_SENTINEL = object()
_WIDTH_FACTOR = 0.1

@dataclass
class Branch:
    angle: int
    size_factor: int

    def __iter__(self):
        return iter((self.angle, self.size_factor))

@dataclass
class Tree:
    x: int
    y: int
    size: int
    level: int
    branches: List[Branch]

    def run(self):
        pen = Turtle(undobuffersize=1)
        pen.hideturtle()
        
        initialize_pen(pen, self.x, self.y)
        return draw_tree(
            [pen],
            self.size,
            self.level,
            _WIDTH_FACTOR,
            [self.branches]
        )
        
        
def main():
    pen = Turtle()
    pen.ht()

    trees = [
        Tree(
            x=0,
            y=0,
            size=70,
            level=8,
            branches = [
                Branch(45, 0.6),
                Branch(0, 0.5),
                Branch(-45, 0.7)
            ]
        )
    ]
    
    tracer(75,0)
    runners = [tree.run() for tree in trees]

    # move the cursor on each tree one by one
    # so we can see the progress on each tree
    # instead of waiting the first one to be
    # completed.
    while runners:
        for runner in runners.copy():
            if next(runner, _SENTINEL) is not _SENTINEL:
                continue

            runners.remove(runner)

    tracer(1,10)

if __name__ == "__main__":
    main()
    mainloop()
