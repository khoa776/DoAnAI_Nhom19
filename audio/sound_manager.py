import pygame
from resource import resource_path

MUSIC_FILE = "serhii_kliets-spaceship-arcade-shooter-game-background-soundtrack-318508.mp3"

def play_music():
    music_path = resource_path(MUSIC_FILE)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.28)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Khong mo duoc nhac nen.")
