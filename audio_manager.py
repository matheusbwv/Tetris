import pygame
import os

class AudioManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.music_tracks = {}
        self.music_volume = 0.5
        self.effects_volume = 0.7
        self.current_track = None
        self.music_paused = False
    
    def load_sound(self, name, path):
        """Carrega um efeito sonoro verificando se o arquivo existe"""
        try:
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(self.effects_volume)
            else:
                print(f"Warning: Sound file not found at {path}")
        except Exception as e:
            print(f"Error loading sound {name}: {str(e)}")
    
    def play_sound(self, name):
        """Toca um efeito sonoro se existir"""
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"Error playing sound {name}: {str(e)}")
        else:
            print(f"Warning: Sound {name} not loaded")
    
    def add_music(self, name, path):
        """Adiciona uma trilha sonora verificando se o arquivo existe"""
        if os.path.exists(path):
            self.music_tracks[name] = path
        else:
            print(f"Warning: Music file not found at {path}")
    
    def play_music(self, track_name, loops=-1, fade_ms=0):
        """Toca uma música específica com opção de fade in"""
        if track_name in self.music_tracks:
            if track_name != self.current_track or not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.load(self.music_tracks[track_name])
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
                    self.current_track = track_name
                    self.music_paused = False
                except Exception as e:
                    print(f"Error playing music {track_name}: {str(e)}")
        else:
            print(f"Warning: Music track {track_name} not loaded")
    
    def stop_music(self, fade_ms=0):
        """Para a música atual com opção de fade out"""
        try:
            pygame.mixer.music.fadeout(fade_ms)
            self.current_track = None
            self.music_paused = False
        except Exception as e:
            print(f"Error stopping music: {str(e)}")
    
    def pause_music(self):
        """Pausa a música atual"""
        if pygame.mixer.music.get_busy() and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True
    
    def unpause_music(self):
        """Despausa a música atual"""
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
    
    def set_music_volume(self, volume):
        """Ajusta o volume da música com validação"""
        self.music_volume = max(0.0, min(1.0, float(volume)))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_effects_volume(self, volume):
        """Ajusta o volume dos efeitos com validação"""
        self.effects_volume = max(0.0, min(1.0, float(volume)))
        for sound in self.sounds.values():
            sound.set_volume(self.effects_volume)
    
    def toggle_music_pause(self):
        """Alterna entre pausar e despausar a música"""
        if self.music_paused:
            self.unpause_music()
        else:
            self.pause_music()
    
    def is_music_playing(self):
        """Verifica se a música está tocando (não pausada)"""
        return pygame.mixer.music.get_busy() and not self.music_paused