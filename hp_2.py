from deuces import Card, Evaluator, Deck
from hse.hand_potential_2 import HandPotential_2

deck = Deck()
evaluator = Evaluator()

hand = [Card.new('Ac'), Card.new('Qc')]
board = [Card.new('3h'), Card.new('4c'), Card.new('Jc')]

HandPotential_2(board, hand)