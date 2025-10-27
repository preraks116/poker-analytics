"""
BluffingSolver: Calculate optimal bluffing frequencies

Core principle:
Optimal bluff frequency = Bet / (Pot + Bet)

This makes opponent indifferent to calling with bluff-catchers.
"""

import sys
from typing import List, Dict, Tuple, Optional

sys.path.append('/home/user/poker-analytics/src')
from deuces import Card
from game_theory.common.hand_range import HandRange
from game_theory.common.equity_calculator import EquityCalculator
from game_theory.common.board_analyzer import BoardAnalyzer
from game_theory.common.range_constructor import RangeConstructor


class BluffingSolver:
    """
    Calculate optimal bluffing frequencies for river spots.

    Based on game theory: opponent must be indifferent to calling.
    """

    def __init__(self):
        self.equity_calc = EquityCalculator()
        self.range_constructor = RangeConstructor()

    def calculate_optimal_frequency(self, pot_size: float, bet_size: float) -> float:
        """
        Calculate theoretical optimal bluff frequency.

        Formula: Optimal_Bluff_Freq = Bet / (Pot + Bet)

        Args:
            pot_size: Current pot size
            bet_size: Size of bet being made

        Returns:
            Optimal bluff frequency (0.0 to 1.0)
        """
        return bet_size / (pot_size + bet_size)

    def calculate_bluff_to_value_ratio(self, pot_size: float, bet_size: float) -> Tuple[int, int]:
        """
        Calculate optimal ratio of bluffs to value bets.

        Args:
            pot_size: Current pot size
            bet_size: Size of bet

        Returns:
            Tuple of (bluffs, value_bets) ratio
        """
        bluff_freq = self.calculate_optimal_frequency(pot_size, bet_size)
        value_freq = 1.0 - bluff_freq

        # Convert to ratio
        # If bluff_freq = 0.33, then ratio is 1:2 (1 bluff per 2 value)
        if value_freq == 0:
            return (1, 0)

        ratio = bluff_freq / value_freq

        # Simplify to simple ratio
        if ratio < 0.25:
            return (1, 4)
        elif ratio < 0.4:
            return (1, 3)
        elif ratio < 0.6:
            return (1, 2)
        elif ratio < 0.8:
            return (3, 4)
        elif ratio < 1.2:
            return (1, 1)
        elif ratio < 1.6:
            return (3, 2)
        else:
            return (2, 1)

    def solve_river_spot(self, board: List[int], pot_size: float,
                        bet_size: float, position: str = "IP") -> Dict:
        """
        Solve a river betting spot.

        Args:
            board: 5 river cards
            pot_size: Current pot size
            bet_size: Proposed bet size
            position: 'IP' (in position) or 'OOP' (out of position)

        Returns:
            Dictionary with:
            - optimal_frequency
            - bluff_to_value_ratio
            - value_range
            - bluff_range
            - recommended_combos
        """
        # Analyze board
        analyzer = BoardAnalyzer(board)

        # Calculate optimal frequency
        optimal_freq = self.calculate_optimal_frequency(pot_size, bet_size)
        bluff_value_ratio = self.calculate_bluff_to_value_ratio(pot_size, bet_size)

        # Construct value range
        # Top 15% of hands typically
        value_range = self.range_constructor.construct_top_percent(15.0)

        # Get number of value combos (after removing board blockers)
        value_combos = value_range.get_combinations(board)

        # Calculate required bluff combos
        bluff_combos_needed = int(value_combos * optimal_freq / (1 - optimal_freq))

        # Find best bluff candidates
        bluff_candidates = self.range_constructor.construct_bluff_candidates(
            board, value_range, num_candidates=min(50, bluff_combos_needed + 10)
        )

        # Build bluff range
        bluff_range = HandRange()
        for hand_str in bluff_candidates[:min(20, bluff_combos_needed // 4)]:
            bluff_range.add_hand(hand_str)

        actual_bluff_combos = bluff_range.get_combinations(board)

        # Calculate actual frequency achieved
        total_combos = value_combos + actual_bluff_combos
        actual_frequency = actual_bluff_combos / total_combos if total_combos > 0 else 0

        return {
            'board_texture': analyzer.texture_category,
            'board_score': analyzer.texture_score,
            'pot_size': pot_size,
            'bet_size': bet_size,
            'bet_percent': (bet_size / pot_size) * 100,
            'optimal_frequency': optimal_freq,
            'bluff_value_ratio': f"{bluff_value_ratio[0]}:{bluff_value_ratio[1]}",
            'value_range': value_range.to_string(),
            'value_combos': value_combos,
            'bluff_range': bluff_range.to_string(),
            'bluff_combos_needed': bluff_combos_needed,
            'bluff_combos_actual': actual_bluff_combos,
            'actual_frequency': actual_frequency,
            'frequency_deviation': abs(actual_frequency - optimal_freq),
            'position': position,
        }

    def analyze_bet_sizing(self, board: List[int], pot_size: float,
                          bet_sizes: List[float] = None) -> List[Dict]:
        """
        Analyze multiple bet sizes for same spot.

        Shows how bluff frequency requirements change with sizing.

        Args:
            board: River board
            pot_size: Current pot
            bet_sizes: List of bet sizes to test (default: [0.33, 0.5, 0.75, 1.0] × pot)

        Returns:
            List of results for each bet size
        """
        if bet_sizes is None:
            bet_sizes = [0.33 * pot_size, 0.5 * pot_size,
                        0.75 * pot_size, 1.0 * pot_size]

        results = []
        for bet_size in bet_sizes:
            result = self.solve_river_spot(board, pot_size, bet_size)
            results.append(result)

        return results

    def calculate_pot_odds_defense(self, pot_size: float, bet_size: float) -> float:
        """
        Calculate minimum defense frequency (MDF) for defender.

        Defender must call with at least this frequency to prevent exploitation.

        Formula: MDF = Pot / (Pot + Bet)

        Args:
            pot_size: Current pot
            bet_size: Bet made

        Returns:
            Minimum defense frequency (0.0 to 1.0)
        """
        return pot_size / (pot_size + bet_size)

    def verify_indifference(self, pot_size: float, bet_size: float,
                           bluff_frequency: float) -> Dict[str, float]:
        """
        Verify that opponent is indifferent to calling at given bluff frequency.

        Args:
            pot_size: Current pot
            bet_size: Bet size
            bluff_frequency: Actual bluff frequency being used

        Returns:
            Dictionary with EV calculations
        """
        # EV of calling with bluff-catcher
        # EV_call = P(bluff) × Pot - P(value) × Bet
        # At optimal frequency, EV_call = 0 (indifferent)

        value_freq = 1.0 - bluff_frequency

        ev_call = bluff_frequency * (pot_size + bet_size) - value_freq * bet_size
        ev_fold = 0.0

        # Should be approximately 0 at optimal frequency
        difference = abs(ev_call - ev_fold)

        return {
            'bluff_frequency': bluff_frequency,
            'ev_call': ev_call,
            'ev_fold': ev_fold,
            'difference': difference,
            'is_indifferent': difference < 0.01,
        }


if __name__ == "__main__":
    print("Testing BluffingSolver...\n")

    solver = BluffingSolver()

    # Test 1: Optimal frequency for different bet sizes
    print("Test 1: Optimal bluff frequencies by bet size")
    print("-" * 60)

    pot = 100.0
    bet_sizes = [25, 33, 50, 75, 100, 150]

    print(f"{'Bet Size':>10} | {'% of Pot':>10} | {'Optimal Freq':>12} | {'Ratio':>8}")
    print("-" * 60)

    for bet in bet_sizes:
        freq = solver.calculate_optimal_frequency(pot, bet)
        ratio = solver.calculate_bluff_to_value_ratio(pot, bet)
        print(f"{bet:>10.0f} | {bet/pot*100:>9.0f}% | {freq:>11.1%} | {ratio[0]:>3}:{ratio[1]:<3}")

    # Test 2: Solve a river spot
    print("\n" + "=" * 60)
    print("Test 2: Solve river spot - Dry board")
    print("=" * 60)

    board1 = [Card.new('Kh'), Card.new('7s'), Card.new('2d'),
              Card.new('9c'), Card.new('4h')]

    result1 = solver.solve_river_spot(board1, pot_size=100.0, bet_size=75.0)

    print(f"Board texture: {result1['board_texture']} (score: {result1['board_score']})")
    print(f"Pot: {result1['pot_size']:.0f}, Bet: {result1['bet_size']:.0f} "
          f"({result1['bet_percent']:.0f}% pot)")
    print(f"Optimal frequency: {result1['optimal_frequency']:.1%}")
    print(f"Bluff:Value ratio: {result1['bluff_value_ratio']}")
    print(f"Value combos: {result1['value_combos']}")
    print(f"Bluff combos needed: {result1['bluff_combos_needed']}")
    print(f"Bluff combos actual: {result1['bluff_combos_actual']}")
    print(f"Actual frequency: {result1['actual_frequency']:.1%}")
    print(f"Deviation: {result1['frequency_deviation']:.3f}")

    # Test 3: Wet board
    print("\n" + "=" * 60)
    print("Test 3: Solve river spot - Wet board")
    print("=" * 60)

    board2 = [Card.new('9h'), Card.new('8h'), Card.new('7d'),
              Card.new('6s'), Card.new('5c')]

    result2 = solver.solve_river_spot(board2, pot_size=100.0, bet_size=75.0)

    print(f"Board texture: {result2['board_texture']} (score: {result2['board_score']})")
    print(f"Optimal frequency: {result2['optimal_frequency']:.1%}")
    print(f"Bluff combos needed: {result2['bluff_combos_needed']}")
    print(f"Bluff combos actual: {result2['bluff_combos_actual']}")
    print(f"Actual frequency: {result2['actual_frequency']:.1%}")

    # Test 4: Verify indifference
    print("\n" + "=" * 60)
    print("Test 4: Verify opponent indifference")
    print("=" * 60)

    verification = solver.verify_indifference(
        pot_size=100.0,
        bet_size=75.0,
        bluff_frequency=0.43  # Should be optimal for 75% pot bet
    )

    print(f"Bluff frequency: {verification['bluff_frequency']:.1%}")
    print(f"EV of calling: {verification['ev_call']:.2f}")
    print(f"EV of folding: {verification['ev_fold']:.2f}")
    print(f"Difference: {verification['difference']:.2f}")
    print(f"Is indifferent: {verification['is_indifferent']}")

    # Test 5: Pot odds defense
    print("\n" + "=" * 60)
    print("Test 5: Minimum defense frequencies")
    print("=" * 60)

    print(f"{'Bet Size':>10} | {'MDF':>12} | {'Can Fold':>12}")
    print("-" * 60)

    for bet in bet_sizes:
        mdf = solver.calculate_pot_odds_defense(pot, bet)
        can_fold = 1.0 - mdf
        print(f"{bet:>10.0f} | {mdf:>11.1%} | {can_fold:>11.1%}")

    print("\n" + "=" * 60)
    print("BluffingSolver tests completed!")
