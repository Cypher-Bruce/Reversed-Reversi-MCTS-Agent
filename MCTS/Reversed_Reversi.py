from math import sqrt, log
import random
import time

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
GAME_STATUS_GOING = -2
GAME_STATUS_TIE = 2
random.seed(0)


class AI(object):

    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

    def go(self, chessboard):
        self.candidate_list.clear()

        # chessboard = chessboard.tolist()
        self.candidate_list = ReversiSimulator.get_valid_moves(chessboard, self.color)
        if len(self.candidate_list) == 0:
            return
        mcts = MCTS(Node(None, chessboard, self.color, None))
        mcts.find_best_move(self.time_out)
        self.candidate_list.append(mcts.best_move)


class MCTS:

    def __init__(self, root):
        self.root = root
        self.best_move = None

    def find_rollout_node(self):
        node = self.root
        while True:
            if node.winner != GAME_STATUS_GOING:
                return node
            if len(node.children) == 0:
                self.generate_children(node)
                return random.choice(node.children)
            else:
                for child in node.children:
                    child.set_uct_value()
                node = max(node.children, key=lambda x: x.UCT_value)
                if node.visited == 0:
                    return node

    def generate_children(self, node):
        valid_moves = ReversiSimulator.get_valid_moves(node.chessboard, node.color)
        if len(valid_moves) == 0:
            new_chessboard = [row[:] for row in node.chessboard]
            new_node = Node(node, new_chessboard, -node.color, None)
            new_node.winner = GAME_STATUS_GOING
            node.children.append(new_node)
            return
        for move in valid_moves:
            new_chessboard = ReversiSimulator.perform_move([row[:] for row in node.chessboard], node.color, move)
            new_node = Node(node, new_chessboard, -node.color, move)
            new_node.winner = ReversiSimulator.check_status(new_chessboard, node.color)
            node.children.append(new_node)

    def back_propagation(self, node, winner_score):
        while node is not None:
            node.visited += 1
            if node.color * winner_score > 0:
                node.wins += abs(winner_score)
            elif node.color * winner_score < 0:
                node.losses += abs(winner_score)
            else:
                node.ties += 1
            node = node.parent

    def find_best_move(self, time_limit):
        start_time = time.time()
        while time.time() - start_time < time_limit * 0.95:
            node = self.find_rollout_node()
            winner_score = ReversiSimulator.rollout(node)
            self.back_propagation(node, winner_score)

        num_visits = 0
        for child in self.root.children:
            print(child.move, child.visited, child.wins, child.losses, child.ties, child.UCT_value)
            if child.visited > num_visits:
                num_visits = child.visited
                self.best_move = child.move


class Node:
    def __init__(self, parent, chessboard, color, move):
        self.parent = parent
        self.chessboard = chessboard
        self.color = color
        self.move = move
        self.children = []
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.visited = 0
        self.UCT_value = 0
        self.winner = GAME_STATUS_GOING

    def set_uct_value(self):
        if self.visited == 0:
            self.UCT_value = float('inf')
        else:
            self.UCT_value = (self.wins + self.ties) / (self.wins + self.losses + self.ties) + 10 * sqrt(log(self.parent.visited) / self.visited)


class ReversiSimulator:

    @staticmethod
    def rollout(node):
        if node.winner != GAME_STATUS_GOING:
            return sum(sum(row) for row in node.chessboard)
        chessboard = [row[:] for row in node.chessboard]
        player = node.color
        frontier = ReversiSimulator.find_frontier(node.chessboard)
        has_no_move = False
        depth = 0
        max_depth = 20
        while True:
            valid_moves = ReversiSimulator.get_valid_moves_with_frontier(chessboard, player, frontier)
            if len(valid_moves) != 0:
                move = random.choice(valid_moves)
                chessboard = ReversiSimulator.perform_move(chessboard, player, move)
                ReversiSimulator.update_frontier(chessboard, frontier, move)
                has_no_move = False
            else:
                if has_no_move:
                    break
                has_no_move = True
            player = -player
            depth += 1
            if depth >= max_depth:
                break

        return sum(sum(row) for row in chessboard)


    @staticmethod
    def get_valid_moves(chessboard, color):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        valid_moves = []

        # Iterate through the board to find the player's pieces
        for row in range(8):
            for col in range(8):
                if chessboard[row][col] == color:
                    # For each piece, check all directions for potential valid moves
                    for dr, dc in directions:
                        r, c = row + dr, col + dc
                        # Move in the direction until you hit an opponent's piece or go out of bounds
                        while 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == -color:
                            r += dr
                            c += dc
                        # If the next spot is empty and not the immediate next spot, it's a valid move
                        if 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == 0 and (r - dr, c - dc) != (row, col) and (r, c) not in valid_moves:
                            valid_moves.append((r, c))

        return valid_moves

    @staticmethod
    def find_frontier(chessboard):
        frontier = []
        for i in range(8):
            for j in range(8):
                if chessboard[i][j] == COLOR_NONE:
                    for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                        r, c = i + dr, j + dc
                        if 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] != COLOR_NONE:
                            frontier.append((i, j))
                            break
        return frontier

    @staticmethod
    def get_valid_moves_with_frontier(chessboard, color, frontier):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        valid_moves = []

        for row, col in frontier:
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == -color:
                    r += dr
                    c += dc
                if 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == color and (r - dr, c - dc) != (row, col):
                    valid_moves.append((row, col))
                    break
        return valid_moves

    @staticmethod
    def update_frontier(chessboard, frontier, move):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        frontier.remove(move)
        for dr, dc in directions:
            r, c = move[0] + dr, move[1] + dc
            if 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == COLOR_NONE and (r, c) not in frontier:
                frontier.append((r, c))

    @staticmethod
    def check_status(chessboard, color):
        opponent_moves = len(ReversiSimulator.get_valid_moves(chessboard, -color))
        if opponent_moves != 0:
            return GAME_STATUS_GOING
        player_moves = len(ReversiSimulator.get_valid_moves(chessboard, color))
        if player_moves != 0:
            return GAME_STATUS_GOING
        total_sum = sum(sum(row) for row in chessboard)
        if total_sum > 0:
            return COLOR_BLACK
        elif total_sum < 0:
            return COLOR_WHITE
        else:
            return GAME_STATUS_TIE

    @staticmethod
    def perform_move(chessboard, color, move):
        chessboard[move[0]][move[1]] = color
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            r, c = move[0] + dr, move[1] + dc
            while 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == -color:
                r += dr
                c += dc
            if 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == color and (r - dr, c - dc) != move:
                r -= dr
                c -= dc
                while 0 <= r < 8 and 0 <= c < 8 and chessboard[r][c] == -color:
                    chessboard[r][c] = color
                    r -= dr
                    c -= dc
        return chessboard

    @staticmethod
    def print_chessboard(chessboard):
        print("# 0 1 2 3 4 5 6 7")
        for i in range(8):
            print(i, end=' ')
            for j in range(8):
                if chessboard[i][j] == COLOR_BLACK:
                    print('B', end=' ')
                elif chessboard[i][j] == COLOR_WHITE:
                    print('W', end=' ')
                else:
                    print('-', end=' ')
            print()
