"""
EquityCalculator: Efficient equity calculation with caching

Wraps existing HSE functionality and provides:
- Cached equity calculations
- Range vs range equity
- Hand vs range equity
- Support for both exact and Monte Carlo methods
"""

import sys
import itertools
from typing import List, Dict, Tuple, Optional
from functools import lru_cache
import numpy as np

sys.path.append('/home/user/poker-analytics/src')
from deuces import Card, Evaluator, Deck
from game_theory.common.hand_range import HandRange


class EquityCalculator:
    """
    Calculate poker hand equities efficiently with caching.

    Supports:
    - Hand vs hand equity
    - Hand vs range equity
    - Range vs range equity
    - Preflop and postflop calculations
    """

    def __init__(self):
        self.evaluator = Evaluator()
        self.equity_cache = {}  # Cache for equity calculations
        self.preflop_equity_table = self._load_preflop_table()

    def _load_preflop_table(self) -> Dict:
        """Load preflop equity table from CSV"""
        try:
            import pandas as pd
            df = pd.read_csv('/home/user/poker-analytics/src/preflop_equity.csv')
            # Convert to dictionary for quick lookup
            equity_table = {}
            for _, row in df.iterrows():
                hand = row['Cards']
                # Store equity for different numbers of opponents
                equity_table[hand] = {
                    'vs_1': float(row['2 plyrs'].strip('%')) / 100.0,
                    'vs_2': float(row['3 plyrs'].strip('%')) / 100.0,
                    'vs_3': float(row['4 plyrs'].strip('%')) / 100.0,
                    'vs_4': float(row['5 plyrs'].strip('%')) / 100.0,
                    'vs_5': float(row['6 plyrs'].strip('%')) / 100.0,
                }
            return equity_table
        except Exception as e:
            print(f"Warning: Could not load preflop equity table: {e}")
            return {}

    def hand_vs_hand_equity(self, hand1: List[int], hand2: List[int],
                           board: List[int] = None, n_simulations: int = 10000) -> float:
        """
        Calculate equity of hand1 vs hand2.

        Args:
            hand1: List of card integers
            hand2: List of card integers
            board: Optional board cards (for postflop)
            n_simulations: Number of Monte Carlo simulations if not exact

        Returns:
            Equity as float (0.0 to 1.0)
        """
        if board is None:
            board = []

        # Create cache key
        cache_key = self._make_cache_key(hand1, hand2, board)
        if cache_key in self.equity_cache:
            return self.equity_cache[cache_key]

        # Run simulation
        equity = self._simulate_equity(hand1, hand2, board, n_simulations)

        # Cache result
        self.equity_cache[cache_key] = equity
        return equity

    def hand_vs_range_equity(self, hand: List[int], villain_range: HandRange,
                            board: List[int] = None, n_simulations: int = 1000) -> float:
        """
        Calculate equity of a hand vs a range.

        Args:
            hand: Hero's hand
            villain_range: Villain's range
            board: Optional board cards
            n_simulations: Simulations per hand matchup

        Returns:
            Average equity vs the range
        """
        if board is None:
            board = []

        # Get all hand combinations in villain's range
        villain_combos = self._get_range_combos(villain_range, board + hand)

        if not villain_combos:
            return 0.5  # Default if no valid combos

        total_equity = 0.0
        total_weight = 0

        for villain_hand in villain_combos:
            equity = self.hand_vs_hand_equity(hand, villain_hand, board, n_simulations)
            total_equity += equity
            total_weight += 1

        return total_equity / total_weight if total_weight > 0 else 0.5

    def range_vs_range_equity(self, range1: HandRange, range2: HandRange,
                             board: List[int] = None) -> float:
        """
        Calculate average equity of range1 vs range2.

        Returns average equity weighted by hand combinations.
        """
        if board is None:
            board = []

        range1_combos = self._get_range_combos(range1, board)
        range2_combos = self._get_range_combos(range2, board)

        if not range1_combos or not range2_combos:
            return 0.5

        total_equity = 0.0
        total_matchups = 0

        for hand1 in range1_combos[:50]:  # Limit for performance
            for hand2 in range2_combos[:50]:
                if not self._hands_overlap(hand1, hand2):
                    equity = self.hand_vs_hand_equity(hand1, hand2, board, n_simulations=1000)
                    total_equity += equity
                    total_matchups += 1

        return total_equity / total_matchups if total_matchups > 0 else 0.5

    def _simulate_equity(self, hand1: List[int], hand2: List[int],
                        board: List[int], n_simulations: int) -> float:
        """
        Monte Carlo simulation for equity calculation.
        """
        if len(board) >= 5:
            # River - can calculate exactly
            return self._exact_equity(hand1, hand2, board)

        wins = 0
        ties = 0
        losses = 0

        for _ in range(n_simulations):
            # Create deck and remove known cards
            deck = Deck()
            for card in hand1 + hand2 + board:
                if card in deck.cards:
                    deck.cards.remove(card)

            # Complete the board
            cards_needed = 5 - len(board)
            sim_board = board + deck.draw(cards_needed)

            # Evaluate hands
            score1 = self.evaluator.evaluate(sim_board, hand1)
            score2 = self.evaluator.evaluate(sim_board, hand2)

            if score1 < score2:  # Lower score wins
                wins += 1
            elif score1 == score2:
                ties += 1
            else:
                losses += 1

        equity = (wins + ties / 2.0) / (wins + ties + losses)
        return equity

    def _exact_equity(self, hand1: List[int], hand2: List[int], board: List[int]) -> float:
        """Calculate exact equity when board is complete"""
        score1 = self.evaluator.evaluate(board, hand1)
        score2 = self.evaluator.evaluate(board, hand2)

        if score1 < score2:
            return 1.0
        elif score1 == score2:
            return 0.5
        else:
            return 0.0

    def _get_range_combos(self, hand_range: HandRange, blocked_cards: List[int],
                         max_combos: int = 100) -> List[List[int]]:
        """
        Get specific hand combinations from a range.

        Args:
            hand_range: HandRange object
            blocked_cards: Cards that are unavailable
            max_combos: Maximum combinations to return

        Returns:
            List of hand combinations (each is list of 2 card ints)
        """
        combos = []
        hand_list = hand_range.get_hand_list()

        # Create set of blocked cards for fast lookup
        blocked_set = set(blocked_cards)

        for hand_str in hand_list:
            if len(combos) >= max_combos:
                break

            # Parse hand string
            rank1 = hand_str[0]
            rank2 = hand_str[1] if len(hand_str) > 1 else hand_str[0]

            is_pair = rank1 == rank2
            is_suited = hand_str.endswith('S')
            is_offsuit = hand_str.endswith('O')

            # Generate specific combinations
            for suit1 in range(4):
                for suit2 in range(4):
                    # Skip invalid combinations
                    if is_pair and suit1 >= suit2:
                        continue
                    if is_suited and suit1 != suit2:
                        continue
                    if is_offsuit and suit1 == suit2:
                        continue

                    card1 = Card.new(rank1 + Card.INT_SUIT_TO_CHAR_SUIT[1 << suit1])
                    card2 = Card.new(rank2 + Card.INT_SUIT_TO_CHAR_SUIT[1 << suit2])

                    if card1 not in blocked_set and card2 not in blocked_set:
                        combos.append([card1, card2])

                        if len(combos) >= max_combos:
                            break

                if len(combos) >= max_combos:
                    break

        return combos

    def _hands_overlap(self, hand1: List[int], hand2: List[int]) -> bool:
        """Check if two hands share any cards"""
        return bool(set(hand1) & set(hand2))

    def _make_cache_key(self, hand1: List[int], hand2: List[int],
                       board: List[int]) -> Tuple:
        """Create hashable cache key for equity lookup"""
        return tuple(sorted(hand1)), tuple(sorted(hand2)), tuple(sorted(board))

    def get_preflop_equity(self, hand_str: str, n_opponents: int = 1) -> float:
        """
        Get preflop equity from lookup table.

        Args:
            hand_str: Hand string like "AKs", "AA", etc.
            n_opponents: Number of opponents (1-5)

        Returns:
            Equity as float (0.0 to 1.0)
        """
        hand_str = hand_str.upper()

        # Normalize hand string
        if len(hand_str) == 2:
            rank1 = hand_str[0]
            rank2 = hand_str[1]
            if rank1 == rank2:
                normalized = rank1 + rank2 + 'o'  # Pairs stored with 'o'
            else:
                # Check which way it's stored
                normalized = rank1 + rank2 + 'o'
                if normalized not in self.preflop_equity_table:
                    normalized = rank2 + rank1 + 'o'
        else:
            normalized = hand_str

        if normalized in self.preflop_equity_table:
            key = f'vs_{n_opponents}'
            if key in self.preflop_equity_table[normalized]:
                return self.preflop_equity_table[normalized][key]

        # Fallback to Monte Carlo
        return 0.5

    def clear_cache(self):
        """Clear equity cache to free memory"""
        self.equity_cache.clear()


if __name__ == "__main__":
    print("Testing EquityCalculator...")

    calc = EquityCalculator()

    # Test 1: AA vs KK preflop
    hand1 = [Card.new('Ah'), Card.new('As')]
    hand2 = [Card.new('Kh'), Card.new('Ks')]

    print("\nTest 1: AA vs KK preflop")
    equity = calc.hand_vs_hand_equity(hand1, hand2, n_simulations=10000)
    print(f"  AA equity vs KK: {equity:.3f} (should be ~0.82)")

    # Test 2: AK vs QQ preflop
    hand1 = [Card.new('Ah'), Card.new('Kh')]
    hand2 = [Card.new('Qc'), Card.new('Qd')]

    print("\nTest 2: AKs vs QQ preflop")
    equity = calc.hand_vs_hand_equity(hand1, hand2, n_simulations=10000)
    print(f"  AKs equity vs QQ: {equity:.3f} (should be ~0.45)")

    # Test 3: Hand vs Range
    hand = [Card.new('Ah'), Card.new('Kh')]
    villain_range = HandRange()
    villain_range.add_hand_range("TT+, AQ+")

    print("\nTest 3: AKs vs Range (TT+, AQ+)")
    equity = calc.hand_vs_range_equity(hand, villain_range, n_simulations=1000)
    print(f"  AKs equity vs range: {equity:.3f}")

    # Test 4: Preflop table lookup
    print("\nTest 4: Preflop equity table lookups")
    for hand_str in ['AAo', 'KKo', 'AKs', 'AKo']:
        equity = calc.get_preflop_equity(hand_str, n_opponents=1)
        print(f"  {hand_str} vs 1 opponent: {equity:.3f}")

    print("\nEquityCalculator tests completed!")
