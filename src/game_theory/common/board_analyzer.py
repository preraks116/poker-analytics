"""
BoardAnalyzer: Classify and analyze poker board textures

Provides texture classification essential for:
- H1: Understanding push/fold scenarios by board type
- H2: Optimal bluffing frequency based on texture
"""

import sys
from typing import List, Dict, Tuple, Set
from collections import Counter

sys.path.append('/home/user/poker-analytics/src')
from deuces import Card, Evaluator


class BoardAnalyzer:
    """
    Analyze poker board textures and properties.

    Classifications:
    - Dry/Medium/Wet based on connectivity
    - Flush possibilities
    - Straight possibilities
    - Paired/unpaired boards
    - High card strength
    """

    # Rank values for analysis
    RANK_VALUES = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6,
                   '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12}

    BROADWAY_CARDS = {'T', 'J', 'Q', 'K', 'A'}

    def __init__(self, board: List[int]):
        """
        Initialize analyzer with a board.

        Args:
            board: List of card integers (3-5 cards)
        """
        self.board = board
        self.evaluator = Evaluator()

        # Parse board properties
        self.ranks = []
        self.suits = []

        for card_int in board:
            rank_int = Card.get_rank_int(card_int)
            suit_int = Card.get_suit_int(card_int)

            # Convert to string representation
            rank_str = Card.STR_RANKS[rank_int]
            self.ranks.append(rank_str)
            self.suits.append(suit_int)

        # Analyze board
        self._analyze()

    def _analyze(self):
        """Perform comprehensive board analysis"""
        self.rank_counts = Counter(self.ranks)
        self.suit_counts = Counter(self.suits)

        # Basic properties
        self.is_paired = max(self.rank_counts.values()) >= 2
        self.is_trips = max(self.rank_counts.values()) >= 3
        self.has_flush = max(self.suit_counts.values()) >= 5
        self.has_flush_draw = max(self.suit_counts.values()) >= 4 if len(self.board) < 5 else False

        # Calculate texture score
        self.texture_score = self._calculate_texture_score()
        self.texture_category = self._categorize_texture()

        # Connectivity
        self.connectivity_score = self._calculate_connectivity()
        self.straight_possibilities = self._count_straight_possibilities()

        # High cards
        self.broadway_count = sum(1 for r in self.ranks if r in self.BROADWAY_CARDS)

    def _calculate_texture_score(self) -> int:
        """
        Calculate texture score (0-10).

        Higher score = wetter board
        """
        score = 0

        # Flush considerations (+3)
        if self.has_flush:
            score += 3
        elif self.has_flush_draw:
            score += 2

        # Straight considerations (+2)
        straight_poss = self._count_straight_possibilities()
        if straight_poss > 0:
            score += min(2, straight_poss)

        # Connectivity (+1-2)
        connectivity = self._calculate_connectivity()
        score += min(2, connectivity // 2)

        # Paired boards (-2)
        if self.is_paired:
            score -= 2
        if self.is_trips:
            score -= 1

        # Unpaired adds wetness (+1)
        if not self.is_paired and len(self.board) >= 3:
            score += 1

        return max(0, min(10, score))

    def _calculate_connectivity(self) -> int:
        """
        Calculate how connected the board ranks are.

        Returns count of ranks within 2 of each other.
        """
        if len(self.ranks) < 2:
            return 0

        rank_values = sorted([self.RANK_VALUES[r] for r in self.ranks])

        connected_count = 0
        for i in range(len(rank_values) - 1):
            if rank_values[i+1] - rank_values[i] <= 2:
                connected_count += 1

        # Check for wheel (A-5 straight)
        if 'A' in self.ranks and '2' in self.ranks:
            connected_count += 1

        return connected_count

    def _count_straight_possibilities(self) -> int:
        """
        Count possible straight combinations on this board.

        Returns number of different straight types possible.
        """
        rank_values = sorted([self.RANK_VALUES[r] for r in set(self.ranks)])

        straight_count = 0

        # Check standard straights
        for start in range(13 - 4):
            end = start + 5
            needed = set(range(start, end))
            have = set(rank_values)

            # Need at least 3 cards for a straight possibility
            if len(needed & have) >= 3:
                straight_count += 1

        # Check wheel (A-2-3-4-5)
        wheel_values = {0, 1, 2, 3, 12}  # 2,3,4,5,A
        if len(wheel_values & set(rank_values)) >= 3:
            straight_count += 1

        return straight_count

    def _categorize_texture(self) -> str:
        """
        Categorize board as dry, medium, or wet.

        Based on texture score:
        - 0-3: Dry
        - 4-6: Medium
        - 7-10: Wet
        """
        if self.texture_score <= 3:
            return 'dry'
        elif self.texture_score <= 6:
            return 'medium'
        else:
            return 'wet'

    def is_monotone(self) -> bool:
        """Check if board is all same suit"""
        return max(self.suit_counts.values()) >= 3

    def is_two_tone(self) -> bool:
        """Check if board has two dominant suits"""
        sorted_counts = sorted(self.suit_counts.values(), reverse=True)
        return len(sorted_counts) >= 2 and sorted_counts[0] + sorted_counts[1] >= len(self.board)

    def is_rainbow(self) -> bool:
        """Check if board has 3+ different suits"""
        return len(self.suit_counts) >= 3

    def get_highest_rank(self) -> str:
        """Return highest rank on board"""
        rank_values = [self.RANK_VALUES[r] for r in self.ranks]
        highest_idx = max(rank_values)

        for rank, value in self.RANK_VALUES.items():
            if value == highest_idx:
                return rank
        return 'A'

    def get_possible_hands(self) -> List[str]:
        """
        Return list of possible made hand types.

        Examples: 'straight', 'flush', 'set', 'two_pair', etc.
        """
        possible = []

        # Check for possible flush
        if self.has_flush:
            possible.append('flush')
        elif self.has_flush_draw:
            possible.append('flush_draw')

        # Check for possible straight
        if self.straight_possibilities > 0:
            possible.append('straight')

        # Paired boards
        if self.is_trips:
            possible.append('quads')
            possible.append('full_house')
        elif self.is_paired:
            possible.append('full_house')
            possible.append('trips')
            possible.append('two_pair')
        else:
            possible.append('two_pair')

        # Always possible
        possible.append('pair')
        possible.append('high_card')

        return possible

    def get_blocker_value(self, hand: List[int]) -> int:
        """
        Calculate blocker value of a hand on this board.

        Higher values = better blockers
        """
        blocker_score = 0

        # Extract hand ranks and suits
        hand_ranks = []
        hand_suits = []

        for card_int in hand:
            rank_int = Card.get_rank_int(card_int)
            suit_int = Card.get_suit_int(card_int)
            rank_str = Card.STR_RANKS[rank_int]

            hand_ranks.append(rank_str)
            hand_suits.append(suit_int)

        # Flush blockers (if board has flush)
        if self.has_flush or self.has_flush_draw:
            # Find dominant suit
            dominant_suit = max(self.suit_counts, key=self.suit_counts.get)
            for suit in hand_suits:
                if suit == dominant_suit:
                    blocker_score += 2

        # Straight blockers
        if self.straight_possibilities > 0:
            # Cards that complete straights are valuable blockers
            for rank in hand_ranks:
                if rank in self.BROADWAY_CARDS:
                    blocker_score += 1

        # Pair blockers
        for rank in hand_ranks:
            if rank in self.ranks:
                # Blocks sets and trips
                blocker_score += 2

        return blocker_score

    def get_summary(self) -> Dict:
        """Return dictionary summary of board analysis"""
        return {
            'board': Card.print_pretty_cards(self.board),
            'texture_score': self.texture_score,
            'texture_category': self.texture_category,
            'is_paired': self.is_paired,
            'is_trips': self.is_trips,
            'has_flush': self.has_flush,
            'has_flush_draw': self.has_flush_draw,
            'connectivity': self.connectivity_score,
            'straight_possibilities': self.straight_possibilities,
            'broadway_count': self.broadway_count,
            'monotone': self.is_monotone(),
            'two_tone': self.is_two_tone(),
            'rainbow': self.is_rainbow(),
            'highest_rank': self.get_highest_rank(),
            'possible_hands': self.get_possible_hands(),
        }

    def __repr__(self) -> str:
        return (f"BoardAnalyzer(texture={self.texture_category}, "
                f"score={self.texture_score}, "
                f"paired={self.is_paired}, "
                f"flush={self.has_flush})")


if __name__ == "__main__":
    print("Testing BoardAnalyzer...\n")

    # Test 1: Dry board
    board1 = [Card.new('Kh'), Card.new('7s'), Card.new('2d')]
    analyzer1 = BoardAnalyzer(board1)
    print("Test 1: Dry Board (Kh 7s 2d)")
    print(f"  Texture: {analyzer1.texture_category}, Score: {analyzer1.texture_score}")
    print(f"  Connectivity: {analyzer1.connectivity_score}")
    print(f"  Straight possibilities: {analyzer1.straight_possibilities}")
    print()

    # Test 2: Wet board
    board2 = [Card.new('9h'), Card.new('8h'), Card.new('7d')]
    analyzer2 = BoardAnalyzer(board2)
    print("Test 2: Wet Board (9h 8h 7d)")
    print(f"  Texture: {analyzer2.texture_category}, Score: {analyzer2.texture_score}")
    print(f"  Connectivity: {analyzer2.connectivity_score}")
    print(f"  Straight possibilities: {analyzer2.straight_possibilities}")
    print(f"  Has flush draw: {analyzer2.has_flush_draw}")
    print()

    # Test 3: Monotone board
    board3 = [Card.new('Ks'), Card.new('9s'), Card.new('4s')]
    analyzer3 = BoardAnalyzer(board3)
    print("Test 3: Monotone Board (Ks 9s 4s)")
    print(f"  Texture: {analyzer3.texture_category}, Score: {analyzer3.texture_score}")
    print(f"  Is monotone: {analyzer3.is_monotone()}")
    print()

    # Test 4: Paired board
    board4 = [Card.new('Kh'), Card.new('Kd'), Card.new('7s')]
    analyzer4 = BoardAnalyzer(board4)
    print("Test 4: Paired Board (Kh Kd 7s)")
    print(f"  Texture: {analyzer4.texture_category}, Score: {analyzer4.texture_score}")
    print(f"  Is paired: {analyzer4.is_paired}")
    print()

    # Test 5: Five-card board with flush
    board5 = [Card.new('Ah'), Card.new('Kh'), Card.new('Qh'),
              Card.new('5h'), Card.new('2h')]
    analyzer5 = BoardAnalyzer(board5)
    print("Test 5: Flush Board (Ah Kh Qh 5h 2h)")
    print(f"  Texture: {analyzer5.texture_category}, Score: {analyzer5.texture_score}")
    print(f"  Has flush: {analyzer5.has_flush}")
    print()

    # Test 6: Blocker analysis
    hand = [Card.new('As'), Card.new('Ks')]
    board6 = [Card.new('Kh'), Card.new('Qd'), Card.new('Jd')]
    analyzer6 = BoardAnalyzer(board6)
    blocker_value = analyzer6.get_blocker_value(hand)
    print("Test 6: Blocker Analysis")
    print(f"  Hand: As Ks")
    print(f"  Board: Kh Qd Jd")
    print(f"  Blocker value: {blocker_value}")
    print()

    print("BoardAnalyzer tests completed!")
