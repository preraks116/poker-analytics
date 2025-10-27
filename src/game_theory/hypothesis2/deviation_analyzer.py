"""
DeviationAnalyzer: Analyze consequences of deviating from optimal bluff frequencies

Calculates:
- EV loss from over-bluffing
- EV loss from under-bluffing
- Exploitative counter-strategies
- Population tendency adjustments
"""

import sys
from typing import Dict, Tuple

sys.path.append('/home/user/poker-analytics/src')


class DeviationAnalyzer:
    """
    Analyze EV consequences of deviating from optimal bluffing frequencies.

    Key insights:
    - Over-bluffing costs EV (opponent can over-call)
    - Under-bluffing costs EV (opponent can over-fold)
    - Quantify exploitability
    """

    def calculate_overbluff_cost(self, optimal_freq: float, actual_freq: float,
                                 pot_size: float, bet_size: float) -> Dict:
        """
        Calculate EV cost of bluffing too frequently.

        When you over-bluff, opponent can profit by calling more.

        Args:
            optimal_freq: Optimal bluff frequency
            actual_freq: Actual (higher) bluff frequency
            pot_size: Current pot
            bet_size: Bet size

        Returns:
            Dictionary with EV analysis
        """
        if actual_freq <= optimal_freq:
            return {
                'overbluff_amount': 0.0,
                'ev_loss_per_bluff': 0.0,
                'total_ev_loss': 0.0,
                'opponent_exploit_ev': 0.0,
            }

        overbluff_amount = actual_freq - optimal_freq

        # When you over-bluff, each extra bluff loses bet_size when called
        # Opponent will call more frequently
        ev_loss_per_extra_bluff = bet_size

        # Total EV loss proportional to over-bluff amount
        total_ev_loss = overbluff_amount * ev_loss_per_extra_bluff

        # Opponent gains by calling more
        opponent_exploit_ev = total_ev_loss

        return {
            'overbluff_amount': overbluff_amount,
            'ev_loss_per_bluff': ev_loss_per_extra_bluff,
            'total_ev_loss': total_ev_loss,
            'opponent_exploit_ev': opponent_exploit_ev,
            'recommendation': f"Reduce bluff frequency by {overbluff_amount:.1%}",
        }

    def calculate_underbluff_cost(self, optimal_freq: float, actual_freq: float,
                                  pot_size: float, bet_size: float) -> Dict:
        """
        Calculate EV cost of bluffing too infrequently.

        When you under-bluff, opponent can profitably over-fold.

        Args:
            optimal_freq: Optimal bluff frequency
            actual_freq: Actual (lower) bluff frequency
            pot_size: Current pot
            bet_size: Bet size

        Returns:
            Dictionary with EV analysis
        """
        if actual_freq >= optimal_freq:
            return {
                'underbluff_amount': 0.0,
                'ev_loss_per_spot': 0.0,
                'total_ev_loss': 0.0,
                'opponent_exploit_ev': 0.0,
            }

        underbluff_amount = optimal_freq - actual_freq

        # When you under-bluff, opponent can fold more
        # You miss out on fold equity
        # Each missed bluff opportunity costs potential pot win
        ev_loss_per_missed_bluff = pot_size * 0.5  # Simplified

        total_ev_loss = underbluff_amount * ev_loss_per_missed_bluff

        # Opponent gains by folding more
        opponent_exploit_ev = total_ev_loss

        return {
            'underbluff_amount': underbluff_amount,
            'ev_loss_per_spot': ev_loss_per_missed_bluff,
            'total_ev_loss': total_ev_loss,
            'opponent_exploit_ev': opponent_exploit_ev,
            'recommendation': f"Increase bluff frequency by {underbluff_amount:.1%}",
        }

    def calculate_exploitative_adjustment(self, opponent_fold_freq: float,
                                          optimal_fold_freq: float,
                                          pot_size: float,
                                          bet_size: float) -> Dict:
        """
        Calculate optimal adjustment to exploit opponent tendencies.

        If opponent folds too much → bluff more
        If opponent calls too much → bluff less

        Args:
            opponent_fold_freq: How often opponent actually folds
            optimal_fold_freq: How often they should fold at equilibrium
            pot_size: Current pot
            bet_size: Bet size

        Returns:
            Dictionary with adjustment recommendations
        """
        fold_deviation = opponent_fold_freq - optimal_fold_freq

        if abs(fold_deviation) < 0.05:
            return {
                'opponent_tendency': 'balanced',
                'recommended_adjustment': 0.0,
                'expected_ev_gain': 0.0,
                'recommendation': "Opponent playing near-optimally, maintain balanced strategy"
            }

        if fold_deviation > 0:
            # Opponent over-folding → bluff more
            recommended_adjustment = fold_deviation * 0.75  # Adjust 75% of their deviation

            # EV gain from exploiting
            expected_ev_gain = recommended_adjustment * pot_size

            return {
                'opponent_tendency': 'over-folding',
                'fold_deviation': fold_deviation,
                'recommended_adjustment': recommended_adjustment,
                'expected_ev_gain_per_spot': expected_ev_gain,
                'recommendation': f"Opponent folds {fold_deviation:.1%} too often. "
                                f"Increase bluff frequency by {recommended_adjustment:.1%}"
            }
        else:
            # Opponent over-calling → bluff less
            recommended_adjustment = abs(fold_deviation)

            # When they over-call, reduce bluffs and bet value hands more
            expected_ev_gain = recommended_adjustment * bet_size * 0.5

            return {
                'opponent_tendency': 'over-calling',
                'call_deviation': abs(fold_deviation),
                'recommended_adjustment': -recommended_adjustment,
                'expected_ev_gain_per_spot': expected_ev_gain,
                'recommendation': f"Opponent calls {abs(fold_deviation):.1%} too often. "
                                f"Decrease bluff frequency by {recommended_adjustment:.1%}, "
                                f"increase value betting"
            }

    def analyze_population_tendency(self, samples: list) -> Dict:
        """
        Analyze population-level bluffing tendencies.

        Args:
            samples: List of (optimal_freq, actual_freq) tuples from hands

        Returns:
            Population statistics and recommendations
        """
        if not samples:
            return {}

        deviations = [actual - optimal for optimal, actual in samples]

        avg_deviation = sum(deviations) / len(deviations)
        overbluff_count = sum(1 for d in deviations if d > 0.05)
        underbluff_count = sum(1 for d in deviations if d < -0.05)
        balanced_count = len(deviations) - overbluff_count - underbluff_count

        tendency = "balanced"
        if avg_deviation > 0.05:
            tendency = "over-bluffing"
        elif avg_deviation < -0.05:
            tendency = "under-bluffing"

        return {
            'sample_size': len(samples),
            'average_deviation': avg_deviation,
            'tendency': tendency,
            'overbluff_pct': (overbluff_count / len(samples)) * 100,
            'underbluff_pct': (underbluff_count / len(samples)) * 100,
            'balanced_pct': (balanced_count / len(samples)) * 100,
            'recommendation': self._get_population_recommendation(tendency, avg_deviation)
        }

    def _get_population_recommendation(self, tendency: str, avg_deviation: float) -> str:
        """Generate recommendation based on population tendency"""
        if tendency == "over-bluffing":
            return (f"Population over-bluffs by {avg_deviation:.1%} on average. "
                   f"Default strategy: call more, especially with bluff-catchers.")
        elif tendency == "under-bluffing":
            return (f"Population under-bluffs by {abs(avg_deviation):.1%} on average. "
                   f"Default strategy: fold more to river bets with marginal hands.")
        else:
            return "Population plays relatively balanced. Use GTO strategy as baseline."

    def calculate_total_exploitability(self, actual_freq: float, optimal_freq: float,
                                      pot_size: float, bet_size: float) -> float:
        """
        Calculate total exploitability (max EV opponent can gain).

        Args:
            actual_freq: Actual bluff frequency
            optimal_freq: Optimal bluff frequency
            pot_size: Current pot
            bet_size: Bet size

        Returns:
            Maximum EV opponent can gain by best response
        """
        deviation = abs(actual_freq - optimal_freq)

        # Exploitability is proportional to deviation
        # Max exploit is when they perfectly adjust their calling frequency
        max_exploit = deviation * max(pot_size, bet_size)

        return max_exploit


if __name__ == "__main__":
    print("Testing DeviationAnalyzer...\n")

    analyzer = DeviationAnalyzer()

    # Test 1: Over-bluffing cost
    print("Test 1: Cost of over-bluffing")
    print("-" * 60)

    optimal = 0.43  # 43% (optimal for 75% pot bet)
    actual_over = 0.60  # 60% (over-bluffing)

    overbluff = analyzer.calculate_overbluff_cost(optimal, actual_over, 100.0, 75.0)

    print(f"Optimal frequency: {optimal:.1%}")
    print(f"Actual frequency: {actual_over:.1%}")
    print(f"Over-bluff amount: {overbluff['overbluff_amount']:.1%}")
    print(f"EV loss per extra bluff: {overbluff['ev_loss_per_bluff']:.2f}")
    print(f"Total EV loss: {overbluff['total_ev_loss']:.2f}")
    print(f"Recommendation: {overbluff['recommendation']}")

    # Test 2: Under-bluffing cost
    print("\n" + "=" * 60)
    print("Test 2: Cost of under-bluffing")
    print("-" * 60)

    actual_under = 0.25  # 25% (under-bluffing)

    underbluff = analyzer.calculate_underbluff_cost(optimal, actual_under, 100.0, 75.0)

    print(f"Optimal frequency: {optimal:.1%}")
    print(f"Actual frequency: {actual_under:.1%}")
    print(f"Under-bluff amount: {underbluff['underbluff_amount']:.1%}")
    print(f"EV loss per missed bluff: {underbluff['ev_loss_per_spot']:.2f}")
    print(f"Total EV loss: {underbluff['total_ev_loss']:.2f}")
    print(f"Recommendation: {underbluff['recommendation']}")

    # Test 3: Exploitative adjustment
    print("\n" + "=" * 60)
    print("Test 3: Exploitative adjustments")
    print("-" * 60)

    # Scenario A: Opponent over-folds
    print("\nScenario A: Opponent folds 70% (should fold 57%)")
    adjustment_a = analyzer.calculate_exploitative_adjustment(0.70, 0.57, 100.0, 75.0)
    print(f"  Tendency: {adjustment_a['opponent_tendency']}")
    print(f"  Recommended adjustment: {adjustment_a['recommended_adjustment']:.1%}")
    print(f"  Expected EV gain: {adjustment_a['expected_ev_gain_per_spot']:.2f} per spot")
    print(f"  Recommendation: {adjustment_a['recommendation']}")

    # Scenario B: Opponent over-calls
    print("\nScenario B: Opponent folds 40% (should fold 57%)")
    adjustment_b = analyzer.calculate_exploitative_adjustment(0.40, 0.57, 100.0, 75.0)
    print(f"  Tendency: {adjustment_b['opponent_tendency']}")
    print(f"  Recommended adjustment: {adjustment_b['recommended_adjustment']:.1%}")
    print(f"  Expected EV gain: {adjustment_b['expected_ev_gain_per_spot']:.2f} per spot")
    print(f"  Recommendation: {adjustment_b['recommendation']}")

    # Test 4: Population analysis
    print("\n" + "=" * 60)
    print("Test 4: Population tendency analysis")
    print("-" * 60)

    # Simulate population data (optimal_freq, actual_freq)
    samples = [
        (0.43, 0.35),  # Under-bluff
        (0.50, 0.40),  # Under-bluff
        (0.33, 0.30),  # Slight under-bluff
        (0.43, 0.45),  # Balanced
        (0.50, 0.45),  # Under-bluff
        (0.43, 0.38),  # Under-bluff
        (0.33, 0.33),  # Balanced
        (0.50, 0.48),  # Balanced
    ]

    pop_analysis = analyzer.analyze_population_tendency(samples)

    print(f"Sample size: {pop_analysis['sample_size']}")
    print(f"Average deviation: {pop_analysis['average_deviation']:.1%}")
    print(f"Overall tendency: {pop_analysis['tendency']}")
    print(f"Over-bluff %: {pop_analysis['overbluff_pct']:.1f}%")
    print(f"Under-bluff %: {pop_analysis['underbluff_pct']:.1f}%")
    print(f"Balanced %: {pop_analysis['balanced_pct']:.1f}%")
    print(f"\nRecommendation: {pop_analysis['recommendation']}")

    # Test 5: Total exploitability
    print("\n" + "=" * 60)
    print("Test 5: Total exploitability")
    print("-" * 60)

    exploitability = analyzer.calculate_total_exploitability(0.60, 0.43, 100.0, 75.0)
    print(f"Actual frequency: 60%")
    print(f"Optimal frequency: 43%")
    print(f"Total exploitability: {exploitability:.2f} BB")

    print("\n" + "=" * 60)
    print("DeviationAnalyzer tests completed!")
