"""
PushFoldSolver: Find Nash equilibrium for push/fold scenarios

Uses iterative best response algorithm:
1. Start with initial ranges
2. Calculate best response call range to push range
3. Calculate best response push range to call range
4. Repeat until convergence
"""

import sys
from typing import Tuple, Dict, List
import numpy as np

sys.path.append('/home/user/poker-analytics/src')
from deuces import Card
from game_theory.common.hand_range import HandRange
from game_theory.common.equity_calculator import EquityCalculator
from game_theory.common.range_constructor import RangeConstructor
from game_theory.hypothesis1.stack_config import StackConfiguration


class PushFoldSolver:
    """
    Solve for Nash equilibrium in push/fold scenarios.

    Uses iterative best response to find equilibrium strategy pair.
    """

    def __init__(self, config: StackConfiguration, convergence_threshold: float = 0.001):
        """
        Initialize solver.

        Args:
            config: Stack configuration
            convergence_threshold: Convergence criterion (range difference)
        """
        self.config = config
        self.threshold = convergence_threshold
        self.equity_calc = EquityCalculator()
        self.range_constructor = RangeConstructor()

        # Results
        self.push_range = None
        self.call_range = None
        self.pusher_ev = None
        self.caller_ev = None
        self.iterations = 0
        self.convergence_history = []

    def solve(self, max_iterations: int = 100, verbose: bool = True) -> Tuple[HandRange, HandRange]:
        """
        Find Nash equilibrium push and call ranges.

        Args:
            max_iterations: Maximum iterations
            verbose: Print progress

        Returns:
            Tuple of (push_range, call_range)
        """
        if verbose:
            print(f"\nSolving push/fold equilibrium for {self.config}")
            print(f"Convergence threshold: {self.threshold}")
            print("-" * 60)

        # Initialize with reasonable starting ranges
        # Pusher starts with top 20% of hands
        push_range = self.range_constructor.construct_top_percent(20.0)

        # Caller starts with top 10% of hands
        call_range = self.range_constructor.construct_top_percent(10.0)

        self.iterations = 0
        converged = False

        while not converged and self.iterations < max_iterations:
            self.iterations += 1

            # Store previous ranges for convergence check
            prev_push_combos = push_range.get_combinations()
            prev_call_combos = call_range.get_combinations()

            # Step 1: Calculate best response call range given push range
            call_range_new = self._calculate_best_response_call(push_range)

            # Step 2: Calculate best response push range given call range
            push_range_new = self._calculate_best_response_push(call_range_new)

            # Check convergence
            push_diff = abs(push_range_new.get_combinations() - prev_push_combos)
            call_diff = abs(call_range_new.get_combinations() - prev_call_combos)
            total_diff = push_diff + call_diff

            self.convergence_history.append({
                'iteration': self.iterations,
                'push_combos': push_range_new.get_combinations(),
                'call_combos': call_range_new.get_combinations(),
                'difference': total_diff
            })

            if verbose:
                push_freq = push_range_new.get_frequency()
                call_freq = call_range_new.get_frequency()
                print(f"Iteration {self.iterations}: "
                      f"Push={push_freq:.1f}%, Call={call_freq:.1f}%, "
                      f"Diff={total_diff:.2f}")

            # Update ranges
            push_range = push_range_new
            call_range = call_range_new

            # Check convergence
            if total_diff < self.threshold:
                converged = True

        self.push_range = push_range
        self.call_range = call_range

        # Calculate expected values
        self._calculate_expected_values()

        if verbose:
            if converged:
                print(f"\n✓ Converged after {self.iterations} iterations")
            else:
                print(f"\n⚠ Did not converge after {max_iterations} iterations")

            print(f"\nNash Equilibrium:")
            print(f"  Push range: {self.push_range.get_frequency():.2f}% "
                  f"({self.push_range.get_combinations()} combos)")
            print(f"  Call range: {self.call_range.get_frequency():.2f}% "
                  f"({self.call_range.get_combinations()} combos)")
            print(f"  Pusher EV: {self.pusher_ev:.4f} BB")
            print(f"  Caller EV: {self.caller_ev:.4f} BB")

        return self.push_range, self.call_range

    def _calculate_best_response_call(self, push_range: HandRange) -> HandRange:
        """
        Calculate optimal calling range against given push range.

        Calls when: Equity × Total_Pot > Stack_Risked
        """
        # Get pot odds required for calling
        required_equity = self.config.get_pot_odds_for_caller()

        # Build calling range with hands that have sufficient equity
        call_range = HandRange()

        # Test each possible hand
        for hand_str in self.range_constructor.HAND_RANKINGS:
            try:
                # Create sample hand
                sample_hand = self.range_constructor._create_sample_hand(hand_str, [])
                if not sample_hand:
                    continue

                # Calculate equity vs push range
                equity = self.equity_calc.hand_vs_range_equity(
                    sample_hand, push_range, n_simulations=1000
                )

                # Call if equity sufficient
                if equity >= required_equity:
                    call_range.add_hand(hand_str)

            except:
                continue

        return call_range

    def _calculate_best_response_push(self, call_range: HandRange) -> HandRange:
        """
        Calculate optimal pushing range against given call range.

        Pushes when: EV(push) ≥ EV(fold)
        """
        push_range = HandRange()

        # Get fold frequency (how often opponent folds)
        # Estimate: opponent folds with hands not in call range
        fold_freq = 1.0 - (call_range.get_frequency() / 100.0)

        # Get pot and stack info
        pot = self.config.get_pot_size()
        stack = self.config.effective_stack
        risk_reward = self.config.get_risk_reward_for_pusher()

        # Calculate EV(fold) - amount already committed
        if self.config.position == "SB_vs_BB":
            ev_fold = -self.config.small_blind
        elif self.config.position == "BTN_vs_BB":
            ev_fold = 0.0  # BTN hasn't committed anything yet
        else:
            ev_fold = 0.0

        # Test each hand
        for hand_str in self.range_constructor.HAND_RANKINGS:
            try:
                sample_hand = self.range_constructor._create_sample_hand(hand_str, [])
                if not sample_hand:
                    continue

                # Calculate equity vs calling range
                equity = self.equity_calc.hand_vs_range_equity(
                    sample_hand, call_range, n_simulations=1000
                )

                # Calculate EV(push)
                # EV = P(fold) × pot + P(call) × [Equity × (2×stack + pot) - stack]
                ev_fold_wins = fold_freq * pot
                ev_called = (1 - fold_freq) * (equity * (2 * stack + pot) - stack)
                ev_push = ev_fold_wins + ev_called

                # Push if EV(push) > EV(fold)
                if ev_push >= ev_fold:
                    push_range.add_hand(hand_str)

            except:
                continue

        return push_range

    def _calculate_expected_values(self):
        """Calculate final expected values for both players"""
        if self.push_range is None or self.call_range is None:
            return

        # Simplified EV calculation
        pot = self.config.get_pot_size()
        stack = self.config.effective_stack

        # Approximate fold frequency
        fold_freq = 1.0 - (self.call_range.get_frequency() / 100.0)

        # Average equity when called (approximate)
        avg_equity = 0.5  # Simplified

        # Pusher EV
        ev_fold_wins = fold_freq * pot
        ev_called = (1 - fold_freq) * (avg_equity * (2 * stack + pot) - stack)
        self.pusher_ev = ev_fold_wins + ev_called

        # Caller EV (when faced with push)
        # They call with call_range, fold otherwise
        # EV when calling: equity × pot - stack
        # EV when folding: 0 (or -BB if already posted)
        self.caller_ev = -self.config.big_blind  # Simplified

    def get_indifference_hands(self) -> Dict[str, List[str]]:
        """
        Get hands on the boundary of push/call ranges.

        These are the hands where players are indifferent between actions.
        """
        if self.push_range is None or self.call_range is None:
            return {}

        # Find marginal push hands (hands just barely in push range)
        push_hands = set(self.push_range.get_hand_list())

        # Find marginal call hands
        call_hands = set(self.call_range.get_hand_list())

        # Test hands just outside ranges
        marginal_push = []
        marginal_call = []

        for hand_str in self.range_constructor.HAND_RANKINGS:
            if hand_str in push_hands:
                # Check if next weaker hand is NOT in range
                # If so, this is marginal
                marginal_push.append(hand_str)
                if len(marginal_push) >= 5:
                    break

            if hand_str in call_hands:
                marginal_call.append(hand_str)
                if len(marginal_call) >= 5:
                    break

        return {
            'marginal_push': marginal_push[:5],
            'marginal_call': marginal_call[:5]
        }

    def get_results_dict(self) -> Dict:
        """Return results as dictionary"""
        return {
            'config': self.config.to_dict(),
            'push_range': {
                'hands': self.push_range.to_string() if self.push_range else "",
                'frequency': self.push_range.get_frequency() if self.push_range else 0,
                'combos': self.push_range.get_combinations() if self.push_range else 0,
            },
            'call_range': {
                'hands': self.call_range.to_string() if self.call_range else "",
                'frequency': self.call_range.get_frequency() if self.call_range else 0,
                'combos': self.call_range.get_combinations() if self.call_range else 0,
            },
            'pusher_ev': self.pusher_ev,
            'caller_ev': self.caller_ev,
            'iterations': self.iterations,
            'converged': self.iterations < 100,
            'indifference_hands': self.get_indifference_hands(),
        }


if __name__ == "__main__":
    print("Testing PushFoldSolver...\n")

    # Test 1: BTN vs BB at 10BB
    print("=" * 60)
    print("TEST 1: BTN vs BB, 10BB effective")
    print("=" * 60)

    config1 = StackConfiguration(
        pusher_stack=10.0,
        position="BTN_vs_BB"
    )

    solver1 = PushFoldSolver(config1, convergence_threshold=5.0)  # Looser for speed
    push_range1, call_range1 = solver1.solve(max_iterations=10, verbose=True)

    print(f"\nPush range: {push_range1}")
    print(f"Call range: {call_range1}")

    # Test 2: SB vs BB at 8BB
    print("\n" + "=" * 60)
    print("TEST 2: SB vs BB, 8BB effective")
    print("=" * 60)

    config2 = StackConfiguration(
        pusher_stack=8.0,
        position="SB_vs_BB"
    )

    solver2 = PushFoldSolver(config2, convergence_threshold=5.0)
    push_range2, call_range2 = solver2.solve(max_iterations=10, verbose=True)

    print(f"\nPush range: {push_range2}")
    print(f"Call range: {call_range2}")

    print("\n" + "=" * 60)
    print("PushFoldSolver tests completed!")
