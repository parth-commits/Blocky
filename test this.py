from assignments.a2.block import Block
from assignments.a2.goal import *
from assignments.a2.goal import _flatten

def my_test_flatten():
    p = (1, 128, 181)
    o = (138, 151, 71)
    r = (199, 44, 58)
    d = (255, 211, 92)
    main = Block((0, 0), 750, None, 0, 3)

    child_zero = Block((375, 0), 375, None, 1, 3)
    main_one = Block((0, 0), 375, r, 1, 3)
    main_two = Block((0, 375), 375, p, 1, 3)
    main_three = Block((375, 375), 375, d, 1, 3)

    hello = Block((563, 0), 188, None, 2, 3)
    child_one = Block((375, 0), 188, r, 2, 3)
    child_two = Block((375, 188), 188, p, 2, 3)
    child_three = Block((563, 188), 188, d, 2, 3)

    hello_zero = Block((657, 0), 94, o, 3, 3)
    hello_one = Block((563, 0), 94, r, 3, 3)
    hello_two = Block((563, 94), 94, p, 3, 3)
    hello_three = Block((657, 94), 94, d, 3, 3)

    hello.children = [hello_zero, hello_one, hello_two, hello_three]
    child_zero.children = [hello, child_one, child_two, child_three]
    main.children = [child_zero, main_one, main_two, main_three]

    x = _flatten(main)
    y = [[r,r,r,r,p,p,p,p],
         [r,r,r,r,p,p,p,p],
         [r,r,r,r,p,p,p,p],
         [r,r,r,r,p,p,p,p],
         [r,r,p,p,d,d,d,d],
         [r,r,p,p,d,d,d,d],
         [r,p,d,d,d,d,d,d],
         [o,d,d,d,d,d,d,d],]
    print(x == y)


if __name__ == '__main__':
    my_test_flatten()
