from audio.sound_manager import play_music
from screens.manual_map import Game


if __name__ == "__main__":
    # Tam tat nhac nen. Muon bat lai thi bo dau # o dong duoi.
    play_music()
    Game().run()
