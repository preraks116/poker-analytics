from deuces import Card, Evaluator, Deck

evaluator = Evaluator()

def preflop_monte_carlo(hand, num_opps, iterations=100000):
    # for num_players in range(1, 11):
    for num_players in range(1, num_opps):
        wins = 0
        ties = 0
        losses = 0
        for i in range(iterations):
            deck = Deck()
            for card in hand:
                deck.cards.remove(card)
            board = deck.draw(5)
            hero_score = evaluator.evaluate(board, hand)
            villain_hands = []
            for i in range(num_players):
                villain_hands.append(deck.draw(2))
            villain_scores = []
            for villain_hand in villain_hands:
                villain_scores.append(evaluator.evaluate(board, villain_hand))
            
            if hero_score < min(villain_scores):
                wins += 1
            elif hero_score == max(villain_scores):
                ties += 1
            else:
                losses += 1
        hse = (wins + ties / 2) / (wins + losses + ties)
        print("Number of Opponents: ", num_players)
        print("Wins: ", wins)
        print("Losses: ", losses)
        print("Ties: ", ties)
        print("WP: ", hse)
        print("----")
