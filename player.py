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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    num_goals = num_human + num_random + len(smart_players)
    goals = generate_goals(num_goals)
    lst = []
    mid = num_human + num_random
    for i in range(num_goals):
        if 0 <= i < num_human:
            lst.append(HumanPlayer(i, goals[i]))
        elif num_human <= i < mid:
            lst.append(RandomPlayer(i, goals[i]))
        else:
            lst.append(SmartPlayer(i, goals[i], smart_players[i-num_human -
                                                              num_random]))
    return lst


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    x = location[0]
    y = location[1]
    x_o = block.position[0]
    y_o = block.position[1]
    x_m = x_o + block.size
    y_m = y_o + block.size
    if x_o <= x < x_m and y_o <= y < y_m:
        if level == block.level or block.level == block.max_depth:
            return block
        for child in block.children:
            if _get_block(child, location, level) is not None:
                return _get_block(child, location, level)
    return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """ A random player who make moves at random"""
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        action_list = list(KEY_ACTION.values())

        while True:
            copy_board = board.create_copy()

            # choose a random level for block
            level = random.choice(list(range(0, copy_board.max_depth + 1)))
            # choose a random location
            max1 = 2 ** copy_board.max_depth
            unit_size = copy_board.size // max1
            pos = (random.choice(list(range(0, max1))) * unit_size,
                   random.choice(list(range(0, max1))) * unit_size)
            block = _get_block(copy_board, pos, level)  # get a block at random
            # position, and random level
            if block is not None:
                # choose a random action
                action = random.choice(action_list)
                # print(action)
                boardy = _get_block(board, pos, level)

                if action == ROTATE_CLOCKWISE and block.rotate(1):
                    self._proceed = False  # Must set to False before returning!
                    return _create_move(action, boardy)

                elif action == ROTATE_COUNTER_CLOCKWISE and block.rotate(3):
                    self._proceed = False  # Must set to False before returning!
                    return _create_move(action, boardy)

                elif action == SWAP_HORIZONTAL and block.swap(0):
                    self._proceed = False  # Must set to False before returning!
                    return _create_move(action, boardy)

                elif action == SWAP_VERTICAL and block.swap(1):
                    self._proceed = False  # Must set to False before returning!
                    return _create_move(action, boardy)

                elif action == SMASH and block.smash():
                    self._proceed = False  # Must set to False before returning!
                    return _create_move(action, boardy)

                elif action == PAINT and block.paint(self.goal.colour):
                    self._proceed = False  # Must set to False before returning!
                    return _create_move(action, boardy)

                elif action == COMBINE and block.combine():
                    self._proceed = False  # Must set to False before returning!
                    return _create_move(action, boardy)


class SmartPlayer(Player):
    """ A smart player who assesses _diff number of moves and makes the move
    that gives the best score. And if none of the moves increase the score,
    then it decides to pass"""
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _diff:
    #   The level of "smartness of the smart player, i.e. the number of moves
    #   it tries to do to find the max score out of them.
    _proceed: bool
    _diff: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        Player.__init__(self, player_id, goal)
        self._diff = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove
        action_list = list(KEY_ACTION.values())
        max_scorer = None
        max_score = 0
        i = 0
        while i < self._diff:
            copy_board = board.create_copy()
            # get a random level
            level = random.choice(list(range(0, copy_board.max_depth + 1)))
            max1 = 2 ** copy_board.max_depth
            unit_size = copy_board.size // max1
            pos = (random.choice(list(range(0, max1))) * unit_size,
                   random.choice(list(range(0, max1))) * unit_size)
            block = _get_block(copy_board, pos, level)  # get a block at random
            # position, and random level
            # choose a random action
            action = random.choice(action_list)
            if block is not None and action is not PASS:
                boardy = _get_block(board, pos, level)
                i += 1
                if action == ROTATE_CLOCKWISE and block.rotate(1) and \
                        self.goal.score(block) > max_score:
                    max_score = self.goal.score(block)
                    max_scorer = _create_move(action, boardy)

                elif action == ROTATE_COUNTER_CLOCKWISE and block.rotate(3) and\
                        self.goal.score(block) > max_score:
                    max_score = self.goal.score(block)
                    max_scorer = _create_move(action, boardy)

                elif action == SWAP_HORIZONTAL and block.swap(0) and \
                        self.goal.score(block) > max_score:
                    max_score = self.goal.score(block)
                    max_scorer = _create_move(action, boardy)

                elif action == SWAP_VERTICAL and block.swap(1) and \
                        self.goal.score(block) > max_score:
                    max_score = self.goal.score(block)
                    max_scorer = _create_move(action, boardy)

                elif action == SMASH and block.smash() and \
                        self.goal.score(block) > max_score:
                    max_score = self.goal.score(block)
                    max_scorer = _create_move(action, boardy)

                elif action == PAINT and block.paint(self.goal.colour) and \
                        self.goal.score(block) > max_score:
                    max_score = self.goal.score(block)
                    max_scorer = _create_move(action, boardy)

                elif action == COMBINE and block.combine() and \
                        self.goal.score(block) > max_score:
                    max_score = self.goal.score(block)
                    max_scorer = _create_move(action, boardy)

        if max_score <= self.goal.score(board):
            self._proceed = False  # Must set to False before returning!
            return _create_move(PASS, board)
        else:
            self._proceed = False  # Must set to False before returning!
            return max_scorer


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
