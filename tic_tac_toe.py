class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # 3x3 board
        self.current_player = 'X'  # X starts first

    def print_board(self):
        print("\n")
        for row in [self.board[i*3:(i+1)*3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')
        print("\n")

    def make_move(self, position):
        if self.board[position] == ' ':
            self.board[position] = self.current_player
            if self.check_winner():
                print(f"Player {self.current_player} wins!")
                return True
            if self.check_draw():
                print("It's a draw!")
                return True
            self.switch_player()
        else:
            print("That position is already taken!")
        return False

    def check_winner(self):
        # Check rows
        for row in [self.board[i*3:(i+1)*3] for i in range(3)]:
            if all(cell == self.current_player for cell in row):
                return True

        # Check columns
        for col in range(3):
            if all(self.board[col+i*3] == self.current_player for i in range(3)):
                return True

        # Check diagonals
        if all(self.board[i] == self.current_player for i in [0, 4, 8]):
            return True
        if all(self.board[i] == self.current_player for i in [2, 4, 6]):
            return True

        return False

    def check_draw(self):
        return ' ' not in self.board

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def play(self):
        print("Welcome to Tic Tac Toe!")
        print("Positions are 0-8, left to right, top to bottom:")
        print("0 | 1 | 2")
        print("---------")
        print("3 | 4 | 5")
        print("---------")
        print("6 | 7 | 8\n")

        while True:
            self.print_board()
            try:
                position = int(input(f"Player {self.current_player}'s turn (0-8): "))
                if position < 0 or position > 8:
                    print("Please enter a number between 0 and 8")
                    continue

                if self.make_move(position):
                    self.print_board()
                    if input("Play again? (y/n): ").lower() == 'y':
                        self.__init__()  # Reset game
                    else:
                        break
            except ValueError:
                print("Please enter a valid number!")

if __name__ == "__main__":
    game = TicTacToe()
    game.play()