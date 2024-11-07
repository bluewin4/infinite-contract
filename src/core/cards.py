from enum import Enum
from dataclasses import dataclass
from typing import List

class CardType(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
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
        # Basic Operations - Categorized based on effect
        self.add_card(Card(
            id="op_increment_x",
            name="Increment X",
            description="Add 1 to x",
            code="x += 1",
            card_type=CardType.AGGRESSIVE,
            complexity=1
        ))
        
        self.add_card(Card(
            id="op_decrement_x",
            name="Decrement X",
            description="Subtract 1 from x",
            code="x -= 1",
            card_type=CardType.DEFENSIVE,
            complexity=1
        ))
        
        self.add_card(Card(
            id="op_double_x",
            name="Double X",
            description="Multiply x by 2",
            code="x *= 2",
            card_type=CardType.AGGRESSIVE,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_halve_x",
            name="Halve X",
            description="Divide x by 2",
            code="x //= 2",
            card_type=CardType.DEFENSIVE,
            complexity=2
        ))
        
        # Variable Transfers - Strategic moves
        self.add_card(Card(
            id="transfer_x_to_y",
            name="X to Y",
            description="Set y equal to x",
            code="y = x",
            card_type=CardType.STRATEGIC,
            complexity=1
        ))
        
        self.add_card(Card(
            id="transfer_y_to_x",
            name="Y to X",
            description="Set x equal to y",
            code="x = y",
            card_type=CardType.STRATEGIC,
            complexity=1
        ))
        
        self.add_card(Card(
            id="transfer_x_to_z",
            name="X to Z",
            description="Set z equal to x",
            code="z = x",
            card_type=CardType.STRATEGIC,
            complexity=1
        ))
        
        self.add_card(Card(
            id="transfer_z_to_x",
            name="Z to X",
            description="Set x equal to z",
            code="x = z",
            card_type=CardType.STRATEGIC,
            complexity=1
        ))
        
        self.add_card(Card(
            id="transfer_z_to_y",
            name="Z to Y",
            description="Set y equal to z",
            code="y = z",
            card_type=CardType.STRATEGIC,
            complexity=1
        ))
        
        # Utility operations
        self.add_card(Card(
            id="util_reset_z",
            name="Reset Z",
            description="Reset z to 0",
            code="z = 0",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        # Contract manipulation cards
        self.add_card(Card(
            id="util_pop",
            name="Remove Last Line",
            description="Remove the last line from the contract",
            code="__contract__.pop()",
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        self.add_card(Card(
            id="util_clear",
            name="Clear Contract",
            description="Remove all lines from the contract",
            code="__contract__.clear()",
            card_type=CardType.UTILITY,
            complexity=3
        ))
        
        self.add_card(Card(
            id="util_invert",
            name="Invert Execution",
            description="Reverse the order of contract execution",
            code="__contract__.invert()",
            card_type=CardType.UTILITY,
            complexity=3
        ))
        
        self.add_card(Card(
            id="util_clean",
            name="Clean Contract",
            description="Remove inactive lines from the contract",
            code="__contract__.clean()",
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        self.add_card(Card(
            id="util_optimize",
            name="Optimize Contract",
            description="Optimize the execution order",
            code="__contract__.optimize()",
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_decrement_y",
            name="Decrement Y",
            description="Subtract 1 from y",
            code="y -= 1",
            card_type=CardType.DEFENSIVE,
            complexity=1
        )) 