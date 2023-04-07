from deuces import Evaluator, Deck

evaluator = Evaluator()

# given the hand and the board, a function that evaluates the number of hands
def outs(board, hand):
    outs = 0    
    
    deck = Deck()

    for card in board + hand: 
        deck.cards.remove(card)

    score = evaluator.evaluate(board, hand)

    print(score)