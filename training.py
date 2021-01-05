import numpy as np
import time
import pickle
from random import randint

# The state class deals with the board and each player class
class State:
    def __init__(self, player1, player2):
        self.board = np.zeros((6, 7))
        self.player1 = player1
        self.player2 = player2
        self.boardHash = None  # string of the current board position
        self.player_symbol = 1  # symbol for the current player
        self.isEnd = False

    # get a hash of the current board position
    def getHash(self):
        boardHash = str(self.board.reshape(7 * 6))
        return boardHash

    #  find the slot the token will arrive at if dropped into a certain column
    def find_slot(self, column):
        slot = 0
        for i in range(6):
            if self.board[i][column] != 0:
                break
            slot = i
        return slot

    #  find all available columns
    def available_moves(self):
        # Just check the top row to see if there's space
        moves = []
        for i in range(7):
            if self.board[0][i] == 0:
                moves.append(i)
        return moves

    # determine if the current game has ended
    def winner(self):
        # check rows
        for row in range(6):
            # must make 4 checks to cover the whole row
            for i in range(4):
                if sum(self.board[row][0+i:4+i]) == 4:
                    self.isEnd = True
                    return 1
                elif sum(self.board[row][0+i:4+i]) == -4:
                    self.isEnd = True
                    return -1
        # check columns
        for column in range(7):
            # must make 3 checks to cover the whole column
            for i in range(3):
                if sum(self.board.T[column][0+i:4+i]) == 4:
                    self.isEnd = True
                    return 1
                if sum(self.board.T[column][0+i:4+i]) == -4:
                    self.isEnd = True
                    return -1
        # check diagonals
        # first diagonal (bottom left to top right)
        for column in range(3, 7):
            for row in range(3, 6):
                total = 0
                # add up the 4 diagonals
                for i in range(4):
                    total += self.board[row-i][column-i]
                if total == 4:
                    self.isEnd = True
                    return 1
                if total == -4:
                    self.isEnd = True
                    return -1
        # second diagonal (bottom right to top left)
        for column in range(3, 7):
            for row in range(0, 3):
                total = 0
                # add up the 4 diagonals
                for i in range(4):
                    total += self.board[row+i][column-i]
                if total == 4:
                    self.isEnd = True
                    return 1
                if total == -4:
                    self.isEnd = True
                    return -1
        # Check whether there are any more moves to be played, if not it's a draw
        if len(self.available_moves()) == 0:
            return 0

        # Otherwise return nothing
        return None

    # reset the board and previous board positions
    def reset(self):
        self.board = self.board = np.zeros((6, 7))
        self.boardHash = None
        self.player_symbol = 1
        self.isEnd = False

    def get_flip_hash(self):
        list1 = []
        for row in self.board:
            list1.append(np.flip(row))
        board = np.array(list1)
        boardHash = str(board.reshape(7 * 6))
        return boardHash

    # give the reward only when game ends
    def giveReward(self):
        result = self.winner()
        # back propagate reward
        if result == 1:
            self.player1.feedReward(1)
            self.player2.feedReward(0)
        elif result == -1:
            self.player1.feedReward(0)
            self.player2.feedReward(1)
        else:
            self.player1.feedReward(0.1)
            self.player2.feedReward(0.5)

    # insert the token and change the player symbol
    def updateState(self, row, column):
        self.board[row][column] = self.player_symbol
        # switch to another player
        self.player_symbol = -1 if self.player_symbol == 1 else 1

    # let the program play against it self and learn
    def play(self, rounds=1000000):
        for i in range(rounds):
            if i % 50000 == 0:
                print("Rounds {}".format(i))
                outfile1 = open('p1', 'wb')
                outfile2 = open('p2', 'wb')
                pickle.dump(self.player1.states_value, outfile1)
                pickle.dump(self.player2.states_value, outfile2)
                outfile1.close()
                outfile2.close()
                print(str((time.time() - begin)/60) + ' minutes')
            while not self.isEnd:
                # Player 1
                positions = self.available_moves()
                p1_action = self.player1.choose_move(positions, self.board, self.player_symbol)
                # take action and update board state
                self.updateState(p1_action[0], p1_action[1])
                board_hash = self.getHash()
                board_hash2 = self.get_flip_hash()
                self.player1.addState(board_hash)
                self.player1.addState(board_hash2)
                # check board status if it is end
                win = self.winner()
                if win is not None:
                    # self.showBoard()
                    # ended with p1 either win or draw
                    self.giveReward()
                    self.player1.reset()
                    self.player2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.available_moves()
                    p2_action = self.player2.choose_move(positions, self.board, self.player_symbol)
                    self.updateState(p2_action[0], p2_action[1])
                    board_hash = self.getHash()
                    board_hash2 = self.get_flip_hash()
                    self.player2.addState(board_hash)
                    self.player2.addState(board_hash2)
                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.player1.reset()
                        self.player2.reset()
                        self.reset()
                        break
        outfile1 = open('p1', 'wb')
        outfile2 = open('p2', 'wb')
        pickle.dump(self.player1.states_value, outfile1)
        pickle.dump(self.player2.states_value, outfile2)
        outfile1.close()
        outfile2.close()

    # play against a human
    def play_human(self):
        print(self.board)
        while not self.isEnd:
            # Player 1
            positions = self.available_moves()
            print('Moves: ', positions)
            choice = int(input('Choose a move:'))
            # take action and update board state
            self.updateState(self.find_slot(choice), choice)
            board_hash = self.getHash()
            self.player1.addState(board_hash)
            print(self.board)
            # check board status if it is end

            win = self.winner()
            if win is not None:
                # self.showBoard()
                # ended with p1 either win or draw
                print('Winner is:', self.player_symbol)
                self.giveReward()
                self.player1.reset()
                self.player2.reset()
                self.reset()
                break

            else:
                # Player 2
                positions = self.available_moves()
                p2_action = self.player2.choose_move(positions, self.board, self.player_symbol)
                self.updateState(p2_action[0], p2_action[1])
                board_hash = self.getHash()
                self.player2.addState(board_hash)
                print("Computer inserts chip into column {} which lands on row {}".format(p2_action[1], p2_action[0]))
                print(self.board)

                win = self.winner()
                if win is not None:
                    # self.showBoard()
                    # ended with p2 either win or draw
                    print('Winner is:', self.player_symbol)
                    self.giveReward()
                    self.player1.reset()
                    self.player2.reset()
                    self.reset()
                    break

# th player class holds the previous games decision making dictionary and the various learning rates
class Player:
    def __init__(self, name, states_value, exp_rate=0.3):
        self.states = []  # a running list of board positions from this particular game
        self.exp_rate = exp_rate  # the rate at which a random move will be chosen
        self.states_value = states_value  # a dictionary of board positions and their values
        self.name = name
        self.learn_rate = 0.2  # 0 is learn nothing new, 1 is only consider new information
        self.discount_factor = 0.9  # 0 is myopic, 1 is long term accuracy

    # get a hash of the current board position
    def getHash(self, board):
        boardHash = str(board.reshape(7 * 6))
        return boardHash

    # finds the slt for a certain column
    def find_slot(self, column, board):
        slot = 0
        for i in range(6):
            if board[i][column] != 0:
                break
            slot = i
        return slot

    # add the board state to the list of states
    def addState(self, state):
        self.states.append(state)

    # resets the states list
    def reset(self):
        self.states = []

    # decide on which move to play
    def choose_move(self, moves, board, player_symbol):
        value_max = -999
        for p in moves:
            next_board = board.copy()
            slot = self.find_slot(p, next_board)
            next_board[slot][p] = player_symbol
            next_boardHash = self.getHash(next_board)
            value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
            if self.winner(next_board) == player_symbol:
                self.states_value[self.get_flip_hash(next_board)] = 999
                move = p
                slot = self.find_slot(move, board)
                return slot, move
            if value >= value_max:
                value_max = value
                move = p
        # Make a random move some of the time
        if np.random.uniform(0, 1) <= self.exp_rate:
            i = np.random.choice(len(moves))
            move = moves[i]
        # find the row (slot)
        slot = self.find_slot(move, board)
        return slot, move

    #  find all available columns
    def available_moves(self, board):
        # Just check the top row to see if there's space
        moves = []
        for i in range(7):
            if board[0][i] == 0:
                moves.append(i)
        return moves

    def engine_choose_move(self, moves, board, player_symbol):
        moves_list = moves.copy()
        for p in moves:
            next_board = board.copy()
            slot = self.find_slot(p, next_board)
            next_board[slot][p] = player_symbol
            if self.winner(next_board) == player_symbol:
                move = p
                slot = self.find_slot(move, board)
                return slot, move
            opponent_moves = self.available_moves(next_board)
            for q in opponent_moves:
                # print('2 move ahead')
                opponent_board = next_board.copy()
                q_slot = self.find_slot(q, opponent_board)
                opponent_board[q_slot][q] = player_symbol * -1
                if self.winner(opponent_board) == player_symbol * -1:
                    moves_list.remove(p)
                    break
                win_in_2 = 0
                lose_boolean1 = True
                my_moves = self.available_moves(opponent_board)
                for r in my_moves:
                    # print('3 move ahead')
                    my_board = opponent_board.copy()
                    r_slot = self.find_slot(r, opponent_board)
                    my_board[r_slot][r] = player_symbol
                    if self.winner(next_board) == player_symbol:
                        win_in_2 += 1
                        continue
                    final_moves = self.available_moves(my_board)
                    lose_boolean2 = False
                    for s in final_moves:
                        final_board = my_board.copy()
                        s_slot = self.find_slot(s, my_board)
                        final_board[s_slot][s] = player_symbol * -1
                        if self.winner(final_board) == player_symbol * -1:
                            lose_boolean2 = True
                    if not lose_boolean2:
                        lose_boolean1 = False
                if win_in_2 == len(moves):
                    move = p
                    slot = self.find_slot(move, board)
                    return slot, move
                if lose_boolean1:
                    moves_list.remove(p)
                    break
        if len(moves_list) < 1:
            pick = randint(0, len(moves)-1)
            move = moves[pick]
            slot = self.find_slot(move, board)
            return slot, move
        pick = randint(0, len(moves_list)-1)
        move = moves_list[pick]
        slot = self.find_slot(move, board)
        print('last return')
        return slot, move

    # at the end of game, update states value
    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.learn_rate * ((self.discount_factor * reward) - self.states_value[st])
            reward = self.states_value[st]

    def get_flip_hash(self, board):
        list = []
        for row in board:
            list.append(np.flip(row))
        board = np.array(list)
        boardHash = str(board.reshape(7 * 6))
        return boardHash

    # determine if the current game has ended
    def winner(self, board):
        # check rows
        for row in range(6):
            # must make 4 checks to cover the whole row
            for i in range(4):
                if sum(board[row][0+i:4+i]) == 4:
                    return 1
                elif sum(board[row][0+i:4+i]) == -4:
                    return -1
        # check columns
        for column in range(7):
            # must make 3 checks to cover the whole column
            for i in range(3):
                if sum(board.T[column][0+i:4+i]) == 4:
                    return 1
                if sum(board.T[column][0+i:4+i]) == -4:
                    return -1
        # check diagonals
        # first diagonal (bottom left to top right)
        for column in range(3, 7):
            for row in range(3, 6):
                total = 0
                # add up the 4 diagonals
                for i in range(4):
                    total += board[row-i][column-i]
                if total == 4:
                    return 1
                if total == -4:
                    return -1
        # second diagonal (bottom right to top left)
        for column in range(3, 7):
            for row in range(0, 3):
                total = 0
                # add up the 4 diagonals
                for i in range(4):
                    total += board[row+i][column-i]
                if total == 4:
                    isEnd = True
                    return 1
                if total == -4:
                    isEnd = True
                    return -1

        # Otherwise return nothing
        return None



begin = time.time()
# open the first dictionary
infile1 = open('p1', 'rb')
player1_dic = pickle.load(infile1)
infile1.close()
# open second dictionary
infile2 = open('p2', 'rb')
player2_dic = pickle.load(infile2)
infile2.close()

p1 = Player('Jo', player1_dic, 0.5)
p2 = Player('Dave', player2_dic, 0.5)

Connect4_game = State(p1, p2)

Connect4_game.play()

