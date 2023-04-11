import itertools
from deuces import Card, Evaluator, Deck

evaluator = Evaluator()

def HandPotential_2(boardcards, ourcards):
    # Hand potential array, each index represents ahead, tied, and behind.
    HP = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    # Initialize HPTotal to 0.
    HPTotal = [0, 0, 0]

    deck = Deck()

    ourrank = evaluator.evaluate(boardcards, ourcards)

    # Remove the cards from the deck.
    for card in boardcards + ourcards:
        deck.cards.remove(card)

    # Consider all two card combinations of the remaining cards for the opponent.
    for oppcards in itertools.combinations(deck.cards, 2):
        deck = Deck()
        oppcards = list(oppcards)
        # Remove the cards from the deck.
        for card in boardcards + ourcards + oppcards:
            deck.cards.remove(card)

        opprank = evaluator.evaluate(boardcards, oppcards)

        if ourrank < opprank:
            index = 0 #ahead
        elif ourrank == opprank:
            index = 1 #tied
        else:
            index = 2 #behind
        HPTotal[index] += 1

        # All possible board cards to come.
        for turn in deck.cards:
            for river in deck.cards:
                if turn == river:
                    continue
                # Final 5-card board.
                board = boardcards + [turn, river]

                ourbest = evaluator.evaluate(board, ourcards)
                oppbest = evaluator.evaluate(board, oppcards)

                if ourbest < oppbest:
                    HP[index][0] += 1
                elif ourbest == oppbest:
                    HP[index][1] += 1
                else:
                    HP[index][2] += 1
    
    # divide every value in HP and HPTotal by 2
    HP = [[x/2 for x in y] for y in HP]
    # HPTotal = [x for x in HPTotal]

    # print HP and HPtotal
    print("HP: ", HP)
    print("HPTotal: ", HPTotal)

    Ppot = (HP[2][0] + HP[2][1]/2 + HP[1][0]/2) / (HPTotal[2] + HPTotal[1])
    Npot = (HP[0][2] + HP[1][2]/2 + HP[0][1]/2) / (HPTotal[0] + HPTotal[1])

    print("Ppot: ", Ppot)
    print("Npot: ", Npot)


    
