from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
import random

class Card(Button):
    """A single card in the memory game."""
    def __init__(self, front_image: str, card_id: str):
        super().__init__()
        # Static assets
        self.back_image = "card.png"           # image when the card is face‑down
        self.front_image = front_image         # image when the card is face‑up
        self.card_id = card_id                 # unique id used for matching logic

        # Kivy visual configuration
        self.background_normal = self.back_image
        self.size_hint = (None, None)
        self.size = (150, 200)

        # Card state
        self.is_open = False

    def on_press(self):
        """
        Flip the card if fewer than two cards are currently open.
        """
        board = self.parent

        # Do not allow more than two cards open
        if board.open_counter >= 2:
            return

        # Ignore a second click on the same card
        if board.first_card_id == self.card_id:
            return

        # Reveal this card
        self.background_normal = self.front_image
        self.is_open = True
        board.register_flip(self.card_id, self)


class Board(FloatLayout):
    """
    The game board that manages all state and interactions.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # State related to the two currently flipped cards
        self.first_card_id = None
        self.second_card_id = None
        self.first_widget = None
        self.second_widget = None

        # Counters
        self.open_counter = 0          # number of cards currently open (0‑2)
        self.pair_counter = 0          # number of matched pairs found
        self.attempt_counter = 0       # number of attempts made

        # Card objects
        self.cards = []
        self._init_cards()
        random.shuffle(self.cards)
        self._layout_cards()

        # UI widgets
        self.check_button = Button(text="Check Pair",
                                   size_hint=(None, None),
                                   size=(150, 150),
                                   pos=(700, 300))
        self.check_button.bind(on_press=self._check_pair)
        self.add_widget(self.check_button)

        self.message = Label(text="Attempts: 0",
                             pos=(700, 500))
        self.add_widget(self.message)

        self.win_message = Label(pos=(350, 300))
        self.add_widget(self.win_message)

    # ------------------------------------------------------------------ #
    # Helper methods
    # ------------------------------------------------------------------ #
    def register_flip(self, card_id: str, widget):
        """
        Called by a `Card` after it is flipped.
        """
        self.open_counter += 1

        if self.open_counter == 1:
            self.first_card_id = card_id
            self.first_widget = widget
        elif self.open_counter == 2:
            self.second_card_id = card_id
            self.second_widget = widget
            self.attempt_counter += 1
            self.message.text = f"Attempts: {self.attempt_counter}"

    def _check_pair(self, *_):
        """
        Handle “Check Pair” button press.
        """
        if self.open_counter < 2:
            return  # need two open cards to compare

        # Matching rule: first digit of one id equals last digit of the other
        is_match = (self.first_card_id[0] == self.second_card_id[-1] or
                    self.first_card_id[-1] == self.second_card_id[0])

        if is_match:
            # Remove matched cards
            self.remove_widget(self.first_widget)
            self.remove_widget(self.second_widget)
            self.pair_counter += 1
        else:
            # Flip both cards face‑down again
            for widget in (self.first_widget, self.second_widget):
                widget.background_normal = widget.back_image
                widget.is_open = False

        # Reset state for next turn
        self.first_card_id = self.second_card_id = None
        self.first_widget = self.second_widget = None
        self.open_counter = 0

        # Check win condition
        if self.pair_counter == 6:
            self.remove_widget(self.check_button)
            self.win_message.text = "WELL DONE! GAME OVER"

    # ---------------------- card setup ---------------------- #
    def _init_cards(self):
        """
        Create 12 Card objects (6 pairs) and store them in `self.cards`.
        """
        images = [
            "mask.png",
            "alcogel.png",
            "corona.png",
            "china.png",
            "hands.png",
            "distance.png",
        ]
        # Each image appears twice -> 6 pairs
        for idx, img in enumerate(images, start=1):
            self.cards.append(Card(img, str(idx)))
            self.cards.append(Card(img, str(idx + 90)))  # matching variant

    def _layout_cards(self):
        """
        Place shuffled cards on the board in a 3 × 4 grid.
        """
        x, y = 60, 40
        for i, card in enumerate(self.cards):
            card.pos = (x, y)
            self.add_widget(card)

            x += 150
            if (i + 1) % 4 == 0:
                y += 200
                x = 60


class MemoryGameApp(App):
    """
    Kivy App wrapper.
    """
    def build(self):
        return Board()


if __name__ == "__main__":
    MemoryGameApp().run()
