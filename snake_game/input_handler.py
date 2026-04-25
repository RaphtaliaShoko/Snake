"""Input handling module for keyboard and gamepad support."""

import time
from typing import Optional, Callable, Dict, List, Tuple
import pygame

from .constants import Direction


class InputHandler:
    """
    Handles all input processing including keyboard and gamepad.
    """

    def __init__(self):
        self._joystick: Optional[pygame.joystick.Joystick] = None
        self._gamepad_available = False
        self._last_direction_time = 0.0
        self._direction_cooldown = 0.1

        self._key_bindings: Dict[int, Callable] = {}
        self._action_bindings: Dict[str, Callable] = {}

        self._gamepad_deadzone = 0.3
        self._gamepad_calibration = (0, 0)
        self._last_dpad_time = 0.0
        self._dpad_cooldown = 0.15

        self._action_queue: List[str] = []
        self._direction_queue: List[Direction] = []

        self._initialize_gamepad()

    def _initialize_gamepad(self) -> None:
        """Initialize gamepad if available."""
        try:
            if pygame.joystick.get_count() > 0:
                self._joystick = pygame.joystick.Joystick(0)
                self._joystick.init()
                self._gamepad_available = True
                print(f"Gamepad connected: {self._joystick.get_name()}")
        except pygame.error:
            self._gamepad_available = False

    def has_gamepad(self) -> bool:
        """Check if a gamepad is available."""
        return self._gamepad_available

    def is_gamepad_enabled(self) -> bool:
        """Check if gamepad input should be processed."""
        return self._gamepad_available

    def set_deadzone(self, deadzone: float) -> None:
        """Set the gamepad analog stick deadzone."""
        self._gamepad_deadzone = max(0.0, min(0.5, deadzone))

    def calibrate_gamepad(self) -> None:
        """Calibrate gamepad to account for drift."""
        if not self._gamepad_available or self._joystick is None:
            return

        samples = []
        for _ in range(10):
            time.sleep(0.05)
            x = self._joystick.get_axis(0)
            y = self._joystick.get_axis(1)
            samples.append((x, y))

        avg_x = sum(s[0] for s in samples) / len(samples)
        avg_y = sum(s[1] for s in samples) / len(samples)
        self._gamepad_calibration = (avg_x, avg_y)

    def process_event(self, event: pygame.event.Event) -> None:
        """Process a single pygame event."""
        if event.type == pygame.JOYBUTTONDOWN:
            self._process_gamepad_button(event.button)
        elif event.type == pygame.JOYAXISMOTION:
            self._process_gamepad_axis(event.axis, event.value)
        elif event.type == pygame.JOYHATMOTION:
            self._process_gamepad_dpad(event.value)

    def _process_gamepad_button(self, button: int) -> None:
        """Process gamepad button press."""
        button_actions = {
            0: "start",
            1: "select",
            2: "action",
            3: "pause",
            4: "up",
            5: "down",
        }

        if button in button_actions:
            action = button_actions[button]
            if action in self._action_bindings:
                self._action_bindings[action]()

    def _process_gamepad_axis(self, axis: int, value: float) -> None:
        """Process gamepad analog stick movement."""
        if axis not in (0, 1):
            return

        calib_x, calib_y = self._gamepad_calibration
        if axis == 0:
            value -= calib_x
        elif axis == 1:
            value -= calib_y

        if abs(value) < self._gamepad_deadzone:
            return

        current_time = time.time()
        if current_time - self._last_dpad_time < self._dpad_cooldown:
            return

        self._last_dpad_time = current_time

        if axis == 0:
            if value > 0:
                self.queue_direction(Direction.RIGHT)
            else:
                self.queue_direction(Direction.LEFT)
        elif axis == 1:
            if value > 0:
                self.queue_direction(Direction.DOWN)
            else:
                self.queue_direction(Direction.UP)

    def _process_gamepad_dpad(self, value: Tuple[int, int]) -> None:
        """Process gamepad D-pad input."""
        dx, dy = value
        if dx == 0 and dy == 0:
            return

        current_time = time.time()
        if current_time - self._last_dpad_time < self._dpad_cooldown:
            return

        self._last_dpad_time = current_time

        if dy < 0:
            self.queue_direction(Direction.UP)
        elif dy > 0:
            self.queue_direction(Direction.DOWN)

        if dx < 0:
            self.queue_direction(Direction.LEFT)
        elif dx > 0:
            self.queue_direction(Direction.RIGHT)

    def register_action(self, action: str, callback: Callable) -> None:
        """Register an action callback."""
        self._action_bindings[action] = callback

    def queue_direction(self, direction: Direction) -> None:
        """Queue a direction change."""
        if len(self._direction_queue) < 2:
            self._direction_queue.append(direction)

    def queue_action(self, action: str) -> None:
        """Queue an action."""
        if len(self._action_queue) < 3:
            self._action_queue.append(action)

    def get_next_direction(self) -> Optional[Direction]:
        """Get the next queued direction."""
        if self._direction_queue:
            return self._direction_queue.pop(0)
        return None

    def get_next_action(self) -> Optional[str]:
        """Get the next queued action."""
        if self._action_queue:
            return self._action_queue.pop(0)
        return None

    def process_keyboard(self, event: pygame.event.Event) -> Optional[Direction]:
        """
        Process keyboard input for direction changes.

        Returns:
            Direction if a direction key was pressed, None otherwise
        """
        if event.type != pygame.KEYDOWN:
            return None

        key_map = {
            pygame.K_UP: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_w: Direction.UP,
            pygame.K_s: Direction.DOWN,
            pygame.K_a: Direction.LEFT,
            pygame.K_d: Direction.RIGHT,
            pygame.K_KP8: Direction.UP,
            pygame.K_KP2: Direction.DOWN,
            pygame.K_KP4: Direction.LEFT,
            pygame.K_KP6: Direction.RIGHT,
        }

        return key_map.get(event.key)

    def is_quit_key(self, event: pygame.event.Event) -> bool:
        """Check if event is a quit key."""
        return event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        )

    def clear_queues(self) -> None:
        """Clear all input queues."""
        self._direction_queue = []
        self._action_queue = []