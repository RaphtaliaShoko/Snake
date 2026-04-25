"""Audio module for game sounds and music."""

import math
import random
from typing import Optional
import pygame
import numpy as np

from .theme import GameTheme


class ProceduralAudio:
    """
    Generates game audio procedurally without external files.
    Uses simple waveform synthesis for sounds.
    """

    def __init__(self):
        self._sample_rate = 44100
        self._eat_sound: Optional[pygame.mixer.Sound] = None
        self._death_sound: Optional[pygame.mixer.Sound] = None
        self._menu_sound: Optional[pygame.mixer.Sound] = None
        self._bonus_sound: Optional[pygame.mixer.Sound] = None
        self._initialized = False
        self._music_playing = False
        self._current_theme: Optional[GameTheme] = None

    def initialize(self, theme: GameTheme) -> None:
        """Initialize audio system with theme settings."""
        if self._initialized:
            return

        try:
            pygame.mixer.init(frequency=self._sample_rate)
            self._create_sounds(theme)
            self._initialized = True
        except pygame.error as e:
            print(f"Warning: Audio initialization failed: {e}")

    def _create_sounds(self, theme: GameTheme) -> None:
        """Create all game sounds."""
        tempo = theme.sounds.music_tempo
        eat_pitch = theme.sounds.eat_pitch
        death_pitch = theme.sounds.death_pitch

        self._eat_sound = self._generate_eat_sound(eat_pitch)
        self._bonus_sound = self._generate_bonus_sound(eat_pitch)
        self._death_sound = self._generate_death_sound(death_pitch)
        self._menu_sound = self._generate_menu_sound()

    def _generate_eat_sound(self, pitch: float = 1.0) -> pygame.mixer.Sound:
        """Generate a short, pleasant eat sound."""
        duration = 0.1
        samples = int(self._sample_rate * duration)

        t = np.linspace(0, duration, samples)
        freq1 = 440 * pitch
        freq2 = 880 * pitch

        wave1 = np.sin(2 * np.pi * freq1 * t) * 0.5
        wave2 = np.sin(2 * np.pi * freq2 * t) * 0.3

        envelope = np.exp(-t * 20)

        audio = (wave1 + wave2) * envelope
        audio = (audio * 32767 * 0.3).astype(np.int16)

        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _generate_bonus_sound(self, pitch: float = 1.0) -> pygame.mixer.Sound:
        """Generate a rewarding bonus sound."""
        duration = 0.2
        samples = int(self._sample_rate * duration)

        t = np.linspace(0, duration, samples)
        frequencies = [523 * pitch, 659 * pitch, 784 * pitch]

        audio = np.zeros(samples)
        for i, freq in enumerate(frequencies):
            offset = i * 0.05
            local_t = np.maximum(0, t - offset)
            wave = np.sin(2 * np.pi * freq * local_t)
            envelope = np.exp(-local_t * 10)
            audio += wave * envelope

        audio = (audio / len(frequencies)) * 0.4
        envelope = np.exp(-t * 5)
        audio = audio * envelope
        audio = (audio * 32767 * 0.3).astype(np.int16)

        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _generate_death_sound(self, pitch: float = 1.0) -> pygame.mixer.Sound:
        """Generate a descending death sound."""
        duration = 0.4
        samples = int(self._sample_rate * duration)

        t = np.linspace(0, duration, samples)
        freq_start = 400 * pitch
        freq_end = 100 * pitch

        freq = freq_start + (freq_end - freq_start) * (t / duration)
        wave = np.sin(2 * np.pi * freq * t)

        noise = np.random.uniform(-0.2, 0.2, samples)
        audio = wave * 0.7 + noise * 0.3

        envelope = np.exp(-t * 4)
        audio = audio * envelope
        audio = (audio * 32767 * 0.3).astype(np.int16)

        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _generate_menu_sound(self) -> pygame.mixer.Sound:
        """Generate a menu navigation sound."""
        duration = 0.05
        samples = int(self._sample_rate * duration)

        t = np.linspace(0, duration, samples)
        freq = 800

        wave = np.sin(2 * np.pi * freq * t)
        envelope = np.exp(-t * 30)
        audio = wave * envelope
        audio = (audio * 32767 * 0.2).astype(np.int16)

        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _generate_music_segment(self, duration: float = 2.0) -> pygame.mixer.Sound:
        """Generate a procedural background music segment."""
        samples = int(self._sample_rate * duration)

        t = np.linspace(0, duration, samples)

        base_freq = 110
        bass = np.sin(2 * np.pi * base_freq * t) * 0.15

        melody_freqs = [220, 330, 440, 330, 220, 330, 440, 550]
        melody = np.zeros(samples)
        beat_duration = duration / len(melody_freqs)
        for i, freq in enumerate(melody_freqs):
            start = int(i * beat_duration * self._sample_rate)
            end = int((i + 1) * beat_duration * self._sample_rate)
            if end > samples:
                end = samples
            local_t = np.linspace(0, beat_duration, end - start)
            note = np.sin(2 * np.pi * freq * local_t)
            envelope = np.exp(-local_t * 5)
            melody[start:end] += note * envelope * 0.1

        harmonics = np.sin(2 * np.pi * 55 * t) * 0.05
        for h in range(2, 5):
            harmonics += np.sin(2 * np.pi * 55 * h * t) * (0.05 / h)

        audio = bass + melody + harmonics

        audio = np.clip(audio, -0.9, 0.9)

        audio = (audio * 32767 * 0.3).astype(np.int16)
        stereo = np.column_stack((audio, audio))

        return pygame.sndarray.make_sound(stereo)

    def play_eat(self, volume: float = 1.0) -> None:
        """Play the eat sound effect."""
        if self._eat_sound:
            self._eat_sound.set_volume(volume)
            self._eat_sound.play()

    def play_bonus(self, volume: float = 1.0) -> None:
        """Play the bonus sound effect."""
        if self._bonus_sound:
            self._bonus_sound.set_volume(volume)
            self._bonus_sound.play()

    def play_death(self, volume: float = 1.0) -> None:
        """Play the death sound effect."""
        if self._death_sound:
            self._death_sound.set_volume(volume)
            self._death_sound.play()

    def play_menu(self, volume: float = 1.0) -> None:
        """Play the menu navigation sound."""
        if self._menu_sound:
            self._menu_sound.set_volume(volume)
            self._menu_sound.play()

    def start_music(self, volume: float = 0.5) -> None:
        """Start background music loop."""
        if not self._initialized or self._music_playing:
            return

        try:
            music_segment = self._generate_music_segment(4.0)
            music_segment.set_volume(volume * 0.5)
            music_segment.play(loops=-1)
            self._music_playing = True
        except Exception as e:
            print(f"Warning: Could not start music: {e}")

    def stop_music(self) -> None:
        """Stop background music."""
        if self._music_playing:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            self._music_playing = False

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        try:
            pygame.mixer.music.set_volume(volume)
        except:
            pass

    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume (0.0 to 1.0)."""
        pass

    def cleanup(self) -> None:
        """Clean up audio resources."""
        self.stop_music()
        if self._initialized:
            try:
                pygame.mixer.quit()
            except:
                pass
            self._initialized = False


class AudioManager:
    """Manages audio playback and theme changes."""

    def __init__(self):
        self._audio = ProceduralAudio()
        self._music_volume = 0.5
        self._sfx_volume = 0.7
        self._initialized = False

    def initialize(self, theme: GameTheme) -> None:
        """Initialize audio with theme."""
        self._audio.initialize(theme)
        self._initialized = True

    def play_eat(self) -> None:
        """Play eat sound."""
        self._audio.play_eat(self._sfx_volume)

    def play_bonus(self) -> None:
        """Play bonus sound."""
        self._audio.play_bonus(self._sfx_volume)

    def play_death(self) -> None:
        """Play death sound."""
        self._audio.play_death(self._sfx_volume)

    def play_menu_select(self) -> None:
        """Play menu selection sound."""
        self._audio.play_menu(self._sfx_volume)

    def start_music(self) -> None:
        """Start background music."""
        if self._initialized:
            self._audio.start_music(self._music_volume)

    def stop_music(self) -> None:
        """Stop background music."""
        self._audio.stop_music()

    def set_music_volume(self, volume: float) -> None:
        """Set music volume."""
        self._music_volume = max(0.0, min(1.0, volume))
        self._audio.set_music_volume(self._music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume."""
        self._sfx_volume = max(0.0, min(1.0, volume))

    def cleanup(self) -> None:
        """Clean up resources."""
        self._audio.cleanup()