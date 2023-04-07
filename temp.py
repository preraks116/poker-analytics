# print("Player 2's cards:")
# Card.print_pretty_cards(player2_hand)

# print("Player 1's hand:")
# Card.print_pretty_cards(player1_hand + board)

# hero_score = evaluator.evaluate(board, player1_hand)
# villain_score = evaluator.evaluate(board, player2_hand)

# # bin the scores into classes
# p1_class = evaluator.get_rank_class(hero_score)
# p2_class = evaluator.get_rank_class(villain_score)

# # or get a human-friendly string to describe the score
# print("Player 1 hand rank = %d (%s)" % (hero_score, evaluator.class_to_string(p1_class)))
# print("Player 2 hand rank = %d (%s)" % (villain_score, evaluator.class_to_string(p2_class)))

# # or just a summary of the entire hand
# hands = [player1_hand, player2_hand]
# evaluator.hand_summary(board, hands)