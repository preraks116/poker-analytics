from deuces import Card, Evaluator, Deck
from hse.hand_potential_2 import HandPotential_2

deck = Deck()
evaluator = Evaluator()

hand = [Card.new('Ad'), Card.new('Qc')]
board = [Card.new('3h'), Card.new('4c'), Card.new('Jh')]

HandPotential_2(board, hand)