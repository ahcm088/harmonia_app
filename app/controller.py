
from .models import ChordData
from .utils import get_degree, get_cadence

class HarmonyController:
    def __init__(self):
        self.lyrics = ""
        self.chords = []  # Lista de ChordData

    def add_chord(self, position, chord_str):
        chord = ChordData(chord=chord_str)
        self.chords.append((position, chord))
