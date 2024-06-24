import Reversed_Reversi
import tkinter as tk
import cProfile


def draw_board(canvas, board, cell_size):
    for i in range(len(board)):
        for j in range(len(board[i])):
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            canvas.create_rectangle(x1, y1, x2, y2, fill='#f2c792')

            if board[i][j] == 1:  # White
                canvas.create_oval(x1, y1, x2, y2, fill='white')
            elif board[i][j] == -1:  # Black
                canvas.create_oval(x1, y1, x2, y2, fill='black')


def update_gui(chessboard):
    canvas.delete("all")
    draw_board(canvas, chessboard, cell_size)
    root.update()


def main():
    global root, canvas, cell_size

    AI_1 = Reversed_Reversi.AI(8, 1, 5)
    AI_2 = Reversed_Reversi.AI(8, -1, 5)
    chessboard = [[0 for _ in range(8)] for _ in range(8)]
    chessboard[3][3] = 1
    chessboard[3][4] = -1
    chessboard[4][3] = -1
    chessboard[4][4] = 1
    # chessboard = [[-1, -1, -1, -1, -1, -1, -1, 1], [-1, 1, 1, -1, -1, -1, -1, 1], [-1, 1, 1, -1, -1, 1, -1, -1], [-1, -1, 1, -1, 1, -1, -1, 0], [-1, 1, -1, 1, 1, -1, -1, -1], [-1, -1, 1, 1, 1, 1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1]]

    test_color = -1
    print("Initial chessboard:")
    Reversed_Reversi.ReversiSimulator.print_chessboard(chessboard)
    print()

    # Set up the GUI
    root = tk.Tk()
    root.title("Reversi Game")
    cell_size = 50
    canvas = tk.Canvas(root, width=8 * cell_size, height=8 * cell_size)
    canvas.pack()

    # Position the window to the upper right side of the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 8 * cell_size
    window_height = 8 * cell_size
    x_position = screen_width - window_width - 400  # 20 pixels from the right edge
    y_position = 100  # 20 pixels from the top edge
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Keep the window always on top of other windows
    root.attributes("-topmost", True)

    update_gui(chessboard)

    player = None
    while True:
        status = Reversed_Reversi.ReversiSimulator.check_status(chessboard, test_color)
        if status != Reversed_Reversi.GAME_STATUS_GOING:
            print("Game over!")
            total_sum = sum(sum(row) for row in chessboard)
            if status == Reversed_Reversi.COLOR_BLACK:
                print("Black wins by", abs(total_sum), "pieces!")
            elif status == Reversed_Reversi.COLOR_WHITE:
                print("White wins by", abs(total_sum), "pieces!")
            else:
                print("Tie!")
            break
        if test_color == 1:
            ai = AI_1
            player = "white"
        else:
            ai = AI_2
            player = "black"
        print("AI is thinking for", player)
        ai.go(chessboard)
        if len(ai.candidate_list) == 0:
            print("No move available for", player)
            test_color = -test_color
            continue
        print("AI place a", player, "piece at", ai.candidate_list[-1])
        chessboard = Reversed_Reversi.ReversiSimulator.perform_move(chessboard, test_color, ai.candidate_list[-1])
        test_color = -test_color
        Reversed_Reversi.ReversiSimulator.print_chessboard(chessboard)
        print(chessboard)
        print()
        update_gui(chessboard)

    root.mainloop()


if __name__ == "__main__":
    # main()

    AI_1 = Reversed_Reversi.AI(8, 1, 5)
    AI_2 = Reversed_Reversi.AI(8, -1, 5)
    chessboard = [[0 for _ in range(8)] for _ in range(8)]
    chessboard[3][3] = 1
    chessboard[3][4] = -1
    chessboard[4][3] = -1
    chessboard[4][4] = 1
    # chessboard = [[-1, -1, -1, -1, -1, -1, -1, 1], [-1, 1, 1, -1, -1, -1, -1, 1], [-1, 1, 1, -1, -1, 1, -1, -1], [-1, -1, 1, -1, 1, -1, -1, 0], [-1, 1, -1, 1, 1, -1, -1, -1], [-1, -1, 1, 1, 1, 1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1]]

    test_color = -1
    print("Initial chessboard:")
    Reversed_Reversi.ReversiSimulator.print_chessboard(chessboard)
    print()

    cProfile.run('AI_1.go(chessboard)')