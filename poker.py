"""This script is used to colculate probabilities and best strategies while playing poker."""

import itertools
import time
import collections

def calc_probability(amount_players, hand, flop=None, turn=None, river=None):
	"""Calculate the probability of winning the hand."""
	# check inputs
	if amount_players < 2:
		print "Incorrect number of players."
		return

	# set up deck
	faces = "23456789TJQKA"
	suits = "CHSD"
	deck = ["".join(t) for t in itertools.product(faces, suits)]
	

	# how many cards are needed?
	count = 0
	if flop == None:
		count += 5
	elif turn == None:
		count += 2
	elif river == None:
		count += 1
	count += 2*amount_players-1

	# count wins/loses (draw is half a win)
	wins = 0
	total = 0
	# loop list of all possible shared cards
	if flop == None:
		deck = [c for c in deck if not c in hand]
		shareds = itertools.combinations(deck, 5)
	elif turn == None:
		deck = [c for c in deck if not c in hand+flop]
		shareds = [flop+t for t in itertools.combinations(deck, 2)]
	elif river == None:
		deck = [c for c in deck if not c in hand+flop+turn]
		shareds = [flop+turn+t for t in itertools.combinations(deck, 1)]
	else:
		deck = [c for c in deck if not c in hand+flop+turn+river]
		shareds = [flop+turn+river]
	for s in shareds:
		# create dictionary of hands that win/lose/draw against the player
		player_score = score(list(s)+hand)
		better = list()
		equal = list()
		deck_temp = deck = [c for c in deck if not c in s]
		possible_hands = [list(h) for h in itertools.combinations(deck_temp, 2)]
		for h in possible_hands:
			temp_score = score(list(s)+h)
			if temp_score > player_score:
				better.append(h)
			elif temp_score == player_score:
				equal.append(h)
			# else:
			# 	score_dict["lose"] = score_dict.setdefault("lose", list()).append(h)

		# loop all possible opponent hand combinations
		opponent_hands = itertools.combinations(possible_hands, amount_players-1)
		for ohs in opponent_hands:
			if no_duplicates(ohs):
				wins += simulate_game(ohs, better, equal)
				total += 1

	print len(better), len(equal), len(possible_hands), len(possible_hands)-len(better)-len(equal)
	return float(wins)/total

def no_duplicates(hands):
	"""Verfiy that there are no duplicate elements in the given list of lists."""
	all_cards = sorted(itertools.chain.from_iterable(hands))
	for i in range(len(all_cards)-1):
		if all_cards[i] == all_cards[i+1]:
			return False
	return True

def simulate_game(ohs, better, equal):
	"""Does the player win the given game? (returns 1 on win and 1/2 on draw)"""
	draw = False
	for oh in ohs:
		if oh in better:
			return 0
		if oh in equal:
			draw = True

	if draw:
		return 0.5
	return 1

def flush(h):
	"""Which cards are part of the flush?"""
	my_dict = dict()
	for c in h:
		my_dict[c[1]] = my_dict.setdefault(c[1], 0)+1
	k,m = max(my_dict.items(), key=(lambda (k,m): m))		# find the suit k with the highest number of cards m
	if m >= 5:
		return [c for c in h if c[1] == k]					# get a list of the cards with suit k
	return None

def straight(h):
	"""What is the highest card of the straight?"""
	values = [card_to_score(c) for c in h]
	if 14 in values:
		values.append(1)	# have to consider A as value 1
	values = remove_duplicates(values)
	values.sort(reverse=True)
	for i in range(len(values)-5):
		if consecutive(values[i:i+5]):
			return values[i]
	return None

def remove_duplicates(l):
	"""Remove duplicates from a list."""
	return list(collections.OrderedDict.fromkeys(l))

def consecutive(h):
	"""Check if the list of cards are consecutive"""
	prev = h[0]
	for c in h[1:]:
		if c != prev-1:
			return False
		prev = c 
	return True

def score(h):
	"""Calculate the score corresponding to the hand."""
	# straight flush
	flush_cards = flush(h)	# can be a list of flush cards, or None
	if flush_cards:
		straight_card = straight(flush_cards)
		if straight_card:
			return (700 + straight_card)*pow(100,4)		

	# 4 of a kind
	count_dict = count_cards(h)
	count_values = count_dict.values()
	values = sorted([card_to_score(c) for c in h], reverse=True)
	if 4 in count_values:
		score4 = card_to_score(find_key(count_dict, 4)[0])
		hc = sorted([v for v in values if v != score4], reverse=True)[0]
		return (60000 + score4*100 + hc)*pow(100,3)

	# full house
	if 3 in count_values and 2 in count_values:
		score3 = card_to_score(find_key(count_dict, 3)[0])
		score2 = card_to_score(find_key(count_dict, 2)[0])
		return (50000 + score3*100 + score2)*pow(100,3)

	# flush
	if flush_cards:
		values = sorted([card_to_score(c) for c in flush_cards], reverse=True)
		hcs = sum([values[i]*pow(100,5-i) for i in range(5)])
		return 4*pow(100,5) + hcs
	
	# straight
	straight_card = straight(h)
	if straight_card:
		return (300 + straight_card)*pow(100,4)

	# 3 of a kind
	if 3 in count_dict.values():
		score3 = card_to_score(find_key(count_dict, 3)[0])
		hcs = sorted([v for v in values if v != score3], reverse=True)[:2]
		return (2000000 + score3*10000 + hcs[0]*100 + hcs[1])*pow(100,2)
	
	# pair(s)
	if 2 in count_dict.values():
		score2s = sorted([card_to_score(k) for k in find_key(count_dict, 3)[:2]])	# list of max ascending two score2s
		score2 = 0
		for s in score2s:
			score2 = score2 *100 + s
		hcs = sorted([v for v in values if not v in score2s], reverse=True)[:3]
		return pow(100,5) + score2*pow(100,3) + hcs[0]*10000 + hcs[1]*100 + hcs[2]
	
	# high card
	return sum([values[i]*pow(100, 5-i) for i in range(5)])

def find_key(my_dict, value):
	return sorted([k for k in my_dict.keys() if my_dict[k]==value], reverse=True)

def count_cards(h):
	"""Count how often each type of card is present (return a dictionary)."""
	my_dict = dict()
	for c in h:
		value = c[0]
		temp = my_dict.setdefault(value, 0)
		my_dict[value] = temp+1
	return my_dict

def card_to_score(c):
	"""Return the value of the given card."""
	return 2 + "23456789TJQKA".index(c[0])
	
### MAIN

# faces = "23456789TJQKA"
# suits = "CH"
# deck  = ["".join(t) for t in itertools.product(faces, suits)]
# possible_hands = itertools.combinations(deck, 2)
# t_start = time.time()
# for h in possible_hands:
# 	t0 = time.time()
# 	prob = calc_probability(2, list(h))
# 	t1 = time.time()
# 	print h, "\t", prob, "\t", t1-t0
# t_end = time.time()
# print
# print "Total time:", t_end-t_start

t_start = time.time()
prob = calc_probability(2, ["AC", "KD"])
t_end = time.time()
print prob, t_end-t_start