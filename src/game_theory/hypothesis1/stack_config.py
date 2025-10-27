"""
StackConfiguration: Define push/fold scenarios

Specifies:
- Stack sizes
- Blind structure
- Position
- Ante (if any)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StackConfiguration:
    """
    Configuration for a push/fold scenario.

    All sizes in big blinds (BB).
    """

    # Stack sizes
    pusher_stack: float  # Effective stack for pusher
    caller_stack: Optional[float] = None  # If different, else uses pusher_stack

    # Blinds and antes
    small_blind: float = 0.5
    big_blind: float = 1.0
    ante: float = 0.0

    # Position
    position: str = "BTN_vs_BB"  # BTN_vs_BB, SB_vs_BB, etc.

    def __post_init__(self):
        """Set defaults and validate"""
        if self.caller_stack is None:
            self.caller_stack = self.pusher_stack

        # Validate
        if self.pusher_stack <= 0 or self.caller_stack <= 0:
            raise ValueError("Stack sizes must be positive")

        if self.big_blind <= 0:
            raise ValueError("Big blind must be positive")

    @property
    def effective_stack(self) -> float:
        """Return the smaller of the two stacks"""
        return min(self.pusher_stack, self.caller_stack)

    def get_pot_size(self) -> float:
        """Calculate starting pot size"""
        pot = 0.0

        if self.position == "SB_vs_BB":
            # SB already posted, BB in pot
            pot = self.small_blind + self.big_blind
        elif self.position == "BTN_vs_BB":
            # Blinds both posted
            pot = self.small_blind + self.big_blind
        elif self.position == "BTN_vs_SB_BB":
            # 3-way
            pot = self.small_blind + self.big_blind
        else:
            # Default: assume SB + BB
            pot = self.small_blind + self.big_blind

        # Add antes if present
        players_in_hand = 2  # Simplified
        if self.ante > 0:
            pot += self.ante * players_in_hand

        return pot

    def get_pot_odds_for_caller(self) -> float:
        """
        Calculate pot odds the caller is getting.

        Pot odds = amount to call / (pot after call)
        """
        pot = self.get_pot_size()

        if self.position == "SB_vs_BB":
            # BB has already posted 1 BB, needs to call (stack - 1) more
            to_call = self.effective_stack - self.big_blind
        elif self.position == "BTN_vs_BB":
            # BB has posted 1 BB, needs to call (stack - 1) more
            to_call = self.effective_stack - self.big_blind
        else:
            to_call = self.effective_stack - self.big_blind

        pot_after_call = pot + 2 * self.effective_stack

        if to_call <= 0:
            return 0.0

        pot_odds = to_call / pot_after_call
        return pot_odds

    def get_risk_reward_for_pusher(self) -> dict:
        """
        Calculate risk/reward for pusher.

        Returns:
            dict with 'risk' (amount at risk) and 'reward' (pot to win immediately)
        """
        pot = self.get_pot_size()

        if self.position == "SB_vs_BB":
            # SB has posted 0.5 BB, risks (stack - 0.5) more
            risk = self.effective_stack - self.small_blind
        elif self.position == "BTN_vs_BB":
            # BTN risks full stack
            risk = self.effective_stack
        else:
            risk = self.effective_stack

        # Reward is pot if opponent folds
        reward = pot

        return {
            'risk': risk,
            'reward': reward,
            'ratio': reward / risk if risk > 0 else 0.0
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'pusher_stack': self.pusher_stack,
            'caller_stack': self.caller_stack,
            'small_blind': self.small_blind,
            'big_blind': self.big_blind,
            'ante': self.ante,
            'position': self.position,
            'effective_stack': self.effective_stack,
            'pot_size': self.get_pot_size(),
            'pot_odds': self.get_pot_odds_for_caller(),
        }

    def __repr__(self) -> str:
        return (f"StackConfig({self.position}, "
                f"stack={self.effective_stack:.1f}BB, "
                f"pot={self.get_pot_size():.1f}BB)")


if __name__ == "__main__":
    print("Testing StackConfiguration...\n")

    # Test 1: Standard BTN vs BB at 10BB
    config1 = StackConfiguration(
        pusher_stack=10.0,
        position="BTN_vs_BB"
    )
    print("Test 1: BTN vs BB, 10BB effective")
    print(f"  Config: {config1}")
    print(f"  Pot size: {config1.get_pot_size():.2f} BB")
    print(f"  Pot odds for caller: {config1.get_pot_odds_for_caller():.3f}")
    print(f"  Risk/Reward: {config1.get_risk_reward_for_pusher()}")
    print()

    # Test 2: SB vs BB at 8BB
    config2 = StackConfiguration(
        pusher_stack=8.0,
        position="SB_vs_BB"
    )
    print("Test 2: SB vs BB, 8BB effective")
    print(f"  Config: {config2}")
    print(f"  Pot size: {config2.get_pot_size():.2f} BB")
    print(f"  Pot odds for caller: {config2.get_pot_odds_for_caller():.3f}")
    print(f"  Risk/Reward: {config2.get_risk_reward_for_pusher()}")
    print()

    # Test 3: With antes
    config3 = StackConfiguration(
        pusher_stack=12.0,
        ante=0.1,
        position="BTN_vs_BB"
    )
    print("Test 3: BTN vs BB, 12BB with antes (0.1 BB)")
    print(f"  Config: {config3}")
    print(f"  Pot size: {config3.get_pot_size():.2f} BB")
    print(f"  Pot odds for caller: {config3.get_pot_odds_for_caller():.3f}")
    print()

    # Test 4: Different stack sizes
    config4 = StackConfiguration(
        pusher_stack=15.0,
        caller_stack=12.0,
        position="BTN_vs_BB"
    )
    print("Test 4: BTN (15BB) vs BB (12BB)")
    print(f"  Config: {config4}")
    print(f"  Effective stack: {config4.effective_stack:.1f} BB")
    print(f"  Pot odds for caller: {config4.get_pot_odds_for_caller():.3f}")
    print()

    print("StackConfiguration tests completed!")
