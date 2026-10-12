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
            complexity=1
        ))
        
        self.add_card(Card(
            id="op_decrement_x",
            name="Decrement X",
            description="Subtract 1 from x",
            code="x -= 1",
            card_type=CardType.DEFENSIVE_X,
            complexity=1
        ))
        
        # Y-focused cards
        self.add_card(Card(
            id="op_increment_y",
            name="Increment Y",
            description="Add 1 to y",
            code="y += 1",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=1
        ))
        
        self.add_card(Card(
            id="op_decrement_y",
            name="Decrement Y",
            description="Subtract 1 from y",
            code="y -= 1",
            card_type=CardType.DEFENSIVE_Y,
            complexity=1
        ))
        
        self.add_card(Card(
            id="op_double_x",
            name="Double X",
            description="Multiply x by 2",
            code="x *= 2",
            card_type=CardType.AGGRESSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_double_y",
            name="Double Y",
            description="Multiply y by 2",
            code="y *= 2",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_halve_x",
            name="Halve X",
            description="Divide x by 2",
            code="x //= 2",
            card_type=CardType.DEFENSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_halve_y",
            name="Halve Y",
            description="Divide y by 2",
            code="y //= 2",
            card_type=CardType.DEFENSIVE_Y,
            complexity=2
        ))

        self.add_card(Card(
            id="op_add_z_to_x",
            name="Add Z to X",
            description="Add z to x",
            code="x += z",
            card_type=CardType.AGGRESSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_add_z_to_y",
            name="Add Z to Y",
            description="Add z to y",
            code="y += z",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_catch_up_x",
            name="Catch Up X",
            description="Set x to y if y is larger",
            code="x = x if x > y else y",
            card_type=CardType.AGGRESSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_catch_up_y",
            name="Catch Up Y",
            description="Set y to x if x is larger",
            code="y = y if y > x else x",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=2
        ))

        # Variable Transfers - Strategic moves
        self.add_card(Card(
            id="swap_x_y",
            name="Swap X and Y",
            description="Swap the values of x and y",
            code="x, y = y, x",
            card_type=CardType.STRATEGIC,
            complexity=2
        ))
        
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

        # Z-related operations remain UTILITY type since they're neutral storage
        self.add_card(Card(
            id="transfer_x_to_z",
            name="X to Z",
            description="Set z equal to x",
            code="z = x",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        self.add_card(Card(
            id="transfer_y_to_z",
            name="Y to Z",
            description="Set z equal to y",
            code="z = y",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        self.add_card(Card(
            id="transfer_z_to_x",
            name="Z to X",
            description="Set x equal to z",
            code="x = z",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        self.add_card(Card(
            id="transfer_z_to_y",
            name="Z to Y",
            description="Set y equal to z",
            code="y = z",
            card_type=CardType.UTILITY,
            complexity=1
        ))

        self.add_card(Card(
            id="util_increment_z",
            name="Increment Z",
            description="Add 1 to z",
            code="z += 1",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        self.add_card(Card(
            id="util_double_z",
            name="Double Z",
            description="Multiply z by 2",
            code="z *= 2",
            card_type=CardType.UTILITY,
            complexity=2
        ))

        # Contract manipulation cards remain as UTILITY
        self.add_card(Card(
            id="util_reset_z",
            name="Reset Z",
            description="Reset z to 0",
            code="z = 0",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
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

        # Expanded deck: more ways to advance, defend and reshape the contract
        self.add_card(Card(
            id="op_underdog_x",
            name="Underdog X",
            description="Add 1 to x if x is behind y",
            code="x += 1 if x < y else 0",
            card_type=CardType.AGGRESSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_copy_z_if_larger_x",
            name="Copy Z to X if Larger",
            description="Set x to z if z is larger",
            code="x = z if z > x else x",
            card_type=CardType.AGGRESSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_add_y_to_x",
            name="Add Y to X",
            description="Add y to x",
            code="x += y",
            card_type=CardType.AGGRESSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_square_x",
            name="Square X",
            description="Multiply x by itself",
            code="x *= x",
            card_type=CardType.AGGRESSIVE_X,
            complexity=3
        ))
        
        self.add_card(Card(
            id="op_reset_x",
            name="Reset X",
            description="Set x to 0",
            code="x = 0",
            card_type=CardType.DEFENSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_x_minus_z",
            name="X Minus Z",
            description="Subtract z from x",
            code="x -= z",
            card_type=CardType.DEFENSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_negate_x",
            name="Negate X",
            description="Flip the sign of x",
            code="x = -x",
            card_type=CardType.DEFENSIVE_X,
            complexity=2
        ))
        
        self.add_card(Card(
            id="swap_x_z",
            name="Swap X and Z",
            description="Swap the values of x and z",
            code="x, z = z, x",
            card_type=CardType.STRATEGIC,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_underdog_y",
            name="Underdog Y",
            description="Add 1 to y if y is behind x",
            code="y += 1 if y < x else 0",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_copy_z_if_larger_y",
            name="Copy Z to Y if Larger",
            description="Set y to z if z is larger",
            code="y = z if z > y else y",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_add_x_to_y",
            name="Add X to Y",
            description="Add x to y",
            code="y += x",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_square_y",
            name="Square Y",
            description="Multiply y by itself",
            code="y *= y",
            card_type=CardType.AGGRESSIVE_Y,
            complexity=3
        ))
        
        self.add_card(Card(
            id="op_reset_y",
            name="Reset Y",
            description="Set y to 0",
            code="y = 0",
            card_type=CardType.DEFENSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_y_minus_z",
            name="Y Minus Z",
            description="Subtract z from y",
            code="y -= z",
            card_type=CardType.DEFENSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="op_negate_y",
            name="Negate Y",
            description="Flip the sign of y",
            code="y = -y",
            card_type=CardType.DEFENSIVE_Y,
            complexity=2
        ))
        
        self.add_card(Card(
            id="swap_y_z",
            name="Swap Y and Z",
            description="Swap the values of y and z",
            code="y, z = z, y",
            card_type=CardType.STRATEGIC,
            complexity=2
        ))
        
        self.add_card(Card(
            id="util_halve_z",
            name="Halve Z",
            description="Divide z by 2",
            code="z //= 2",
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        self.add_card(Card(
            id="util_decrement_z",
            name="Decrement Z",
            description="Subtract 1 from z",
            code="z -= 1",
            card_type=CardType.UTILITY,
            complexity=1
        ))
        
        self.add_card(Card(
            id="util_remove_first",
            name="Remove First Line",
            description="Remove the line that runs first",
            code="__contract__.remove_first()",
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        self.add_card(Card(
            id="util_duplicate_last",
            name="Duplicate Last Line",
            description="Add another copy of the most recently added line",
            code="__contract__.duplicate_last()",
            card_type=CardType.UTILITY,
            complexity=2
        ))
        
        self.add_card(Card(
            id="util_last_to_top",
            name="Move Last Line to Top",
            description="Make the line that runs last run first instead",
            code="__contract__.last_to_top()",
            card_type=CardType.UTILITY,
            complexity=3
        ))
