from deuces import Card, Evaluator, Deck
from hse.hse_2 import hse_2
from hse.hse_1 import hse_1

deck = Deck()
evaluator = Evaluator()


hand = [Card.new('2s'), Card.new('3c')]

board = [Card.new('Th'), Card.new('8h'), Card.new('6h')]

h_1 = hse_1(board, hand)
print("------")
h_2 = hse_2(board, hand)
print("------")
print("Adjusted HSE for 2 players:", pow(h_1, 2))
print("HSE_2:", h_2)