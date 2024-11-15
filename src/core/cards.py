from enum import Enum
from dataclasses import dataclass
from typing import List

class CardType(Enum):
    AGGRESSIVE_X = "aggressive_x"
    AGGRESSIVE_Y = "aggressive_y"
    DEFENSIVE_X = "defensive_x"
    DEFENSIVE_Y = "defensive_y"
    STRATEGIC = "strategic"
    UTILITY = "utility"

@dataclass
class Card:
    id: str
    name: str
    description: str
    code: str
    card_type: CardType
    complexity: int
    frequency: float = 1.0  # Default frequency weight of 1.0

class CardLibrary:
    def __init__(self):
        self.cards = {}
        self._initialize_cards()
        
    def add_card(self, card: Card):
        self.cards[card.id] = card
        
    def get_card(self, card_id: str) -> Card:
        return self.cards.get(card_id)
        
    def get_cards_by_type(self, card_type: CardType) -> List[Card]:
        return [card for card in self.cards.values() if card.card_type == card_type]
        
    def _initialize_cards(self):
        # X-focused cards
        self.add_card(Card(
            id="op_increment_x",
            name="Increment X",
            description="Add 1 to x",
            code="x += 1",
            card_type=CardType.AGGRESSIVE_X,
            complexity=1,
            frequency=5.0
        ))
        
        self.add_card(Card(
            id="op_decrement_x",
            name="Decrement X",
            description="Subtract 1 from x",
            code="x -= 1",
            card_type=CardType.DEFENSIVE_X,
            complexity=1,
            frequency=5.0
        ))
        
        # Y-focused cards
        self.add_card(Card(
            id="op_increment_y",
            name="Increment Y",
            description="Add 1 to y",
            code="y += 1",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=1,
            frequency=5.0
        ))
        
        self.add_card(Card(
            id="op_decrement_y",
            name="Decrement Y",
            description="Subtract 1 from y",
            code="y -= 1",
            card_type=CardType.DEFENSIVE_Y,
            complexity=1,
            frequency=5.0
        ))
        
        self.add_card(Card(
            id="op_double_x",
            name="Double X",
            description="Multiply x by 2",
            code="x *= 2",
            card_type=CardType.AGGRESSIVE_X,
            complexity=2,
            frequency=2.0
        ))
        
        self.add_card(Card(
            id="op_double_y",
            name="Double Y",
            description="Multiply y by 2",
            code="y *= 2",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=2,
            frequency=2.0
        ))
        
        self.add_card(Card(
            id="op_halve_x",
            name="Halve X",
            description="Divide x by 2",
            code="x //= 2",
            card_type=CardType.DEFENSIVE_X,
            complexity=2,
            frequency=2.0
        ))
        
        self.add_card(Card(
            id="op_halve_y",
            name="Halve Y",
            description="Divide y by 2",
            code="y //= 2",
            card_type=CardType.DEFENSIVE_Y,
            complexity=2,
            frequency=2.0
        ))

        # Variable Transfers - Strategic moves
        self.add_card(Card(
            id="transfer_x_to_y",
            name="X to Y",
            description="Set y equal to x",
            code="y = x",
            card_type=CardType.STRATEGIC,
            complexity=1,
            frequency=0.5
        ))
        
        self.add_card(Card(
            id="transfer_y_to_x",
            name="Y to X",
            description="Set x equal to y",
            code="x = y",
            card_type=CardType.STRATEGIC,
            complexity=1,
            frequency=0.5
        ))

        # Z-related operations remain UTILITY type since they're neutral storage
        self.add_card(Card(
            id="transfer_x_to_z",
            name="X to Z",
            description="Set z equal to x",
            code="z = x",
            card_type=CardType.UTILITY,
            complexity=1,
            frequency=0.5
        ))
        
        self.add_card(Card(
            id="transfer_y_to_z",
            name="Y to Z",
            description="Set z equal to y",
            code="z = y",
            card_type=CardType.UTILITY,
            complexity=1,
            frequency=0.5
        ))
        
        self.add_card(Card(
            id="transfer_z_to_x",
            name="Z to X",
            description="Set x equal to z",
            code="z = x",
            card_type=CardType.UTILITY,
            complexity=1,
            frequency=0.5
        ))
        
        self.add_card(Card(
            id="transfer_z_to_y",
            name="Z to Y",
            description="Set y equal to z",
            code="y = z",
            card_type=CardType.UTILITY,
            complexity=1,
            frequency=0.5
        ))

        # Contract manipulation cards remain as UTILITY
        self.add_card(Card(
            id="util_reset_z",
            name="Reset Z",
            description="Reset z to 0",
            code="z = 0",
            card_type=CardType.UTILITY,
            complexity=1,
            frequency=0.5
        ))
        
        self.add_card(Card(
            id="util_pop",
            name="Remove Last Line",
            description="Remove the last line from the contract",
            code="__contract__.pop()",
            card_type=CardType.UTILITY,
            complexity=2,
            frequency=0.5
        ))
        
        self.add_card(Card(
            id="util_clear",
            name="Clear Contract",
            description="Remove all lines from the contract",
            code="__contract__.clear()",
            card_type=CardType.UTILITY,
            complexity=3,
            frequency=0.5
        ))
        
        self.add_card(Card(
            id="util_invert",
            name="Invert Execution",
            description="Reverse the order of contract execution",
            code="__contract__.invert()",
            card_type=CardType.UTILITY,
            complexity=3,
            frequency=0.5
        ))
        
        # self.add_card(Card(
        #     id="util_clean",
        #     name="Clean Contract",
        #     description="Remove inactive lines from the contract",
        #     code="__contract__.clean()",
        #     card_type=CardType.UTILITY,
        #     complexity=2,
        #     frequency=0.5
        # ))
        
        # self.add_card(Card(
        #     id="util_optimize",
        #     name="Optimize Contract",
        #     description="Optimize the execution order",
        #     code="__contract__.optimize()",
        #     card_type=CardType.UTILITY,
        #     complexity=2,
        #     frequency=0.5
        # )) 

    def set_card_frequency(self, card_id: str, frequency: float) -> bool:
        """Set the frequency weight for a specific card"""
        if card_id in self.cards:
            self.cards[card_id].frequency = max(0.0, frequency)  # Ensure non-negative
            return True
        return False

    def set_type_frequency(self, card_type: CardType, frequency: float) -> None:
        """Set the frequency weight for all cards of a specific type"""
        for card in self.cards.values():
            if card.card_type == card_type:
                card.frequency = max(0.0, frequency)
 