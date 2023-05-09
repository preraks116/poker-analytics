from deuces import Evaluator

evaluator = Evaluator()

def percentage_rank(board, hand):
    rank = evaluator.evaluate(board, hand)
    percentage = 1.0 - evaluator.get_five_card_rank_percentage(rank)
    return percentage