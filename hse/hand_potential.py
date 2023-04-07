from deuces import Evaluator, Deck

evaluator = Evaluator()

def HandPotential(boardcards, ourcards):
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
    for i in range(len(deck.cards)):
        for j in range(i + 1, len(deck.cards)):
            oppcards = [deck.cards[i], deck.cards[j]]

            # print(oppcards)

            opprank = evaluator.evaluate(boardcards, oppcards)

            if ourrank < opprank:
                index = 0  # ahead
            elif ourrank == opprank:
                index = 1  # tied
            else:
                index = 2  # behind

            HPTotal[index] += 1

            # All possible board cards to come.
            for k in range(len(deck.cards)):
                if k == i or k == j:
                    continue

                for l in range(k + 1, len(deck.cards)):
                    if l == i or l == j:
                        continue

                    turn = deck.cards[k]
                    river = deck.cards[l]

                    # Final 5-card board.
                    board = boardcards + [turn, river]

                    # print("Board: ", board)

                    ourbest = evaluator.evaluate(board, ourcards)
                    oppbest = evaluator.evaluate(board, oppcards)

                    if ourbest < oppbest:
                        HP[index][0] += 1  # ahead
                    elif ourbest == oppbest:
                        HP[index][1] += 1  # tied
                    else:
                        HP[index][2] += 1  # behind

    # Ppot: were behind but moved ahead.
    Ppot = (HP[2][0] + HP[2][1] / 2 + HP[1][0] / 2) / (HPTotal[2] + HPTotal[1])

    # Npot: were ahead but fell behind.
    Npot = (HP[0][2] + HP[1][2] / 2 + HP[0][1] / 2) / (HPTotal[0] + HPTotal[1])

    # print all the information
    print("Hand Potential")
    print("Ppot: ", Ppot)
    print("Npot: ", Npot)

    return (Ppot, Npot)
