#!/bin/env python2.5
__doc__ = '''Functions for computing Glicko chess-style ratings.'''

import math

min_rd = 165
max_rd = 340
start_r = 1500
start_rd = max_rd
typical_rd = 200
expiration_t = 730 # two years
q = math.log(10) / 400
c = math.sqrt((math.pow(max_rd, 2) - math.pow(typical_rd, 2)) / expiration_t)

def g(rd):
	'''
	>>> '%.4f' % g(30)
	'0.9955'
	>>> '%.4f' % g(100)
	'0.9531'
	>>> '%.4f' % g(300)
	'0.7242'
	'''
	return 1 / math.sqrt(1 + 3 * math.pow(q, 2) * math.pow(rd, 2) / math.pow(math.pi, 2))

def e(r, rj, rdj):
	'''
	>>> '%.3f' % e(1500, 1400, 30)
	'0.639'
	>>> '%.3f' % e(1500, 1550, 100)
	'0.432'
	>>> '%.3f' % e(1500, 1700, 300)
	'0.303'
	'''
	return 1 / (1 + math.pow(10, -g(rdj) * (r -rj) / 400))

def d_squared(r, opponents):
	'''
	>>> '%.2f' % d_squared(1500, [(1400, 30, 1), (1550, 100, 0), (1700, 300, 0)])
	'53685.74'
	'''
	summation = 0
	for opponent in opponents:
		rj, rdj, sj = opponent
		ej = e(r, rj, rdj)
		summation += math.pow(g(rdj), 2) * ej * (1 - ej)
	return math.pow(math.pow(q, 2) * summation, -1)

def pre_rd(old_rd, c, t):
	return max(min(math.sqrt(math.pow(old_rd, 2) + t * math.pow(c, 2)), max_rd), min_rd)

def post_r(r, rd, opponents):
	'''
	>>> '%.0f' % post_r(1500, 200, [(1400, 30, 1), (1550, 100, 0), (1700, 300, 0)])
	'1464'
	'''
	summation = 0
	for opponent in opponents:
		rj, rdj, sj = opponent
		summation += g(rdj) * (sj - e(r, rj, rdj))
	return r + ((q / ((1 / math.pow(rd, 2)) + (1 / d_squared(r, opponents)))) * summation)

def post_rd(r, rd, opponents):
	'''
	>>> '%.1f' % post_rd(1500, 200, [(1400, 30, 1), (1550, 100, 0), (1700, 300, 0)])
	'151.4'
	'''
	return math.sqrt(math.pow((1 / math.pow(rd, 2)) + (1 / d_squared(r, opponents)), -1))

if __name__ == '__main__':
	import doctest
	doctest.testmod()
