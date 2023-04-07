from deuces import Card, Evaluator, Deck

evaluator = Evaluator()

# function that performs a monte carlo simulation of a hand
def monte_carlo(board, hand, iterations, num_opps):  
    wins = 0
    losses = 0
    ties = 0


    # for all possible starting hands the opponent could have
    for i in range(iterations):
        deck = Deck()

        # remove the cards from the deck
        for card in board + hand: 
            deck.cards.remove(card)

        cards_needed = 5 - len(board)
        board = board + deck.draw(cards_needed)

        # evaluate the hand
        hero_score = evaluator.evaluate(board, hand)
        villain_hand = deck.draw(2)
        villain_score = evaluator.evaluate(board, villain_hand)

        if hero_score < villain_score:
            wins += 1
        elif hero_score > villain_score:
            losses += 1
        else:
            ties += 1

    # print("Board:")
    # Card.print_pretty_cards(board)
    # print("Hero best hand:")
    # Card.print_pretty_cards(evaluator.get_best_hand(board, hand))
    # print("Rank: ", hero_score)
    # print("Class: ", evaluator.class_to_string(hero_class))
    print("Number of Opponents: ", num_opps)
    print("Wins: ", wins)
    print("Losses: ", losses)
    print("Ties: ", ties)
    hse = (wins + ties / 2) / (wins + losses + ties)
    print("Base HSE: ", hse)
    if(num_opps > 1):
        hse = hse ** num_opps
        print("Adjusted HSE: ", hse)
    return hse