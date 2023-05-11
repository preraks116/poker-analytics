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

    for oppcards in itertools.combinations(deck.cards, 2):
        oppcards = list(oppcards)

        # Remove the cards from the deck.
        for card in oppcards:
            deck.cards.remove(card)

        opprank = evaluator.evaluate(boardcards, oppcards)
        if ourrank < opprank:
            index = 0 #ahead
        elif ourrank == opprank:
            index = 1 #tied
        else:
            index = 2 #behind

        # All possiblities of the next 2 cards (turn and river)
        for next_cards in itertools.combinations(deck.cards, 2):
            next_cards = list(next_cards)
            HPTotal[index] += 1
            updated_board = boardcards + next_cards
            ourbest = evaluator.evaluate(updated_board, ourcards)
            oppbest = evaluator.evaluate(updated_board, oppcards)
            
            if ourbest < oppbest:
                HP[index][0] += 1
            elif ourbest == oppbest:
                HP[index][1] += 1
            else:
                HP[index][2] += 1
        
        # Restore the cards to the deck.
        for card in oppcards:
            deck.cards.append(card)
    
    print("HP: ", HP)
    print("HPTotal: ", HPTotal)

    # if the last two row of HP is all 0, then Ppot = 0
    if HP[2][0] == 0 and HP[2][1] == 0 and HP[2][2] == 0 and HP[1][0] == 0 and HP[1][1] == 0 and HP[1][2] == 0:
        Ppot = 0
    else:
        Ppot = (HP[2][0] + HP[2][1]/2 + HP[1][0]/2) / (HPTotal[2] + HPTotal[1])
    
    Npot = (HP[0][2] + HP[1][2]/2 + HP[0][1]/2) / (HPTotal[0] + HPTotal[1])
    print("Ppot: ", Ppot)
    print("Npot: ", Npot)

    return Ppot, Npot
    
