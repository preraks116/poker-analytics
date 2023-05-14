from deuces import Card, Evaluator, Deck
from hse.hand_potential_1 import HandPotential_1

deck = Deck()
evaluator = Evaluator()

hand = [Card.new('7d'), Card.new('5c')]
board = [Card.new('4h'), Card.new('3c'), Card.new('2h')]


HandPotential_1(board, hand)