import sys
import random
from functools import partial

import numpy as np

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLabel, QSlider
from PySide6.QtCore import Qt

LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonal, anti-diagonal
)

P1 = 3  # value marking player one's squares on the board
P2 = 5  # value marking player two's squares on the board

def _check_game_state(board):
    sums = np.concatenate((
        board.sum(axis=1),                                
        board.sum(axis=0),                                
        [np.trace(board), np.trace(np.fliplr(board))], 
    ))
    return sums

def _check_winner(sums):
    if 9 in sums:
        return 'P1'
    if 15 in sums:
        return 'P2'
    return 'ongoing'


class Bot:
    def __init__(self, difficulty, player_number):
        self.difficulty = difficulty
        if player_number == P1:
            self.opp_number = P2
        else:
            self.opp_number = P1

    def calc_next_move(self, sums, open_fields):

        random_move = random.randint(1,99)
        random_move2 = random.randint(1,99)
        # if random_move > self.difficulty:
        #     return random.choice(open_fields)
        
        play_spot = self.check_lose(sums, open_fields)
        if play_spot is not None:
            if random_move >= self.difficulty and random_move2 > self.difficulty:
                return random.choice(open_fields)
            else:
                return play_spot
        return random.choice(open_fields)   

    def check_lose(self, sums, open_fields):
        problem_line = np.flatnonzero(sums == 2*self.opp_number)
        if len(problem_line) == 1:
            print(problem_line)
            print(type(problem_line))
            problem_spots = LINES[problem_line[0]]
            problem_square = [s for s in problem_spots if s in open_fields]
            return problem_square[0]
        else: return None
        
        
         
            


class TTTBotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.create_gui()

        # init variables
        self.current_difficulty = 0

        self._init_game_state()
        



    def create_gui(self):
        self.setWindowTitle('TTT Bot')
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_vertical_layout = QVBoxLayout(self.main_widget)

        # frame to hold the interaction with the system: 
        # start and reset, player order and difficulty slider
        top_bar_frame = QFrame()
        top_bar_layout = QHBoxLayout(top_bar_frame)
        self.start_reset_button = QPushButton('Reset')
        self.start_reset_button.clicked.connect(self.start_reset_click)
        slider_frame = QFrame()
        slider_frame_layout = QVBoxLayout(slider_frame)
        self.difficulty_slider = QSlider()
        self.difficulty_label = QLabel('0')
        slider_frame_layout.addWidget(self.difficulty_slider)
        self.difficulty_slider.setRange(1,100)
        slider_frame_layout.addWidget(self.difficulty_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.difficulty_slider.setOrientation(Qt.Orientation.Horizontal)
        self.difficulty_slider.valueChanged.connect(self.slider_value_changed)
        self.play_order_button = QPushButton('Going First')
        self.play_order_button.setEnabled(False)
        #add to frame
        top_bar_layout.addWidget(self.start_reset_button)
        top_bar_layout.addWidget(slider_frame)
        top_bar_layout.addWidget(self.play_order_button)

        #main play area
        main_area_frame = QFrame()
        main_area_layout = QGridLayout(main_area_frame)
        self.main_buttons = []
        for i in range(9):
            row, col = divmod(i, 3)
            btn = QPushButton(str(''))
            btn.clicked.connect(partial(self.main_button_click, i))
            main_area_layout.addWidget(btn, row, col)
            self.main_buttons.append(btn)

        #staus label at the bottom
        self.bottom_label = QLabel('')

        #add all to the main layout
        main_vertical_layout.addWidget(top_bar_frame)
        main_vertical_layout.addWidget(main_area_frame)
        main_vertical_layout.addWidget(self.bottom_label)



    def main_button_click(self, button_number):
        
        clicked_field = divmod(button_number, 3)
        self.open_fields.remove(button_number)
        self.game_board[clicked_field] = self.board_number
        self.main_buttons[button_number].setText(self.play_label)
        sums = _check_game_state(self.game_board)
        self.game_state = _check_winner(sums)
        if self.game_state == 'P1' or self.game_state == 'P2' or len(self.open_fields) == 0:
            for button in self.main_buttons:
                button.setEnabled(False)
            if self.game_state == 'P1':
                self.bottom_label.setText('Player 1 Wins')
            elif self.game_state == 'P2':
                self.bottom_label.setText('Player 2 Wins')
            elif len(self.open_fields) == 0:
                self.game_state = 'Draw'
                self.bottom_label.setText('Draw')   
        if self.game_state == 'ongoing':
            self._turn_tracker()
        

    def slider_value_changed(self):
        self.current_difficulty = self.difficulty_slider.value()
        self.difficulty_label.setText(str(self.current_difficulty))

    def start_reset_click(self):
        self._init_game_state()
        

    def _init_game_state(self):
        self.generate_bot()
        self.game_state = 'ongoing'
        self.turn_number = 0
        self.game_board = np.zeros((3,3), dtype=int)
        self.open_fields = list(range(9))
        self.play_label = 'X'
        self.board_number = P1
        for button in self.main_buttons:
            button.setText('')
            button.setEnabled(True)
        self._turn_tracker()

    def _turn_tracker(self):

        self.turn_number += 1
        if self.turn_number % 2 == 1:
            self.player = 'P1'
            self.play_label = 'X'
            self.board_number = P1
            #self.bot_to_play()
        else:
            self.player = 'P2'
            self.play_label = 'O'
            self.board_number = P2
            #self.bot_to_play()
    
    #def who_to_play(self):

    def bot_to_play(self):
        clicked = self.bot_turn()

        self.main_button_click(clicked)

    def generate_bot(self):
        difficulty = self.difficulty_slider.value()
        self.bot = Bot(difficulty, P2)

    def bot_turn(self):
        sums = _check_game_state(board=self.game_board)

        return self.bot.calc_next_move(sums, self.open_fields)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TTTBotWindow()
    window.show()
    sys.exit(app.exec())