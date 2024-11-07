from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

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
    complexity: int  # 1-5 scale

class CardLibrary:
    def __init__(self):
        self.cards: Dict[str, Card] = {}
        self._initialize_cards()
        
    def _initialize_cards(self):
        # Aggressive Cards
        self.add_card(Card(
            id="agg_1",
            name="Direct Increment",
            description="Directly increment x by 1",
            code="x += 1",
            card_type=CardType.AGGRESSIVE,
            complexity=1
        ))
        
        self.add_card(Card(
            id="agg_2",
            name="Double Strike",
            description="Double the value of x",
            code="x *= 2",
            card_type=CardType.AGGRESSIVE,
            complexity=2
        ))
        
        self.add_card(Card(
            id="agg_3",
            name="Power Play",
            description="Add y's value to x",
            code="x += y",
            card_type=CardType.AGGRESSIVE,
            complexity=3
        ))
        
        # Defensive Cards
        self.add_card(Card(
            id="def_1",
            name="Decrease Y",
            description="Decrease y by 1",
            code="y -= 1",
            card_type=CardType.DEFENSIVE,
            complexity=1
        ))
        
        self.add_card(Card(
            id="def_2",
            name="Halve Y",
            description="Divide y by 2",
            code="y //= 2",
            card_type=CardType.DEFENSIVE,
            complexity=2
        ))
        
        self.add_card(Card(
            id="def_3",
            name="Negate Y",
            description="Make y negative",
            code="y = -abs(y)",
            card_type=CardType.DEFENSIVE,
            complexity=3
        ))
        
        # Strategic Cards
        self.add_card(Card(
            id="str_1",
            name="Variable Swap",
            description="Swap x and y values using z",
            code="z = x; x = y; y = z",
            card_type=CardType.STRATEGIC,
            complexity=3
        ))
        
        self.add_card(Card(
            id="str_2",
            name="Conditional Boost",
            description="Double x if y is negative",
            code="x *= 2 if y < 0 else x",
            card_type=CardType.STRATEGIC,
            complexity=4
        ))
        
        self.add_card(Card(
            id="str_3",
            name="Value Storage",
            description="Store x's value in z",
            code="z = x",
            card_type=CardType.STRATEGIC,
            complexity=1
        ))
        
        # Utility Cards
        self.add_card(Card(
            id="util_1",
            name="Reset Z",
            description="Reset z to 0",
            code="z = 0",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        self.add_card(Card(
            id="util_2",
            name="Absolute Value",
            description="Make x positive",
            code="x = abs(x)",
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        # Utility Cards for Contract Management
        self.add_card(Card(
            id="util_1",
            name="Remove Last Line",
            description="Remove the most recently added line from the contract",
            code="__contract__.pop()",  # Special command
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        self.add_card(Card(
            id="util_2",
            name="Clear Inactive Lines",
            description="Remove all lines that aren't in the execution order",
            code="__contract__.clean()",  # Special command
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        self.add_card(Card(
            id="util_3",
            name="Optimize Order",
            description="Reorder execution to match code order",
            code="__contract__.optimize()",  # Special command
            card_type=CardType.UTILITY,
            complexity=3
        ))

    def add_card(self, card: Card):
        self.cards[card.id] = card
        
    def get_cards_by_type(self, card_type: CardType) -> List[Card]:
        return [card for card in self.cards.values() if card.card_type == card_type]
        
    def get_card(self, card_id: str) -> Card:
        return self.cards.get(card_id) 