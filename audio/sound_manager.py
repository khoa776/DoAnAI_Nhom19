import os

import pygame


MUSIC_FILE = "serhii_kliets-spaceship-arcade-shooter-game-background-soundtrack-318508.mp3"


def play_music():
    root_folder = os.path.dirname(os.path.dirname(__file__))
    music_path = os.path.join(root_folder, MUSIC_FILE)

    if not os.path.exists(music_path):
        print("Khong tim thay file nhac nen.")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.28)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Khong mo duoc nhac nen.")
