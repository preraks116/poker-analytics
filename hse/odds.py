from deuces import Card, Evaluator, Deck
import itertools

evaluator = Evaluator()

def mc_odds_calculator(hero_hand, villain_hand):
    hero_wins = 0
    villain_wins = 0

    for i in range(100000):
        deck = Deck()

        for card in hero_hand + villain_hand:
            deck.cards.remove(card)
        board = deck.draw(5)

        hero_score = evaluator.evaluate(list(board), hero_hand)
        villain_score = evaluator.evaluate(list(board), villain_hand)

        if hero_score < villain_score:
            hero_wins += 1
        elif hero_score > villain_score:
            villain_wins += 1

        

    w_1 = hero_wins / (hero_wins + villain_wins)
    w_2 = villain_wins / (hero_wins + villain_wins)

    print("Hero WP: ", hero_wins / (hero_wins + villain_wins))
    print("Villain WP: ", villain_wins / (hero_wins + villain_wins))

    return w_1, w_2

def odds_calculator(hero_hand, villain_hand):
    hero_wins = 0
    villain_wins = 0

    deck = Deck()

    for card in hero_hand + villain_hand:
        deck.cards.remove(card)

    # all possible boards
    for board in itertools.combinations(deck.cards, 5):
        hero_score = evaluator.evaluate(list(board), hero_hand)
        villain_score = evaluator.evaluate(list(board), villain_hand)

        if hero_score < villain_score:
            hero_wins += 1
        elif hero_score > villain_score:
            villain_wins += 1

    hero_wp = hero_wins / (hero_wins + villain_wins)
    villain_wp = villain_wins / (hero_wins + villain_wins)

    print("Hero WP: ", hero_wins / (hero_wins + villain_wins))
    print("Villain WP: ", villain_wins / (hero_wins + villain_wins))

    return hero_wp, villain_wp