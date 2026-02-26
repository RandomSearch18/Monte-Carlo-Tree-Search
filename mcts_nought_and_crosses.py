"""
Monte Carlo Tree Search [py] File
Copyright Loughborough University
"""

import random
import math
from copy import deepcopy

# -----------------------------
# Game configuration
# -----------------------------
ROWS = 4
COLS = 5
WIN_LENGTH = 4

EMPTY = "."
HUMAN = "X"
AI = "O"


# -----------------------------
# Board utilities
# -----------------------------
def new_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def print_board(board):
    for row in board:
        print(" ".join(row))
    print()


def available_moves(board):
    return [(r, c) for r in range(ROWS) for c in range(COLS) if board[r][c] == EMPTY]


def make_move(board, move, player):
    r, c = move
    board[r][c] = player


# -----------------------------
# Win checking
# -----------------------------
def check_winner(board, player):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != player:
                continue

            # horizontal
            if c + WIN_LENGTH <= COLS:
                if all(board[r][c + i] == player for i in range(WIN_LENGTH)):
                    return True

            # vertical
            if r + WIN_LENGTH <= ROWS:
                if all(board[r + i][c] == player for i in range(WIN_LENGTH)):
                    return True

            # diagonal down-right
            if r + WIN_LENGTH <= ROWS and c + WIN_LENGTH <= COLS:
                if all(board[r + i][c + i] == player for i in range(WIN_LENGTH)):
                    return True

            # diagonal down-left
            if r + WIN_LENGTH <= ROWS and c - WIN_LENGTH >= -1:
                if all(board[r + i][c - i] == player for i in range(WIN_LENGTH)):
                    return True
    return False


def is_draw(board):
    return not available_moves(board)


# -----------------------------
# MCTS Node
# -----------------------------
class Node:
    def __init__(self, board, player, parent=None, move=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.move = move

        self.children = []
        self.visits = 0
        self.wins = 0


# -----------------------------
# UCB1
# -----------------------------
def ucb(child, parent_visits, c=1.4):
    if child.visits == 0:
        return float("inf")
    return (child.wins / child.visits) + c * math.sqrt(
        math.log(parent_visits) / child.visits
    )


# -----------------------------
# MCTS steps
# -----------------------------
def select(node):
    while node.children:
        node = max(node.children, key=lambda n: ucb(n, node.visits))
    return node


def expand(node):
    for move in available_moves(node.board):
        b = deepcopy(node.board)
        make_move(b, move, node.player)
        node.children.append(Node(b, HUMAN if node.player == AI else AI, node, move))


def simulate(board, player):
    b = deepcopy(board)
    current = player

    while True:
        if check_winner(b, AI):
            return AI
        if check_winner(b, HUMAN):
            return HUMAN
        if is_draw(b):
            return None

        move = random.choice(available_moves(b))
        make_move(b, move, current)
        current = HUMAN if current == AI else AI


def backpropagate(node, winner):
    while node:
        node.visits += 1
        if winner == AI:
            node.wins += 1
        node = node.parent


# -----------------------------
# MCTS decision
# -----------------------------
def mcts_move(board, simulations=200):
    root = Node(deepcopy(board), AI)

    for _ in range(simulations):
        leaf = select(root)
        if leaf.visits > 0:
            expand(leaf)
            if leaf.children:
                leaf = random.choice(leaf.children)
        winner = simulate(leaf.board, leaf.player)
        backpropagate(leaf, winner)

    print("\n--- MCTS Move Statistics ---")
    for child in root.children:
        win_rate = child.wins / child.visits if child.visits > 0 else 0
        print(f"Move {child.move}: visits={child.visits}, win rate={win_rate:.2f}")

    best = max(root.children, key=lambda n: n.visits)
    print(f"Chosen move: {best.move}\n")
    return best.move


# -----------------------------
# Game loop
# -----------------------------
def play():
    board = new_board()
    print_board(board)

    while True:
        r = int(input("Row: "))
        c = int(input("Col: "))
        make_move(board, (r, c), HUMAN)
        print_board(board)

        if check_winner(board, HUMAN):
            print("You win!")
            return

        move = mcts_move(board, simulations=200)
        make_move(board, move, AI)
        print_board(board)

        if check_winner(board, AI):
            print("AI wins!")
            return

        if is_draw(board):
            print("Draw!")
            return


play()
