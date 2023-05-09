from deuces import Card, Evaluator, Deck
from hse.odds import odds_calculator
from hse.odds import mc_odds_calculator

deck = Deck()
evaluator = Evaluator()

hero_hand = [Card.new('Ah'), Card.new('Ks')]
# 29.8
villain_hand = [Card.new('Kc'), Card.new('Kd')]
# 70.2

# odds_calculator(hero_hand, villain_hand)
mc_odds_calculator(hero_hand, villain_hand)