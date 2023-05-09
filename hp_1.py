from deuces import Card, Evaluator, Deck
from hse.hand_potential_1 import HandPotential_1

deck = Deck()
evaluator = Evaluator()

hand = [Card.new('Ad'), Card.new('Qc')]
board = [Card.new('3h'), Card.new('4c'), Card.new('Jh')]

HandPotential_1(board, hand)