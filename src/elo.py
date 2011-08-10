#!/bin/env python2.5
__doc__ = '''Functions for computing Elo chess-style ratings.'''

import math

start_r = 1500
k = 32

def e(r, rb):
	'''
	>>> '%.3f' % e(1613, 1609)
	'0.506'
	>>> '%.3f' % e(1613, 1477)
	'0.686'
	>>> '%.3f' % e(1613, 1388)
	'0.785'
	>>> '%.3f' % e(1613, 1586)
	'0.539'
	>>> '%.3f' % e(1613, 1720)
	'0.351'
	'''
	return 1 / (1 + math.pow(10, float(rb - r) / 400))

def r(r, opponents, k):
	'''
	>>> int(round(r(1613, [(1609, 0), (1477, 0.5), (1388, 1), (1586, 1), (1720, 0)], 32)))
	1601
	'''
	s_sum = 0
	e_sum = 0
	for rb, sa in opponents:
		s_sum += sa
		e_sum += e(r, rb)
	return r + (k * (s_sum - e_sum))

"""
coach_rating = {}
for game in Game.select(sqlbuilder.IN(Game.q.id, sqlbuilder.Select(
		GameTeam.q.gameID, where=GameTeam.q.score>0)), orderBy='date'):

	pre_game = []
	for gameTeam in game.gameTeams:
		pre_game.append((gameTeam.team.coach, coach_rating.get(gameTeam.team.coach.id, start_r), gameTeam.score))
	assert len(pre_game) == 2, 'Should have exactly two coaches in game'

	(coacha, ra, scorea), (coachb, rb, scoreb) = pre_game
	if scorea > scoreb:
		sa = 1
		sb = 0
	elif scorea == scoreb:
		sa = .5
		sb = .5
	else:
		sa = 0
		sb = 1

	coach_rating[coacha.id] = r(ra, [(rb, sa)], k)
	coach_rating[coachb.id] = r(rb, [(ra, sb)], k)
"""

if __name__ == '__main__':
	import doctest
	doctest.testmod()
