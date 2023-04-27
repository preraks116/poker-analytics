from deuces import Card, Evaluator, Deck
from hse.hand_potential_1 import HandPotential_1
from hse.hand_potential_2 import HandPotential_2

deck = Deck()
evaluator = Evaluator()


hand = [Card.new('Ad'), Card.new('Qc')]

board = [Card.new('3h'), Card.new('4c'), Card.new('Jh')]

# hand = [Card.new('Ad'), Card.new('Qc')]
# hand = [Card.new('Jh'), Card.new('Th')]

# board = [Card.new('Qh'), Card.new('Kh'), Card.new('2c')]

HandPotential_2(board, hand)