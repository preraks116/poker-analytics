"""
HandRange: Efficient representation and manipulation of poker hand ranges

This class provides the foundation for range-based analysis in both
push/fold equilibrium and optimal bluffing frequency studies.
"""

import numpy as np
from typing import List, Set, Tuple, Optional, Dict
from collections import defaultdict
import itertools
import sys
sys.path.append('/home/user/poker-analytics/src')
from deuces import Card


class HandRange:
    """
    Represents a range of poker hands using efficient matrix storage.

    Stores hands in two 13x13 matrices:
    - suited_matrix: For suited hands (AKs, etc.)
    - offsuit_matrix: For offsuit hands (AKo, etc.)
    - Pairs are stored on the diagonal of suited_matrix

    Ranks are indexed 0-12: 2, 3, 4, 5, 6, 7, 8, 9, T, J, Q, K, A
    """

    # Rank mappings
    RANKS = '23456789TJQKA'
    RANK_TO_INT = {r: i for i, r in enumerate(RANKS)}
    INT_TO_RANK = {i: r for i, r in enumerate(RANKS)}

    def __init__(self):
        """Initialize empty hand range"""
        self.suited_matrix = np.zeros((13, 13), dtype=bool)
        self.offsuit_matrix = np.zeros((13, 13), dtype=bool)
        self.hand_list = []  # Cache of hands for quick access
        self._dirty = False  # Track if hand_list needs update

    def add_hand(self, hand_str: str) -> None:
        """
        Add a hand or hand class to the range.

        Examples:
            "AA" - all pocket aces
            "AKs" - ace-king suited
            "AKo" - ace-king offsuit
            "AK" - all ace-king (suited and offsuit)
        """
        hand_str = hand_str.upper().strip()

        if len(hand_str) < 2:
            raise ValueError(f"Invalid hand string: {hand_str}")

        rank1 = hand_str[0]
        rank2 = hand_str[1]

        if rank1 not in self.RANK_TO_INT or rank2 not in self.RANK_TO_INT:
            raise ValueError(f"Invalid ranks in hand: {hand_str}")

        r1 = self.RANK_TO_INT[rank1]
        r2 = self.RANK_TO_INT[rank2]

        # Ensure r1 >= r2 (higher rank first)
        if r1 < r2:
            r1, r2 = r2, r1

        # Determine if suited, offsuit, or both
        if len(hand_str) == 2:
            # No suffix - pocket pair or all combos
            if r1 == r2:
                self.suited_matrix[r1, r2] = True
            else:
                self.suited_matrix[r1, r2] = True
                self.offsuit_matrix[r1, r2] = True
        elif hand_str.endswith('S'):
            # Suited only
            self.suited_matrix[r1, r2] = True
        elif hand_str.endswith('O'):
            # Offsuit only
            self.offsuit_matrix[r1, r2] = True
        else:
            raise ValueError(f"Invalid hand suffix: {hand_str}")

        self._dirty = True

    def add_hand_range(self, range_str: str) -> None:
        """
        Add multiple hands from a range string.

        Examples:
            "AA, KK, AKs"
            "22+, A2s+, KQs+"
            "AA-TT, AK, AQ"
        """
        # Split by comma and process each part
        parts = [p.strip() for p in range_str.split(',')]

        for part in parts:
            if '+' in part:
                self._add_hand_plus(part)
            elif '-' in part:
                self._add_hand_range_dash(part)
            else:
                self.add_hand(part)

    def _add_hand_plus(self, hand_str: str) -> None:
        """Add a hand and all stronger versions (e.g., 'ATs+' adds ATs, AJs, AQs, AKs)"""
        hand_str = hand_str.rstrip('+')

        if len(hand_str) < 2:
            raise ValueError(f"Invalid hand+ string: {hand_str}")

        rank1 = hand_str[0]
        rank2 = hand_str[1]
        r1 = self.RANK_TO_INT[rank1]
        r2 = self.RANK_TO_INT[rank2]

        if r1 < r2:
            r1, r2 = r2, r1

        suited_only = hand_str.endswith('S')
        offsuit_only = hand_str.endswith('O')

        if r1 == r2:
            # Pocket pairs: add this pair and all higher
            for rank in range(r1, 13):
                self.suited_matrix[rank, rank] = True
        else:
            # Non-pairs: add this and all with higher second card
            for rank2_new in range(r2, r1):
                if suited_only:
                    self.suited_matrix[r1, rank2_new] = True
                elif offsuit_only:
                    self.offsuit_matrix[r1, rank2_new] = True
                else:
                    self.suited_matrix[r1, rank2_new] = True
                    self.offsuit_matrix[r1, rank2_new] = True

        self._dirty = True

    def _add_hand_range_dash(self, range_str: str) -> None:
        """Add a range like 'AA-TT' (all pairs from AA to TT)"""
        parts = range_str.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid range string: {range_str}")

        start_hand = parts[0].strip()
        end_hand = parts[1].strip()

        # For pairs
        if len(start_hand) == 2 and start_hand[0] == start_hand[1]:
            start_rank = self.RANK_TO_INT[start_hand[0]]
            end_rank = self.RANK_TO_INT[end_hand[0]]

            if start_rank < end_rank:
                start_rank, end_rank = end_rank, start_rank

            for rank in range(end_rank, start_rank + 1):
                self.suited_matrix[rank, rank] = True
        else:
            raise ValueError(f"Dash notation currently only supports pairs: {range_str}")

        self._dirty = True

    def remove_hand(self, hand_str: str) -> None:
        """Remove a hand from the range"""
        hand_str = hand_str.upper().strip()

        if len(hand_str) < 2:
            return

        rank1 = hand_str[0]
        rank2 = hand_str[1]
        r1 = self.RANK_TO_INT[rank1]
        r2 = self.RANK_TO_INT[rank2]

        if r1 < r2:
            r1, r2 = r2, r1

        if len(hand_str) == 2:
            if r1 == r2:
                self.suited_matrix[r1, r2] = False
            else:
                self.suited_matrix[r1, r2] = False
                self.offsuit_matrix[r1, r2] = False
        elif hand_str.endswith('S'):
            self.suited_matrix[r1, r2] = False
        elif hand_str.endswith('O'):
            self.offsuit_matrix[r1, r2] = False

        self._dirty = True

    def contains(self, hand_str: str) -> bool:
        """Check if a specific hand is in the range"""
        hand_str = hand_str.upper().strip()

        if len(hand_str) < 2:
            return False

        rank1 = hand_str[0]
        rank2 = hand_str[1]

        if rank1 not in self.RANK_TO_INT or rank2 not in self.RANK_TO_INT:
            return False

        r1 = self.RANK_TO_INT[rank1]
        r2 = self.RANK_TO_INT[rank2]

        if r1 < r2:
            r1, r2 = r2, r1

        if len(hand_str) == 2:
            if r1 == r2:
                return bool(self.suited_matrix[r1, r2])
            else:
                return bool(self.suited_matrix[r1, r2] or self.offsuit_matrix[r1, r2])
        elif hand_str.endswith('S'):
            return bool(self.suited_matrix[r1, r2])
        elif hand_str.endswith('O'):
            return bool(self.offsuit_matrix[r1, r2])

        return False

    def get_combinations(self, board: Optional[List[int]] = None) -> int:
        """
        Count total number of hand combinations in range.

        If board is provided, remove dead cards from combinations.
        Pairs: 6 combos (4 choose 2)
        Suited: 4 combos
        Offsuit: 12 combos
        """
        total = 0

        # Track which cards are unavailable
        blocked_ranks = defaultdict(set)
        if board:
            for card_int in board:
                rank = Card.get_rank_int(card_int)
                suit = Card.get_suit_int(card_int)
                blocked_ranks[rank].add(suit)

        for r1 in range(13):
            for r2 in range(13):
                if r1 == r2 and self.suited_matrix[r1, r2]:
                    # Pocket pair
                    available_suits = 4 - len(blocked_ranks.get(r1, set()))
                    combos = available_suits * (available_suits - 1) // 2
                    total += combos
                elif r1 > r2:
                    # Non-pair
                    if self.suited_matrix[r1, r2]:
                        # Suited combos (4 suits)
                        for suit in range(4):
                            if suit not in blocked_ranks.get(r1, set()) and \
                               suit not in blocked_ranks.get(r2, set()):
                                total += 1

                    if self.offsuit_matrix[r1, r2]:
                        # Offsuit combos
                        suits_r1 = set(range(4)) - blocked_ranks.get(r1, set())
                        suits_r2 = set(range(4)) - blocked_ranks.get(r2, set())
                        for s1 in suits_r1:
                            for s2 in suits_r2:
                                if s1 != s2:
                                    total += 1

        return total

    def get_frequency(self) -> float:
        """Return what percentage of all starting hands are in this range"""
        total_combos = self.get_combinations()
        return (total_combos / 1326.0) * 100.0  # 1326 total starting hands

    def get_hand_list(self) -> List[str]:
        """Return list of hand classes in range (e.g., ['AA', 'AKs', 'AKo'])"""
        if not self._dirty and self.hand_list:
            return self.hand_list

        hands = []

        for r1 in range(13):
            for r2 in range(13):
                rank1_str = self.INT_TO_RANK[r1]
                rank2_str = self.INT_TO_RANK[r2]

                if r1 == r2 and self.suited_matrix[r1, r2]:
                    hands.append(f"{rank1_str}{rank2_str}")
                elif r1 > r2:
                    if self.suited_matrix[r1, r2]:
                        hands.append(f"{rank1_str}{rank2_str}s")
                    if self.offsuit_matrix[r1, r2]:
                        hands.append(f"{rank1_str}{rank2_str}o")

        self.hand_list = hands
        self._dirty = False
        return hands

    def to_string(self) -> str:
        """Convert range to compact string notation"""
        return ", ".join(self.get_hand_list())

    def clear(self) -> None:
        """Remove all hands from range"""
        self.suited_matrix.fill(False)
        self.offsuit_matrix.fill(False)
        self.hand_list = []
        self._dirty = False

    def copy(self) -> 'HandRange':
        """Create a deep copy of this range"""
        new_range = HandRange()
        new_range.suited_matrix = self.suited_matrix.copy()
        new_range.offsuit_matrix = self.offsuit_matrix.copy()
        new_range.hand_list = self.hand_list.copy()
        new_range._dirty = self._dirty
        return new_range

    def intersection(self, other: 'HandRange') -> 'HandRange':
        """Return a new range with hands in both ranges"""
        new_range = HandRange()
        new_range.suited_matrix = self.suited_matrix & other.suited_matrix
        new_range.offsuit_matrix = self.offsuit_matrix & other.offsuit_matrix
        new_range._dirty = True
        return new_range

    def union(self, other: 'HandRange') -> 'HandRange':
        """Return a new range with hands in either range"""
        new_range = HandRange()
        new_range.suited_matrix = self.suited_matrix | other.suited_matrix
        new_range.offsuit_matrix = self.offsuit_matrix | other.offsuit_matrix
        new_range._dirty = True
        return new_range

    def difference(self, other: 'HandRange') -> 'HandRange':
        """Return a new range with hands in this range but not the other"""
        new_range = HandRange()
        new_range.suited_matrix = self.suited_matrix & ~other.suited_matrix
        new_range.offsuit_matrix = self.offsuit_matrix & ~other.offsuit_matrix
        new_range._dirty = True
        return new_range

    def __repr__(self) -> str:
        freq = self.get_frequency()
        combos = self.get_combinations()
        return f"HandRange({combos} combos, {freq:.1f}%)"

    def __str__(self) -> str:
        return self.to_string()


if __name__ == "__main__":
    # Test the HandRange class
    print("Testing HandRange class...")

    # Test 1: Add individual hands
    range1 = HandRange()
    range1.add_hand("AA")
    range1.add_hand("KK")
    range1.add_hand("AKs")
    range1.add_hand("AKo")
    print(f"Range 1: {range1}")
    print(f"  Combinations: {range1.get_combinations()}")
    print(f"  Frequency: {range1.get_frequency():.2f}%")

    # Test 2: Add range string
    range2 = HandRange()
    range2.add_hand_range("AA-TT, AK, AQ")
    print(f"\nRange 2: {range2}")
    print(f"  Combinations: {range2.get_combinations()}")
    print(f"  Frequency: {range2.get_frequency():.2f}%")

    # Test 3: Plus notation
    range3 = HandRange()
    range3.add_hand_range("88+, ATs+, KQs")
    print(f"\nRange 3: {range3}")
    print(f"  Combinations: {range3.get_combinations()}")

    # Test 4: Union
    range4 = range1.union(range2)
    print(f"\nRange 4 (1 ∪ 2): {range4}")
    print(f"  Combinations: {range4.get_combinations()}")

    # Test 5: Contains
    print(f"\nRange 2 contains 'AA': {range2.contains('AA')}")
    print(f"Range 2 contains 'AKs': {range2.contains('AKs')}")
    print(f"Range 2 contains '72o': {range2.contains('72o')}")

    print("\nHandRange tests completed!")
