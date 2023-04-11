from deuces import Evaluator

evaluator = Evaluator()

def percentage_rank(board, hand):
    rank = evaluator.evaluate(board, hand)
    rank_class = evaluator.get_rank_class(rank)
    rank_class_string = evaluator.class_to_string(rank_class)
    percentage = 1.0 - evaluator.get_five_card_rank_percentage(rank)
    return percentage