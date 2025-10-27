"""
RangeConstructor: Build hand ranges based on various criteria

Used by both hypotheses to:
- H1: Build push/call ranges based on equilibrium conditions
- H2: Build value ranges and bluff candidate ranges
"""

import sys
from typing import List, Optional, Callable
import itertools

sys.path.append('/home/user/poker-analytics/src')
from deuces import Card, Evaluator
from game_theory.common.hand_range import HandRange
from game_theory.common.equity_calculator import EquityCalculator
from game_theory.common.board_analyzer import BoardAnalyzer


class RangeConstructor:
    """
    Construct hand ranges based on various criteria.

    Methods:
    - construct_by_equity: Build range with minimum equity threshold
    - construct_top_percent: Build range with top X% of hands
    - construct_value_range: Build value betting range
    - construct_bluff_candidates: Build bluffing range
    """

    # Hand rankings for preflop (approximate)
    HAND_RANKINGS = [
        'AA', 'KK', 'QQ', 'JJ', 'TT',  # Premium pairs
        'AKs', 'AQs', 'AJs', 'AKo',  # Ace-high
        '99', 'ATs', 'AQo', 'KQs',  # Strong hands
        '88', 'AJo', 'KJs', 'KTs', 'QJs',  # Good hands
        '77', 'ATo', 'KQo', 'QTs', 'JTs',  # Playable hands
        '66', 'A9s', 'KJo', 'QJo', 'JTo',
        '55', 'A8s', 'A7s', 'KTo', 'QTo',
        '44', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',  # Suited aces
        '33', '22',  # Small pairs
        'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s',  # Suited kings
        'Q9s', 'J9s', 'T9s', '98s', '87s', '76s', '65s',  # Suited connectors
        'A9o', 'A8o', 'A7o', 'A6o', 'A5o', 'A4o', 'A3o', 'A2o',  # Offsuit aces
        'K9o', 'Q9o', 'J9o', 'T9o',  # Weak offsuit
        '54s', '43s', '32s',  # Weak suited connectors
    ]

    def __init__(self):
        self.equity_calc = EquityCalculator()
        self.evaluator = Evaluator()

    def construct_top_percent(self, target_percent: float) -> HandRange:
        """
        Construct range containing top X% of hands.

        Args:
            target_percent: Desired percentage (0-100)

        Returns:
            HandRange with approximately target_percent frequency
        """
        hand_range = HandRange()
        current_percent = 0.0

        for hand_str in self.HAND_RANKINGS:
            hand_range.add_hand(hand_str)
            current_percent = hand_range.get_frequency()

            if current_percent >= target_percent:
                break

        return hand_range

    def construct_by_equity(self, equity_threshold: float,
                           vs_range: HandRange,
                           board: Optional[List[int]] = None) -> HandRange:
        """
        Construct range where all hands have equity >= threshold vs opponent range.

        Args:
            equity_threshold: Minimum equity required (0.0 to 1.0)
            vs_range: Opponent's range
            board: Optional board cards

        Returns:
            HandRange with hands meeting equity requirement
        """
        if board is None:
            board = []

        result_range = HandRange()

        # Test each hand class
        for hand_str in self.HAND_RANKINGS:
            # Create a sample hand
            try:
                sample_hand = self._create_sample_hand(hand_str, board)
                if sample_hand:
                    equity = self.equity_calc.hand_vs_range_equity(
                        sample_hand, vs_range, board, n_simulations=1000
                    )

                    if equity >= equity_threshold:
                        result_range.add_hand(hand_str)
            except:
                # Skip hands that can't be created (blocked by board)
                continue

        return result_range

    def construct_value_range(self, board: List[int],
                             calling_range: HandRange,
                             equity_threshold: float = 0.65) -> HandRange:
        """
        Construct value betting range.

        Value hands are those that have equity > threshold vs calling range.

        Args:
            board: Board cards
            calling_range: Opponent's calling range
            equity_threshold: Minimum equity for value bet (default 0.65)

        Returns:
            HandRange suitable for value betting
        """
        return self.construct_by_equity(equity_threshold, calling_range, board)

    def construct_bluff_candidates(self, board: List[int],
                                   value_range: HandRange,
                                   max_equity: float = 0.35,
                                   num_candidates: int = 50) -> List[str]:
        """
        Find best bluff candidates for given board.

        Good bluffs:
        - Have low equity (< max_equity)
        - Have blocker value
        - Can credibly represent value range

        Args:
            board: Board cards
            value_range: Value betting range (to ensure bluffs make sense)
            max_equity: Maximum equity for bluff candidate
            num_candidates: Number of bluff candidates to return

        Returns:
            List of hand strings sorted by bluff quality
        """
        analyzer = BoardAnalyzer(board)
        bluff_candidates = []

        # All possible starting hands (simplified)
        all_hands = self.HAND_RANKINGS[30:]  # Weak hands only

        for hand_str in all_hands:
            try:
                sample_hand = self._create_sample_hand(hand_str, board)
                if not sample_hand:
                    continue

                # Check if low equity (weak hand)
                # We'll approximate equity based on ranking
                # In practice, would calculate vs opponent range

                # Calculate blocker value
                blocker_value = analyzer.get_blocker_value(sample_hand)

                # Score this bluff candidate
                # Higher score = better bluff
                score = blocker_value

                # Prefer suited hands (for flush draws that missed)
                if hand_str.endswith('S'):
                    score += 1

                # Prefer connected hands (for straight draws that missed)
                if self._is_connected(hand_str):
                    score += 1

                bluff_candidates.append((hand_str, score))

            except:
                continue

        # Sort by score (descending)
        bluff_candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top N
        return [hand for hand, score in bluff_candidates[:num_candidates]]

    def construct_polarized_range(self, board: List[int],
                                  value_percent: float = 15.0,
                                  bluff_percent: float = 10.0) -> tuple:
        """
        Construct a polarized betting range (strong hands + bluffs).

        Args:
            board: Board cards
            value_percent: Top X% for value
            bluff_percent: Bottom X% for bluffs

        Returns:
            Tuple of (value_range, bluff_range)
        """
        # Build value range (top hands)
        value_range = self.construct_top_percent(value_percent)

        # Build bluff range
        # Start from weak hands
        bluff_range = HandRange()
        candidates = self.construct_bluff_candidates(board, value_range, num_candidates=20)

        for hand_str in candidates[:10]:  # Take top 10 bluffs
            bluff_range.add_hand(hand_str)

        return value_range, bluff_range

    def construct_calling_range(self, pot_odds: float,
                                betting_range: HandRange,
                                board: List[int] = None) -> HandRange:
        """
        Construct calling range based on pot odds.

        Calls when: Equity vs betting range >= pot odds

        Args:
            pot_odds: Pot odds being offered (0.0 to 1.0)
            betting_range: Opponent's betting range
            board: Optional board cards

        Returns:
            HandRange that should call based on pot odds
        """
        return self.construct_by_equity(pot_odds, betting_range, board)

    def _create_sample_hand(self, hand_str: str, board: List[int]) -> Optional[List[int]]:
        """
        Create a sample hand from hand string, avoiding board cards.

        Args:
            hand_str: Hand string like "AKs", "AA", etc.
            board: Board cards to avoid

        Returns:
            List of two card integers, or None if can't create
        """
        # Parse hand string
        rank1 = hand_str[0]
        rank2 = hand_str[1]
        is_suited = hand_str.endswith('S')

        # Get board cards for blocking
        board_set = set(board)

        # Try to create hand
        if rank1 == rank2:
            # Pair - try different suits
            for suit1 in ['s', 'h', 'd', 'c']:
                for suit2 in ['s', 'h', 'd', 'c']:
                    if suit1 < suit2:
                        card1 = Card.new(rank1 + suit1)
                        card2 = Card.new(rank2 + suit2)
                        if card1 not in board_set and card2 not in board_set:
                            return [card1, card2]
        elif is_suited:
            # Suited - try each suit
            for suit in ['s', 'h', 'd', 'c']:
                card1 = Card.new(rank1 + suit)
                card2 = Card.new(rank2 + suit)
                if card1 not in board_set and card2 not in board_set:
                    return [card1, card2]
        else:
            # Offsuit - try different suits
            for suit1 in ['s', 'h', 'd', 'c']:
                for suit2 in ['s', 'h', 'd', 'c']:
                    if suit1 != suit2:
                        card1 = Card.new(rank1 + suit1)
                        card2 = Card.new(rank2 + suit2)
                        if card1 not in board_set and card2 not in board_set:
                            return [card1, card2]

        return None

    def _is_connected(self, hand_str: str) -> bool:
        """Check if hand ranks are connected (within 2)"""
        rank1 = hand_str[0]
        rank2 = hand_str[1]

        ranks = '23456789TJQKA'
        idx1 = ranks.index(rank1)
        idx2 = ranks.index(rank2)

        return abs(idx1 - idx2) <= 2


if __name__ == "__main__":
    print("Testing RangeConstructor...\n")

    constructor = RangeConstructor()

    # Test 1: Top percent
    print("Test 1: Construct top 10% of hands")
    top_10 = constructor.construct_top_percent(10.0)
    print(f"  Range: {top_10}")
    print(f"  Actual frequency: {top_10.get_frequency():.2f}%")
    print()

    # Test 2: Top 20%
    print("Test 2: Construct top 20% of hands")
    top_20 = constructor.construct_top_percent(20.0)
    print(f"  Range: {top_20}")
    print(f"  Actual frequency: {top_20.get_frequency():.2f}%")
    print()

    # Test 3: Bluff candidates on a board
    board = [Card.new('Kh'), Card.new('Qd'), Card.new('Jc'),
             Card.new('5s'), Card.new('2h')]
    print("Test 3: Find bluff candidates on K♥ Q♦ J♣ 5♠ 2♥")

    value_range = constructor.construct_top_percent(15.0)
    bluffs = constructor.construct_bluff_candidates(board, value_range, num_candidates=10)
    print(f"  Top 10 bluff candidates: {', '.join(bluffs[:10])}")
    print()

    # Test 4: Polarized range
    print("Test 4: Construct polarized range (15% value, 10% bluffs)")
    value_r, bluff_r = constructor.construct_polarized_range(board, 15.0, 10.0)
    print(f"  Value range ({value_r.get_frequency():.1f}%): {value_r}")
    print(f"  Bluff range ({bluff_r.get_frequency():.1f}%): {bluff_r}")
    print()

    # Test 5: Equity-based range
    print("Test 5: Construct range with 60%+ equity vs TT+,AK")
    opponent_range = HandRange()
    opponent_range.add_hand_range("TT+, AK")

    equity_range = constructor.construct_by_equity(0.60, opponent_range)
    print(f"  Range: {equity_range}")
    print(f"  Frequency: {equity_range.get_frequency():.2f}%")
    print()

    print("RangeConstructor tests completed!")
