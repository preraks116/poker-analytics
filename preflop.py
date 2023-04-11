from deuces import Card
from hse.mc_preflop import preflop_monte_carlo

hand = [Card.new('As'), Card.new('Ks')]
preflop_monte_carlo(hand, 10)