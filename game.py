from enum import Enum
from character import *

class Game:
    def __init__(self) -> None:
        self.turn_index = 0
        self.repeating_turn = False # Unused for now
        self.cycle = 1
        self.queue = []
        self.game_state = GameState.NOT_STARTED
    
    def start(self):
        self.game_state = GameState.PLAYING
        # For testing purpose
        self.userCharas = {'C01': playableData[0]}
        self.enemies = {'E01': enemyData[2]}
        self.queue = ['C01', 'E01']
    


class GameState(Enum):
    NOT_STARTED = 0
    PLAYING = 1
    GAME_OVER = 2