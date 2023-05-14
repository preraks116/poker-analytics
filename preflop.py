from deuces import Card
from hse.mc_preflop import preflop_monte_carlo
from hse.mc_preflop import preflop_wp

hand = [Card.new('Ah'), Card.new('3c')]
preflop_monte_carlo(hand, 2)
# preflop_wp(hand)
