from deuces import Card, Evaluator, Deck
from hse.odds import odds_calculator
from hse.odds import mc_odds_calculator

deck = Deck()
evaluator = Evaluator()

hero_hand = [Card.new('Qc'), Card.new('Td')]
# 29.8
villain_hand = [Card.new('8c'), Card.new('6s')]
# 70.2

hands = [
    [['9h','7h'], ['3c','2s']],
    [['9c','7s'], ['3s','2d']],
    [['Jc','9c'], ['As','Td']],
    [['Ks','8c'], ['Ad','6c']],
    [['Ad','3c'], ['Ks','4c']],
    [['Tc','8s'], ['6s','6d']],
    [['Jc','9c'], ['7d','5d']],
    [['Kc','Jh'], ['Ah','3c']],
    [['8c','3s'], ['Kd','8d']],
    [['Qc','Td'], ['8c','6s']],
]

hands2 = [
    [['Qc','Td'], ['Ts','Th']],
    [['Qc','Td'], ['Ac','8s']],
    [['Qc','Qh'], ['Th','Ts']],
]

hands3 = [
    [['As','Ad'], ['2c','2d']],
    [['As','Ad'], ['Kh','9h']],
    [['Ks','Kd'], ['Ac','Qc']],
    [['As','Ad'], ['5s','2c']],
]

hands4 = [
    [['8d','9d'], ['3s','3c']],
]

for hand in hands:
    hero_hand = [Card.new(hand[0][0]), Card.new(hand[0][1])]
    villain_hand = [Card.new(hand[1][0]), Card.new(hand[1][1])]
    Card.print_pretty_cards(hero_hand)
    Card.print_pretty_cards(villain_hand)
    mc_val1, mc_val2 = mc_odds_calculator(hero_hand, villain_hand)
    abs_val1, abs_val2 = odds_calculator(hero_hand, villain_hand)
    error_percentage1 = abs(mc_val1 - abs_val1) / abs_val1
    error_percentage2 = abs(mc_val2 - abs_val2) / abs_val2
    print("MC1: ", mc_val1)
    print("ABS1: ", abs_val1)
    print("Error1: ", error_percentage1)
    print("-----")
    print(round(mc_val1,5), "&", round(abs_val1,5), "&", round(error_percentage1,5))
    print("-----")
    print("MC2: ", mc_val2)
    print("ABS2: ", abs_val2)
    print("Error2: ", error_percentage2)
    print("-----")
    print(round(mc_val2,5), "&", round(abs_val2,5), "&", round(error_percentage2,5))
    print("------")
    print("--------------------")

# odds_calculator(hero_hand, villain_hand)