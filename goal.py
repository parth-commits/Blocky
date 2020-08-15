"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations

import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    x = random.choice([0, 1])
    col_list = COLOUR_LIST[:]
    temp = num_goals
    ret_lst = []
    if x == 0:  # 0 is for perimeter goal
        for _ in range(temp):
            y = random.choice(col_list)  # a tuple of colour
            ret_lst.append(PerimeterGoal(y))
            col_list.remove(y)
        return ret_lst
    else:  # blob goal
        for _ in range(temp):
            y = random.choice(col_list)  # a tuple of colour
            ret_lst.append(BlobGoal(y))
            col_list.remove(y)
        return ret_lst


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if block.level == block.max_depth:  # if its a unit block already
        return [[block.colour]]
    elif not block.children:  # not a unit block, but doesnt have children
        side = 2**(block.max_depth - block.level)
        flat = []
        for _ in range(side):
            row = []
            for _ in range(side):
                row.append(block.colour)
            flat.append(row)
        return flat
    else:  # not a unit block, and HAS children
        # 2  1
        # 3  4
        flat = []
        one = _flatten(block.children[0])
        two = _flatten(block.children[1])
        three = _flatten(block.children[2])
        four = _flatten(block.children[3])
        if len(one) == 1:  # if it looks like this: [[unit]]
            # note: if one is a unit, then all are units
            # returns a 2x2
            return [[two[0][0], three[0][0]], [one[0][0], four[0][0]]]
        else:  # now its a 2x2, 4x4, 8x8 etc
            for x in range(len(one)):
                row = []  # each row is actually a column
                row.extend(two[x])
                row.extend(three[x])
                flat.append(row)
            for x in range(len(one)):
                row = []
                row.extend(one[x])
                row.extend(four[x])
                flat.append(row)
            return flat


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """ This is an instance of a perimeter goal.
    What is a perimeter goal is in the description
    """
    def score(self, board: Block) -> int:
        flat = _flatten(board)
        score = 0
        for i in range(len(flat)):
            if flat[0][i] == self.colour:
                score += 1
            if flat[-1][i] == self.colour:
                score += 1
            if flat[i][0] == self.colour:
                score += 1
            if flat[i][-1] == self.colour:
                score += 1
        return score

    def description(self) -> str:
        return 'Make the largest ' + colour_name(self.colour) + \
               ' border around the board'


class BlobGoal(Goal):
    """This is an instance of a blob goal.
    What a blob goal is in description
    """
    def score(self, board: Block) -> int:
        flat = _flatten(board)
        visited = []
        for i in range(len(flat)):
            col = []
            for _ in range(len(flat)):
                col.append(-1)
            visited.append(col)
        score = 0
        for i in range(len(flat)):
            for j in range(len(flat)):
                temp_score = self._undiscovered_blob_size((i, j), flat, visited)
                if temp_score > score:
                    score = temp_score
        return score

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        x = pos[0]  # column
        y = pos[1]  # row
        # location out of bounds
        if x < 0 or x >= len(board) or y < 0 or y >= len(board):
            return 0
        # location is visited
        elif visited[x][y] == 0 or visited[x][y] == 1:
            return 0
        # location is not visited, checks if not right colour for goal
        elif board[x][y] != self.colour:
            visited[x][y] = 0
            return 0
        # location is still not visited, colour at pos is correct, now ask
        # neighbors size
        else:
            visited[x][y] = 1
            top = self._undiscovered_blob_size((x, y - 1), board, visited)
            bottom = self._undiscovered_blob_size((x, y + 1), board, visited)
            left = self._undiscovered_blob_size((x - 1, y), board, visited)
            right = self._undiscovered_blob_size((x + 1, y), board, visited)
            return 1 + top + bottom + left + right

    def description(self) -> str:
        return 'Make the largest \'blob\' (area) of' + colour_name(self.colour)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
