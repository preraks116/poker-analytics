"""
StrategyAnalyzer: Analyze and validate push/fold strategies

Provides:
- Exploitability measurement
- Deviation cost analysis
- Comparison to known solutions
- Sensitivity analysis
"""

import sys
from typing import Dict, Tuple
import numpy as np

sys.path.append('/home/user/poker-analytics/src')
from game_theory.common.hand_range import HandRange
from game_theory.common.equity_calculator import EquityCalculator
from game_theory.hypothesis1.stack_config import StackConfiguration


class StrategyAnalyzer:
    """
    Analyze properties of push/fold strategies.

    Key metrics:
    - Exploitability
    - Deviation costs
    - Strategy robustness
    """

    def __init__(self):
        self.equity_calc = EquityCalculator()

    def calculate_exploitability(self, push_range: HandRange,
                                 call_range: HandRange,
                                 config: StackConfiguration) -> float:
        """
        Calculate maximum EV an opponent can gain by deviating.

        Exploitability = max(EV_best_response) - EV_equilibrium

        Args:
            push_range: Equilibrium push range
            call_range: Equilibrium call range
            config: Stack configuration

        Returns:
            Exploitability in BB
        """
        # Simplified exploitability measure
        # In practice, would calculate exact best responses

        # Check if ranges are reasonable
        push_freq = push_range.get_frequency()
        call_freq = call_range.get_frequency()

        # Heuristic: exploitability increases with imbalance
        exploitability = abs(push_freq - call_freq * 2.0) / 100.0

        return exploitability

    def measure_deviation_cost(self, equilibrium_push: HandRange,
                              equilibrium_call: HandRange,
                              test_push: HandRange,
                              test_call: HandRange,
                              config: StackConfiguration) -> Dict[str, float]:
        """
        Measure EV cost of deviating from equilibrium.

        Args:
            equilibrium_push/call: Equilibrium ranges
            test_push/call: Test ranges (deviations)
            config: Stack configuration

        Returns:
            Dictionary with EV losses for both players
        """
        # Calculate EV difference
        # Simplified: based on frequency differences

        push_diff = abs(test_push.get_frequency() - equilibrium_push.get_frequency())
        call_diff = abs(test_call.get_frequency() - equilibrium_call.get_frequency())

        # Estimate EV loss
        pusher_loss = push_diff * 0.01  # Simplified
        caller_loss = call_diff * 0.01

        return {
            'pusher_ev_loss': pusher_loss,
            'caller_ev_loss': caller_loss,
            'total_loss': pusher_loss + caller_loss
        }

    def analyze_range_properties(self, hand_range: HandRange) -> Dict:
        """
        Analyze properties of a range.

        Returns statistics about range composition.
        """
        hands = hand_range.get_hand_list()

        # Count hand types
        pairs = sum(1 for h in hands if len(h) == 2 and h[0] == h[1])
        suited = sum(1 for h in hands if h.endswith('S'))
        offsuit = sum(1 for h in hands if h.endswith('O'))

        # High cards
        premium = sum(1 for h in hands if h[0] in ['A', 'K', 'Q'])

        return {
            'total_hands': len(hands),
            'frequency': hand_range.get_frequency(),
            'combinations': hand_range.get_combinations(),
            'pairs': pairs,
            'suited': suited,
            'offsuit': offsuit,
            'premium_hands': premium,
        }

    def compare_strategies(self, strategy1: Tuple[HandRange, HandRange],
                          strategy2: Tuple[HandRange, HandRange]) -> Dict:
        """
        Compare two strategy pairs.

        Returns differences and overlap metrics.
        """
        push1, call1 = strategy1
        push2, call2 = strategy2

        # Calculate overlaps
        push_overlap = push1.intersection(push2)
        call_overlap = call1.intersection(call2)

        # Calculate differences
        push_diff = abs(push1.get_frequency() - push2.get_frequency())
        call_diff = abs(call1.get_frequency() - call2.get_frequency())

        return {
            'push_overlap': push_overlap.get_frequency(),
            'call_overlap': call_overlap.get_frequency(),
            'push_frequency_diff': push_diff,
            'call_frequency_diff': call_diff,
            'total_difference': push_diff + call_diff,
        }

    def sensitivity_analysis(self, base_config: StackConfiguration,
                            base_push: HandRange,
                            base_call: HandRange,
                            stack_variations: list = None) -> Dict:
        """
        Analyze how strategy changes with stack size variations.

        Args:
            base_config: Base configuration
            base_push/call: Base equilibrium ranges
            stack_variations: List of stack size adjustments (e.g., [-1, -0.5, +0.5, +1])

        Returns:
            Dictionary with sensitivity metrics
        """
        if stack_variations is None:
            stack_variations = [-1.0, -0.5, +0.5, +1.0]

        results = []

        for variation in stack_variations:
            new_stack = base_config.pusher_stack + variation

            if new_stack <= 0:
                continue

            # Create new config
            new_config = StackConfiguration(
                pusher_stack=new_stack,
                position=base_config.position
            )

            results.append({
                'stack_size': new_stack,
                'variation': variation,
                # Would solve for new equilibrium here
                # For now, just record config
                'config': new_config.to_dict()
            })

        return {
            'base_stack': base_config.pusher_stack,
            'variations': results
        }


if __name__ == "__main__":
    print("Testing StrategyAnalyzer...\n")

    analyzer = StrategyAnalyzer()

    # Test 1: Analyze range properties
    test_range = HandRange()
    test_range.add_hand_range("77+, AJ+, KQ")

    print("Test 1: Analyze range properties")
    props = analyzer.analyze_range_properties(test_range)
    print(f"  Range: {test_range}")
    print(f"  Properties: {props}")
    print()

    # Test 2: Compare strategies
    push1 = HandRange()
    push1.add_hand_range("77+, AT+, KJ+")
    call1 = HandRange()
    call1.add_hand_range("99+, AQ+")

    push2 = HandRange()
    push2.add_hand_range("88+, AT+, KQ+")
    call2 = HandRange()
    call2.add_hand_range("TT+, AK")

    print("Test 2: Compare two strategies")
    comparison = analyzer.compare_strategies((push1, call1), (push2, call2))
    print(f"  Strategy 1: Push={push1.get_frequency():.1f}%, Call={call1.get_frequency():.1f}%")
    print(f"  Strategy 2: Push={push2.get_frequency():.1f}%, Call={call2.get_frequency():.1f}%")
    print(f"  Comparison: {comparison}")
    print()

    # Test 3: Exploitability
    config = StackConfiguration(pusher_stack=10.0)
    exploitability = analyzer.calculate_exploitability(push1, call1, config)
    print(f"Test 3: Exploitability = {exploitability:.4f} BB")
    print()

    print("StrategyAnalyzer tests completed!")
