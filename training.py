import numpy as np

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
            if i % 10000 == 0:
                print("Rounds {}".format(i))
                np.save('p1.npy', self.player1.states_value)
                np.save('p2.npy', self.player2.states_value)
            while not self.isEnd:
                # Player 1
                positions = self.available_moves()
                p1_action = self.player1.choose_move(positions, self.board, self.player_symbol)
                # take action and update board state
                self.updateState(p1_action[0], p1_action[1])
                board_hash = self.getHash()
                self.player1.addState(board_hash)
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
                    self.player2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.player1.reset()
                        self.player2.reset()
                        self.reset()
                        break
        np.save('p1.npy', self.player1.states_value)
        np.save('p2.npy', self.player2.states_value)

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
        # Make a random move some of the time
        if np.random.uniform(0, 1) <= self.exp_rate:
            i = np.random.choice(len(moves))
            move = moves[i]

        else:
            value_max = -999
            for p in moves:
                next_board = board.copy()
                slot = self.find_slot(p, next_board)
                next_board[slot][p] = player_symbol
                next_boardHash = self.getHash(next_board)
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash)
                if value >= value_max:
                    value_max = value
                    move = p
                # find the row (slot)
        slot = self.find_slot(move, board)
        return slot, move

    # at the end of game, update states value
    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_value.get(st) is None:
                self.states_value[st] = 0
            self.states_value[st] += self.learn_rate * ((self.discount_factor * reward) - self.states_value[st])
            reward = self.states_value[st]


player1_dic = np.load('p1.npy', allow_pickle=True).item()
player2_dic = np.load('p2.npy', allow_pickle=True).item()
p1 = Player('Jo', player1_dic, 0.3)
p2 = Player('Dave', player2_dic, 0.3)
Connect4_game = State(p1, p2)

Connect4_game.play()

