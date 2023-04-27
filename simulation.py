from deuces import Card, Evaluator, Deck
from hse.mc_preflop import preflop_monte_carlo
from hse.hse_1 import hse_1
from hse.hand_potential_1 import HandPotential_1
from hse.hand_potential_2 import HandPotential_2
from hse.percentage_rank import percentage_rank

deck = Deck()
evaluator = Evaluator()
num_opps = 1

hero_hand = deck.draw(2)
villain_hand = deck.draw(2)
print("Hero's hand:")
Card.print_pretty_cards(hero_hand)

print("Villain's hand:")
Card.print_pretty_cards(villain_hand)
print("--------------------")
print("Preflop:")
print("Hero:")
preflop_monte_carlo(hero_hand, 2)
print("Villain:")
preflop_monte_carlo(villain_hand, 2)
print("--------------------")

board = deck.draw(3)
print("Board:")
Card.print_pretty_cards(board)
print("Hero's hand rank: ", percentage_rank(board, hero_hand))
print("Villain's hand rank: ", percentage_rank(board, villain_hand))

print("--------------------")
print("HSE1:")
print("Hero:")
hse_1(board, hero_hand, num_opps)
print("Villain:")
hse_1(board, villain_hand, num_opps)
print("--------------------")
print("HandPotential2:")
print("Hero:")
HandPotential_2(board, hero_hand)
print("Villain:")
HandPotential_2(board, villain_hand)
print("--------------------")

turn = deck.draw(1)
board = board + [turn]
print("Board:")
Card.print_pretty_cards(board)
print("Hero's hand rank: ", percentage_rank(board, hero_hand))
print("Villain's hand rank: ", percentage_rank(board, villain_hand))

print("--------------------")
print("HandPotential1:")
print("Hero:")
HandPotential_1(board, hero_hand)
print("Villain:")
HandPotential_1(board, villain_hand)

river = deck.draw(1)
board = board + [river]
print("Board:")
Card.print_pretty_cards(board)
print("Hero's hand rank: ", percentage_rank(board, hero_hand))
print("Villain's hand rank: ", percentage_rank(board, villain_hand))

print("--------------------")
hero_rank = evaluator.evaluate(board, hero_hand)
villain_rank = evaluator.evaluate(board, villain_hand)

hero_rank_class = evaluator.get_rank_class(hero_rank)
villain_rank_class = evaluator.get_rank_class(villain_rank)

print("Hero's rank: ", evaluator.class_to_string(hero_rank_class))
print("Villain's rank: ", evaluator.class_to_string(villain_rank_class))

best_hero_hand = evaluator.get_best_hand(board, hero_hand)
best_villain_hand = evaluator.get_best_hand(board, villain_hand)

print("Hero's best hand:")
Card.print_pretty_cards(best_hero_hand)
print("Villain's best hand:")
Card.print_pretty_cards(best_villain_hand)

if hero_rank_class > villain_rank_class:
    print("Hero wins!")
elif hero_rank_class < villain_rank_class:
    print("Villain wins!")