from deuces import Card, Evaluator, Deck

evaluator = Evaluator()

def hse_1(board, hand, num_opps):
    wins = 0
    losses = 0
    ties = 0

    deck = Deck()

    for card in board + hand: 
        deck.cards.remove(card)

    hero_score = evaluator.evaluate(board, hand)
    hero_class = evaluator.get_rank_class(hero_score)

    # for all possible starting hands the opponent could have
    for i in range(len(deck.cards)):
        for j in range(i + 1, len(deck.cards)):

            villain_hand = [deck.cards[i], deck.cards[j]]
            villain_score = evaluator.evaluate(board, villain_hand)
        
            if hero_score < villain_score:
                wins += 1
            elif hero_score > villain_score:
                losses += 1
            else:
                ties += 1

    print("Hero best hand:")
    Card.print_pretty_cards(evaluator.get_best_hand(board, hand))
    print("Rank: ", hero_score)
    print("Class: ", evaluator.class_to_string(hero_class))

    print("Wins: ", wins)
    print("Losses: ", losses)
    print("Ties: ", ties)

    hse = (wins + ties / 2) / (wins + losses + ties)
    print("HSE: ", hse)