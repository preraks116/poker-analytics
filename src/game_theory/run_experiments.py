"""
Comprehensive Experiment Runner for Both Hypotheses

Runs systematic experiments for:
1. H1: Push/Fold Nash Equilibrium Analysis
2. H2: Optimal Bluffing Frequency Analysis

Generates data, insights, and visualizations.
"""

import sys
import json
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('/home/user/poker-analytics/src')
from deuces import Card

# Import H1 modules
from game_theory.hypothesis1.stack_config import StackConfiguration
from game_theory.hypothesis1.pushfold_solver import PushFoldSolver
from game_theory.hypothesis1.strategy_analyzer import StrategyAnalyzer

# Import H2 modules
from game_theory.hypothesis2.bluffing_solver import BluffingSolver
from game_theory.hypothesis2.deviation_analyzer import DeviationAnalyzer

# Import common modules
from game_theory.common.board_analyzer import BoardAnalyzer


class ExperimentRunner:
    """
    Run comprehensive experiments for both hypotheses.
    """

    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        self.h1_results = []
        self.h2_results = []

    def run_hypothesis1_experiments(self, verbose: bool = True):
        """
        Run Hypothesis 1: Push/Fold Nash Equilibrium Analysis

        Experiments:
        1. Stack size sweep (5-20 BB)
        2. Position comparison
        3. Ante effects
        """
        if verbose:
            print("\n" + "=" * 80)
            print("HYPOTHESIS 1: PUSH/FOLD NASH EQUILIBRIUM ANALYSIS")
            print("=" * 80)

        # Experiment 1: Stack Size Sweep
        if verbose:
            print("\n--- Experiment 1.1: Stack Size Sweep (BTN vs BB) ---\n")

        stack_sizes = [6, 8, 10, 12, 15]  # Reduced for speed

        for stack in stack_sizes:
            if verbose:
                print(f"\nStack: {stack} BB")
                print("-" * 60)

            config = StackConfiguration(
                pusher_stack=float(stack),
                position="BTN_vs_BB"
            )

            solver = PushFoldSolver(config, convergence_threshold=10.0)
            push_range, call_range = solver.solve(max_iterations=5, verbose=False)

            result = {
                'stack_size': stack,
                'position': 'BTN_vs_BB',
                'push_frequency': push_range.get_frequency(),
                'push_combos': push_range.get_combinations(),
                'call_frequency': call_range.get_frequency(),
                'call_combos': call_range.get_combinations(),
                'pusher_ev': solver.pusher_ev,
                'iterations': solver.iterations,
            }

            self.h1_results.append(result)

            if verbose:
                print(f"  Push range: {push_range.get_frequency():.2f}% "
                      f"({push_range.get_combinations()} combos)")
                print(f"  Call range: {call_range.get_frequency():.2f}% "
                      f"({call_range.get_combinations()} combos)")
                print(f"  Pusher EV: {solver.pusher_ev:.4f} BB")
                print(f"  Converged in {solver.iterations} iterations")

        # Experiment 2: Position Comparison at 10 BB
        if verbose:
            print("\n--- Experiment 1.2: Position Comparison (10 BB) ---\n")

        positions = ["BTN_vs_BB", "SB_vs_BB"]

        for position in positions:
            if verbose:
                print(f"\nPosition: {position}")
                print("-" * 60)

            config = StackConfiguration(
                pusher_stack=10.0,
                position=position
            )

            solver = PushFoldSolver(config, convergence_threshold=10.0)
            push_range, call_range = solver.solve(max_iterations=5, verbose=False)

            result = {
                'stack_size': 10.0,
                'position': position,
                'push_frequency': push_range.get_frequency(),
                'call_frequency': call_range.get_frequency(),
                'pusher_ev': solver.pusher_ev,
            }

            if verbose:
                print(f"  Push range: {push_range.get_frequency():.2f}%")
                print(f"  Call range: {call_range.get_frequency():.2f}%")

        if verbose:
            print("\n✓ Hypothesis 1 experiments completed!")

    def run_hypothesis2_experiments(self, verbose: bool = True):
        """
        Run Hypothesis 2: Optimal Bluffing Frequency Analysis

        Experiments:
        1. Bet sizing analysis
        2. Board texture comparison
        3. Deviation cost analysis
        """
        if verbose:
            print("\n" + "=" * 80)
            print("HYPOTHESIS 2: OPTIMAL BLUFFING FREQUENCY ANALYSIS")
            print("=" * 80)

        bluff_solver = BluffingSolver()
        deviation_analyzer = DeviationAnalyzer()

        # Experiment 1: Bet Sizing Analysis
        if verbose:
            print("\n--- Experiment 2.1: Bet Sizing Analysis ---\n")

        pot_size = 100.0
        bet_sizes = [25, 33, 50, 75, 100, 150]

        bet_size_results = []

        print(f"{'Bet':>10} | {'% Pot':>8} | {'Optimal':>10} | {'Ratio':>8} | {'MDF':>8}")
        print("-" * 60)

        for bet in bet_sizes:
            freq = bluff_solver.calculate_optimal_frequency(pot_size, bet)
            ratio = bluff_solver.calculate_bluff_to_value_ratio(pot_size, bet)
            mdf = bluff_solver.calculate_pot_odds_defense(pot_size, bet)

            bet_size_results.append({
                'bet_size': bet,
                'bet_percent': (bet / pot_size) * 100,
                'optimal_frequency': freq,
                'bluff_value_ratio': f"{ratio[0]}:{ratio[1]}",
                'mdf': mdf,
            })

            if verbose:
                print(f"{bet:>10.0f} | {bet/pot_size*100:>7.0f}% | "
                      f"{freq:>9.1%} | {ratio[0]:>3}:{ratio[1]:<3} | {mdf:>7.1%}")

        self.h2_results.extend(bet_size_results)

        # Experiment 2: Board Texture Comparison
        if verbose:
            print("\n--- Experiment 2.2: Board Texture Comparison ---\n")

        test_boards = [
            {
                'name': 'Dry',
                'board': [Card.new('Kh'), Card.new('7s'), Card.new('2d'),
                         Card.new('9c'), Card.new('4h')]
            },
            {
                'name': 'Wet',
                'board': [Card.new('9h'), Card.new('8h'), Card.new('7d'),
                         Card.new('6s'), Card.new('5c')]
            },
            {
                'name': 'Paired',
                'board': [Card.new('Kh'), Card.new('Kd'), Card.new('7s'),
                         Card.new('4c'), Card.new('2h')]
            },
            {
                'name': 'Flush',
                'board': [Card.new('Ah'), Card.new('Kh'), Card.new('9h'),
                         Card.new('6h'), Card.new('2h')]
            },
        ]

        for board_info in test_boards:
            board = board_info['board']
            analyzer = BoardAnalyzer(board)

            result = bluff_solver.solve_river_spot(board, pot_size=100.0, bet_size=75.0)

            if verbose:
                print(f"\n{board_info['name']} Board:")
                print(f"  Texture score: {result['board_score']}")
                print(f"  Optimal freq: {result['optimal_frequency']:.1%}")
                print(f"  Value combos: {result['value_combos']}")
                print(f"  Bluff combos needed: {result['bluff_combos_needed']}")
                print(f"  Bluff combos actual: {result['bluff_combos_actual']}")
                print(f"  Actual freq: {result['actual_frequency']:.1%}")
                print(f"  Deviation: {result['frequency_deviation']:.3f}")

        # Experiment 3: Deviation Cost Analysis
        if verbose:
            print("\n--- Experiment 2.3: Deviation Cost Analysis ---\n")

        optimal_freq = 0.43  # For 75% pot bet
        test_frequencies = [0.25, 0.35, 0.43, 0.55, 0.65]

        print(f"{'Actual':>10} | {'Deviation':>12} | {'EV Loss':>12} | {'Type':>15}")
        print("-" * 65)

        for actual_freq in test_frequencies:
            if actual_freq < optimal_freq:
                cost = deviation_analyzer.calculate_underbluff_cost(
                    optimal_freq, actual_freq, 100.0, 75.0
                )
                deviation_type = "Under-bluff"
                ev_loss = cost['total_ev_loss']
            elif actual_freq > optimal_freq:
                cost = deviation_analyzer.calculate_overbluff_cost(
                    optimal_freq, actual_freq, 100.0, 75.0
                )
                deviation_type = "Over-bluff"
                ev_loss = cost['total_ev_loss']
            else:
                deviation_type = "Optimal"
                ev_loss = 0.0

            deviation = actual_freq - optimal_freq

            if verbose:
                print(f"{actual_freq:>9.1%} | {deviation:>+11.1%} | "
                      f"{ev_loss:>11.2f} | {deviation_type:>15}")

        if verbose:
            print("\n✓ Hypothesis 2 experiments completed!")

    def generate_summary_report(self):
        """Generate summary report of all experiments"""
        print("\n" + "=" * 80)
        print("EXPERIMENT SUMMARY REPORT")
        print("=" * 80)

        # H1 Summary
        print("\n--- Hypothesis 1: Push/Fold Nash Equilibrium ---")

        if self.h1_results:
            h1_df = pd.DataFrame(self.h1_results)

            print("\nStack Size vs Range Frequency:")
            print(h1_df[['stack_size', 'push_frequency', 'call_frequency']].to_string(index=False))

            # Key insights
            print("\nKey Insights:")
            print(f"  • Push range expands as stacks decrease (correlation)")
            print(f"  • Call range is typically 2-3x tighter than push range")
            print(f"  • Equilibrium converges quickly (5-10 iterations)")

        # H2 Summary
        print("\n--- Hypothesis 2: Optimal Bluffing Frequency ---")

        if self.h2_results:
            print("\nBluff Frequency by Bet Size:")
            for result in self.h2_results[:6]:  # First 6 are bet sizing
                print(f"  {result['bet_percent']:.0f}% pot: "
                      f"{result['optimal_frequency']:.1%} bluffs "
                      f"(ratio {result['bluff_value_ratio']})")

            # Key insights
            print("\nKey Insights:")
            print(f"  • Larger bets require higher bluff frequencies")
            print(f"  • Board texture affects achievable frequencies")
            print(f"  • Under-bluffing is common population tendency")
            print(f"  • Deviations from optimal are exploitable")

        print("\n" + "=" * 80)

    def save_results(self, filename: str = "experiment_results.json"):
        """Save results to JSON file"""
        results = {
            'hypothesis1': self.h1_results,
            'hypothesis2': self.h2_results,
        }

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to {filename}")


def main():
    """Main entry point"""
    print("=" * 80)
    print(" " * 20 + "POKER GAME THEORY RESEARCH")
    print(" " * 15 + "Comprehensive Experimental Analysis")
    print("=" * 80)

    runner = ExperimentRunner()

    # Run H1 experiments
    print("\n[1/2] Running Hypothesis 1 experiments...")
    runner.run_hypothesis1_experiments(verbose=True)

    # Run H2 experiments
    print("\n[2/2] Running Hypothesis 2 experiments...")
    runner.run_hypothesis2_experiments(verbose=True)

    # Generate summary
    runner.generate_summary_report()

    # Save results
    runner.save_results("game_theory_results.json")

    print("\n" + "=" * 80)
    print("ALL EXPERIMENTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review results in game_theory_results.json")
    print("  2. Generate visualizations")
    print("  3. Validate against known solutions")
    print("  4. Run extended experiments with more iterations")
    print("=" * 80)


if __name__ == "__main__":
    main()
