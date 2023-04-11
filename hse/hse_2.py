from deuces import Card, Evaluator, Deck
import itertools

evaluator = Evaluator()

def hse_2(board, hand, num_opps):
    wins, losses, ties = 0, 0, 0

    deck = Deck()
    # remove the cards from the deck
    for card in board + hand:
        deck.cards.remove(card)

    cards_needed = 5 - len(board)
    # for all possible combinations of the cards needed to fill the board
    for comm_cards in itertools.combinations(deck.cards, cards_needed):

        if any(card in board + hand for card in comm_cards):
            continue

        deck = Deck()
        final_board = board + list(comm_cards)
        for card in final_board + hand:
            deck.cards.remove(card)

        hero_score = evaluator.evaluate(final_board, hand)
        
        # # for all possible starting hands the opponent could have
        for i in range(len(deck.cards)):
            for j in range(i + 1, len(deck.cards)):
                villain_hand = [deck.cards[i], deck.cards[j]]

                # evaluate the hand
                villain_score = evaluator.evaluate(final_board, villain_hand)

                if hero_score < villain_score:
                    wins += 1
                elif hero_score > villain_score:
                    losses += 1
                else:
                    ties += 1

    print("Board:")
    Card.print_pretty_cards(board)
    print("Hero best hand:")
    Card.print_pretty_cards(evaluator.get_best_hand(board, hand))
    print("Rank: ", hero_score)
    print("Hero Class:", evaluator.class_to_string(evaluator.get_rank_class(hero_score)))
    print("Number of Opponents: ", num_opps)
    hse = (wins + ties / 2) / (wins + losses + ties)
    print("Wins: ", wins)
    print("Losses: ", losses)
    print("Ties: ", ties)
    print("Base HSE: ", hse)
    if(num_opps > 1):
        print("Adjusted HSE: ", hse ** num_opps)

