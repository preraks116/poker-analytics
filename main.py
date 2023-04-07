from deuces import Card, Evaluator, Deck
from hse.hse_1 import hse_1
from hse.monte_carlo import monte_carlo
from hse.hand_potential import HandPotential
from hse.outs import outs


evaluator = Evaluator()

print("Dealing a new hand...")
deck = Deck()
player1_hand = deck.draw(2)
board = deck.draw(3)

# number of villains
num_opps = 1

print("The board:")
Card.print_pretty_cards(board)

print("Hero's cards:")
Card.print_pretty_cards(player1_hand)

hse_1(board, player1_hand, num_opps)
# print("--------------------")
# monte_carlo(board, player1_hand, 10000, num_opps)
# HandPotential(board, player1_hand)
# outs(board, player1_hand)