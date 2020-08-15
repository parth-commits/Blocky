from __future__ import annotations

from typing import List, Optional, Tuple
import os
import pygame
import pytest

from block import Block, generate_board
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals
from player import Player, HumanPlayer, SmartPlayer, \
    RandomPlayer, _get_block, create_players
from renderer import Renderer
from settings import COLOUR_LIST

# === TASK 2 ===


def test_smash_block_no_children() -> None:
    b = Block((0, 0), 500, COLOUR_LIST[0], 0, 2)
    assert b.smash()
    assert len(b.children) == 4
    assert b.colour is None


def test_smash_block_with_children() -> None:
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 200, None, 1, 2),
                  Block(b._children_positions()[1], 200, None, 1, 2),
                  Block(b._children_positions()[2], 200, None, 1, 2),
                  Block(b._children_positions()[3], 200, None, 1, 2)]
    assert not b.smash()


# === TASK 3 ===


def test_generate_goals() -> None:
    goals = generate_goals(4)
    assert len(goals) == 4
    if type(goals[0]) == PerimeterGoal:
        for item in goals:
            assert type(item) == PerimeterGoal
    if type(goals[0]) == BlobGoal:
        for item in goals:
            assert type(item) == BlobGoal


def test_generate_goals_colours() -> None:
    goals = generate_goals(4)
    assert goals[0].colour in COLOUR_LIST

# === TASK 4 ===


def test_create_players_01() -> None:
    players = create_players(1, 1, [2, 4])
    assert len(players) == 4
    assert players[0].id == 0
    assert players[1].id == 1
    assert type(players[0]) == HumanPlayer
    assert type(players[1]) == RandomPlayer
    assert type(players[2]) == SmartPlayer
    assert type(players[3]) == SmartPlayer
    assert players[3]._diff == 4


def test_create_players_02() -> None:
    players = create_players(1, 1, [2, 4])
    for player in players:
        assert type(player.goal) == PerimeterGoal or \
               type(player.goal) == BlobGoal

# === TASK 5 ===

# SWAP


def test_swap_no_children() -> None:
    b = Block((0, 0), 500, COLOUR_LIST[0], 0, 2)
    assert not b.swap(1)

# Fails cuz we give it 2 and 5, which is not said in docstring
def test_swap_invalid_direction() -> None:
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 250, None, 1, 2),
                  Block(b._children_positions()[1], 250, None, 1, 2),
                  Block(b._children_positions()[2], 250, None, 1, 2),
                  Block(b._children_positions()[3], 250, None, 1, 2)]
    assert not b.swap(2)
    assert not b.swap(5)


def test_swap_v_block_max_level_1() -> None:
    b = Block((0, 0), 500, None, 0, 1)
    b.children = [Block(b._children_positions()[0], 250, COLOUR_LIST[0], 1, 1),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 1),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 1),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 1)]
    assert b.swap(1)
    assert b.children == [Block(b._children_positions()[0], 250,
                                COLOUR_LIST[3], 1, 1),
                          Block(b._children_positions()[1], 250,
                                COLOUR_LIST[2], 1, 1),
                          Block(b._children_positions()[2], 250,
                                COLOUR_LIST[1], 1, 1),
                          Block(b._children_positions()[3], 250,
                                COLOUR_LIST[0], 1, 1)]


def test_swap_h_block_max_level_1() -> None:
    b = Block((0, 0), 500, None, 0, 1)
    b.children = [Block(b._children_positions()[0], 250, COLOUR_LIST[0], 1, 1),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 1),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 1),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 1)]
    assert b.swap(0)
    assert b.children == [Block(b._children_positions()[0], 250,
                                COLOUR_LIST[1], 1, 1),
                          Block(b._children_positions()[1], 250,
                                COLOUR_LIST[0], 1, 1),
                          Block(b._children_positions()[2], 250,
                                COLOUR_LIST[3], 1, 1),
                          Block(b._children_positions()[3], 250,
                                COLOUR_LIST[2], 1, 1)]


def test_swap_v_block_max_level_2() -> None:
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 250, None, 1, 2),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 2),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 2),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 2)]
    b.children[0].children = [Block(b.children[0]._children_positions()[0], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[1],
                                    125, COLOUR_LIST[0], 2, 2),
                              Block(b.children[0]._children_positions()[2], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[3], 125,
                                    COLOUR_LIST[3], 2, 2)]
    assert b.swap(1)
    c = Block((0, 0), 500, None, 0, 2)
    c.children = [Block((250, 0), 250, COLOUR_LIST[3], 1, 2),
                  Block((0, 0), 250, COLOUR_LIST[2], 1, 2),
                  Block((0, 250), 250, COLOUR_LIST[1], 1, 2),
                  Block((250, 250), 250, None, 1, 2)]
    c.children[3].children = [Block((375, 250), 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block((250, 250),
                                    125, COLOUR_LIST[0], 2, 2),
                              Block((250, 375), 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block((375, 375), 125,
                                    COLOUR_LIST[3], 2, 2)]
    assert b == c

# ROTATE


def test_rotate_no_children()-> None:
    c = Block((0, 0), 500, COLOUR_LIST[1], 0, 0)
    assert not c.rotate(1)
    assert not c.rotate(0)

def test_rotate_counter_max_level_1() -> None:
    b = Block((0, 0), 500, None, 0, 1)
    b.children = [Block(b._children_positions()[0], 250, COLOUR_LIST[0], 1, 1),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 1),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 1),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 1)]
    assert b.rotate(3)
    assert b.children == [Block(b._children_positions()[0], 250,
                                COLOUR_LIST[3], 1, 1),
                          Block(b._children_positions()[1], 250,
                                COLOUR_LIST[0], 1, 1),
                          Block(b._children_positions()[2], 250,
                                COLOUR_LIST[1], 1, 1),
                          Block(b._children_positions()[3], 250,
                                COLOUR_LIST[2], 1, 1)]

def test_rotate_clockwise_max_level_1() -> None:
    b = Block((0, 0), 500, None, 0, 1)
    b.children = [Block(b._children_positions()[0], 250, COLOUR_LIST[0], 1, 1),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 1),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 1),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 1)]
    assert b.rotate(1)
    assert b.children == [Block(b._children_positions()[0], 250,
                                COLOUR_LIST[1], 1, 1),
                          Block(b._children_positions()[1], 250,
                                COLOUR_LIST[2], 1, 1),
                          Block(b._children_positions()[2], 250,
                                COLOUR_LIST[3], 1, 1),
                          Block(b._children_positions()[3], 250,
                                COLOUR_LIST[0], 1, 1)]

def test_rotate_clockwise_max_level_2() -> None:
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 250, None, 1, 2),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 2),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 2),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 2)]
    b.children[0].children = [Block(b.children[0]._children_positions()[0], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[1],
                                    125, COLOUR_LIST[0], 2, 2),
                              Block(b.children[0]._children_positions()[2], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[3], 125,
                                    COLOUR_LIST[3], 2, 2)]
    assert b.rotate(1)
    c = Block((0, 0), 500, None, 0, 2)
    c.children = [Block((250, 0), 250, COLOUR_LIST[1], 1, 2),
                  Block((0, 0), 250, COLOUR_LIST[2], 1, 2),
                  Block((0, 250), 250, COLOUR_LIST[3], 1, 2),
                  Block((250, 250), 250, None, 1, 2)]
    c.children[3].children = [Block((375, 250), 125,
                                    COLOUR_LIST[0], 2, 2),
                              Block((250, 250),
                                    125, COLOUR_LIST[2], 2, 2),
                              Block((250, 375), 125,
                                    COLOUR_LIST[3], 2, 2),
                              Block((375, 375), 125,
                                    COLOUR_LIST[2], 2, 2)]
    assert b == c

# PAINT

def test_paint_invalid_cases() -> None:
    # Not at max_depth
    c = Block((0, 0), 500, COLOUR_LIST[1], 0, 1)
    assert not c.paint(COLOUR_LIST[1])
    # Not a leaf
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 250, None, 1, 2),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 2),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 2),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 2)]
    assert not c.paint(COLOUR_LIST[1])
    # Already has target color
    a = Block((0, 0), 500, COLOUR_LIST[1], 0, 0)
    assert not a.paint(COLOUR_LIST[1])


def test_paint_no_children_level_0() -> None:
    b = Block((0, 0), 500, COLOUR_LIST[1], 0, 0)
    assert b.paint(COLOUR_LIST[3])
    assert b.colour == COLOUR_LIST[3]


def test_paint_at_level_2() -> None:
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 250, None, 1, 2),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 2),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 2),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 2)]
    b.children[0].children = [Block(b.children[0]._children_positions()[0], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[1],
                                    125, COLOUR_LIST[0], 2, 2),
                              Block(b.children[0]._children_positions()[2], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[3], 125,
                                    COLOUR_LIST[3], 2, 2)]
    assert b.children[0].children[0].paint(COLOUR_LIST[0])
    assert b.children[0].children[0].colour == COLOUR_LIST[0]
    assert not b.children[1].paint(COLOUR_LIST[0])

# COMBINE

def test_combine_invalid_cases() -> None:
    # No children
    b = Block((0, 0), 500, COLOUR_LIST[1], 0, 0)
    assert not b.combine()
    # Not at level max_depth - 1
    c = Block((0, 0), 500, None, 0, 2)
    assert not c.combine()

def test_combine_no_dominant_color() -> None:
    d = Block((0, 0), 500, None, 0, 1)
    d.children = [Block(d._children_positions()[0], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[1], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[2], 250, COLOUR_LIST[2], 1, 1),
                  Block(d._children_positions()[3], 250, COLOUR_LIST[2], 1, 1)]
    assert not d.combine()


def test_combine_3_vs_1() -> None:
    d = Block((0, 0), 500, None, 0, 1)
    d.children = [Block(d._children_positions()[0], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[1], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[2], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[3], 250, COLOUR_LIST[3], 1, 1)]
    assert d.combine()
    assert d.colour == COLOUR_LIST[1]


def test_combine_4_vs_0() -> None:
    d = Block((0, 0), 500, None, 0, 1)
    d.children = [Block(d._children_positions()[0], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[1], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[2], 250, COLOUR_LIST[1], 1, 1),
                  Block(d._children_positions()[3], 250, COLOUR_LIST[1], 1, 1)]
    assert d.combine()
    assert d.colour == COLOUR_LIST[1]


# === TASK 6 ===


# FLATTEN

def set_children(block: Block, colours: List[Optional[Tuple[int, int, int]]]) \
        -> None:
    """Set the children at <level> for <block> using the given <colours>.

    Precondition:
        - len(colours) == 4
        - block.level + 1 <= block.max_depth
    """
    size = block._child_size()
    positions = block._children_positions()
    level = block.level + 1
    depth = block.max_depth

    block.children = []  # Potentially discard children
    for i in range(4):
        b = Block(positions[i], size, colours[i], level, depth)
        block.children.append(b)


def test_flatten_01() -> None:
    board = Block((0, 0), 750, None, 0, 2)
    colours = [None, COLOUR_LIST[2], None, COLOUR_LIST[3]]
    set_children(board, colours)

    colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[0], colours)

    colours = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[3]]
    set_children(board.children[2], colours)

    result = _flatten(board)
    assert result == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1],
                                COLOUR_LIST[0]], [COLOUR_LIST[2], COLOUR_LIST[2],
                                                  COLOUR_LIST[1], COLOUR_LIST[3]],
                               [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3],
                               COLOUR_LIST[3]], [COLOUR_LIST[0], COLOUR_LIST[3],
                               COLOUR_LIST[3], COLOUR_LIST[3]]]


def test_flatten_02() -> None:

    board = Block((0, 0), 750, None, 0, 3)

    colours = [None, None, None, None]
    set_children(board, colours)

    colours = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3]]
    set_children(board.children[0], colours)
    colours = [COLOUR_LIST[0], COLOUR_LIST[2], None, COLOUR_LIST[1]]
    set_children(board.children[1], colours)
    colours = [None, COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0]]
    set_children(board.children[2], colours)
    colours = [None, COLOUR_LIST[0], COLOUR_LIST[3], None]
    set_children(board.children[3], colours)

    colours = [COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[3]]
    set_children(board.children[1].children[2], colours)
    colours = [COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[3]]
    set_children(board.children[2].children[0], colours)
    colours = [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[3].children[0], colours)
    colours = [COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[0]]
    set_children(board.children[3].children[3], colours)

    result = _flatten(board)
    assert result == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[2]],
                    [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[2]],
    [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0]],
    [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[0]],
    [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3]],
    [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3]],
    [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]],
    [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[0]]]

# SCORE PERIMETERGOAL

def test_score_perimeter_goal_no_children() -> None:
    b = Block((0, 0), 500, COLOUR_LIST[1], 0, 2)
    P = PerimeterGoal(COLOUR_LIST[1])
    assert P.score(b) == 16


def test_score_perimeter_goal_no_children_max_depth_3() -> None:
    b = Block((0, 0), 500, COLOUR_LIST[1], 0, 3)
    P = PerimeterGoal(COLOUR_LIST[1])
    assert P.score(b) == 32


def test_score_perimeter_goal() -> None:
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 250, None, 1, 2),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 2),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 2),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 2)]
    b.children[0].children = [Block(b.children[0]._children_positions()[0], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[1],
                                    125, COLOUR_LIST[0], 2, 2),
                              Block(b.children[0]._children_positions()[2], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[3], 125,
                                    COLOUR_LIST[3], 2, 2)]
    P = PerimeterGoal(COLOUR_LIST[3])
    assert P.score(b) == 5
    b.children[0].children[0].paint(COLOUR_LIST[3])
    assert P.score(b) == 7

# === TASK 7 ===


def test_score_blob_goal_no_children() -> None:
    b = Block((0, 0), 500, COLOUR_LIST[1], 0, 0)
    P = BlobGoal(COLOUR_LIST[1])
    assert P.score(b) == 1
    b = Block((0, 0), 500, COLOUR_LIST[1], 0, 1)
    assert P.score(b) == 4


def test_score_blob_goal_02() -> None:
    b = Block((0, 0), 500, None, 0, 2)
    b.children = [Block(b._children_positions()[0], 250, None, 1, 2),
                  Block(b._children_positions()[1], 250, COLOUR_LIST[1], 1, 2),
                  Block(b._children_positions()[2], 250, COLOUR_LIST[2], 1, 2),
                  Block(b._children_positions()[3], 250, COLOUR_LIST[3], 1, 2)]
    b.children[0].children = [Block(b.children[0]._children_positions()[0], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[1],
                                    125, COLOUR_LIST[0], 2, 2),
                              Block(b.children[0]._children_positions()[2], 125,
                                    COLOUR_LIST[2], 2, 2),
                              Block(b.children[0]._children_positions()[3], 125,
                                    COLOUR_LIST[3], 2, 2)]
    P = BlobGoal(COLOUR_LIST[3])
    assert P.score(b) == 5
    b.children[0].children[2].paint(COLOUR_LIST[3])
    assert P.score(b) == 6
    b.children[1].colour = COLOUR_LIST[3]
    assert P.score(b) == 10

# === TASK 8 ===

# RANDOM PLAYER


def test_create_copy() -> None:
    b2 = generate_board(3, 750)
    copy = b2.create_copy()
    assert b2 == copy
    # Deep copy
    assert id(b2) != id(copy)


def test_generate_move_random_player() -> None:
    b2 = generate_board(3, 750)
    P = RandomPlayer(2, PerimeterGoal(COLOUR_LIST[2]))
    P._proceed = True
    assert P.generate_move(b2)[0] in ['swap', 'rotate',
                                      'paint', 'combine', 'smash']


if __name__ == '__main__':
    pytest.main(['testsa2.py'])
