#!/usr/bin/env python2.4
__doc__ = '''Blood Bowl Web manager data model.'''

import ConfigParser
import datetime
import sys
import types

# Read in the nuffle configuration so we can determine
# where our third party python libraries have been
# installed.
cfg = ConfigParser.ConfigParser()
cfg.read('nuffle.cfg')
sys.path.insert(0, cfg.get('nuffle', 'dir.lib.python'))
from sqlobject import *


### CACHED KONSTANTS ###

def maIncrease():
	if not globals().has_key('__MA_INCREASE'):
		global __MA_INCREASE
		__MA_INCREASE = Skill.byName('+MA')
	return __MA_INCREASE

def stIncrease():
	if not globals().has_key('__ST_INCREASE'):
		global __ST_INCREASE
		__ST_INCREASE = Skill.byName('+ST')
	return __ST_INCREASE

def agIncrease():
	if not globals().has_key('__AG_INCREASE'):
		global __AG_INCREASE
		__AG_INCREASE = Skill.byName('+AG')
	return __AG_INCREASE

def avIncrease():
	if not globals().has_key('__AV_INCREASE'):
		global __AV_INCREASE
		__AV_INCREASE = Skill.byName('+AV')
	return __AV_INCREASE

def loner():
	if not globals().has_key('__LONER'):
		global __LONER
		__LONER = Skill.byName('Loner')
	return __LONER

def positionSkills(position):
	if not globals().has_key('__POSITION_SKILLS'):
		global __POSITION_SKILLS
		__POSITION_SKILLS = {}
	if not __POSITION_SKILLS.has_key(position):
		__POSITION_SKILLS[position] = position._skills
	return __POSITION_SKILLS[position]

def normalAccess(position):
	if not globals().has_key('__NORMAL_ACCESS'):
		global __NORMAL_ACCESS
		__NORMAL_ACCESS = {}
	if not __NORMAL_ACCESS.has_key(position):
		__NORMAL_ACCESS[position] = position._normalAccess
	return __NORMAL_ACCESS[position]

def doubleAccess(position):
	if not globals().has_key('__DOUBLE_ACCESS'):
		global __DOUBLE_ACCESS
		__DOUBLE_ACCESS = {}
	if not __DOUBLE_ACCESS.has_key(position):
		__DOUBLE_ACCESS[position] = position._doubleAccess
	return __DOUBLE_ACCESS[position]


### FUNCTIONS ###

def sqlobjectConnection():
	return dbconnection.connectionForURI(cfg.get('nuffle', 'db.uri'))


def skillCutoff (numAdvances):
	if numAdvances <= 0:
		return 0
	elif numAdvances == 1:
		return 6
	elif numAdvances == 2:
		return 16
	elif numAdvances == 3:
		return 31
	elif numAdvances == 4:
		return 51
	elif numAdvances == 5:
		return 76
	elif numAdvances >= 6:
		return 176


### BUSINESS CLASSES ###

class BizObject (SQLObject):
	'''Base business object.'''
	_connection = cfg.get('nuffle', 'db.uri')

	def basePath (self):
		return self.__class__.__name__.lower()

	def edit (self):
		return '/%s/edit?id=%s' % (self.basePath(), self.id)

	def printPage (self):
		return '/%sPrint/id/%s' % (self.basePath(), self.id)

	def view (self):
		return '/%s/id/%s' % (self.basePath(), self.id)


class Bye (BizObject):

	date = DateTimeCol (notNone = True)
	season = ForeignKey ('Season', notNone = True)
	team = ForeignKey ('Team', notNone = True)


class Coach (BizObject):
	class sqlmeta:
		defaultOrder = 'realname'

	username = StringCol (alternateID = True, length = 16, notNone = True)
	password = StringCol (length = 16, notNone = True)
	realname = StringCol (length = 128, default = None)
	email = StringCol (length = 64, default = None)
	phone = StringCol (length = 32, default = None)
	role = EnumCol (enumValues = ['ADMIN', 'USER'], default = 'USER')
	teams = MultipleJoin ('Team')

	def isAdmin (self):
		return self.role == 'ADMIN'


class Game (BizObject):
	class sqlmeta:
		defaultOrder = '-date'

	date = DateTimeCol (notNone = True)
	gate = IntCol (default = None)
	overtime = BoolCol (default = 0)
	description = StringCol (default = None)
	gameTeams = MultipleJoin ('GameTeam')
	season = ForeignKey ('Season', notNone = True)

	def isDone (self):
		for gameTeam in self.gameTeams:
			if gameTeam.score > 0:
				return True
		return False


class GameTeam (BizObject):
	class sqlmeta:
		defaultOrder = '-score'

	game = ForeignKey ('Game', notNone = True)
	team = ForeignKey ('Team', notNone = True)
	score = IntCol (default = 0)
	winnings = IntCol (default = 0, notNone = True)
	ffChange = EnumCol (enumValues = ['-1', '0', '+1'], default = '0')
	players = MultipleJoin ('GameTeamPlayer')


class GameTeamPlayer (BizObject):
	class sqlmeta:
		defaultOrder = 'id'

	gameTeam = ForeignKey ('GameTeam', notNone = True)
	player = ForeignKey ('Player', notNone = True)
	td = IntCol (default = 0, notNone = True)
	cas = IntCol (default = 0, notNone = True)
	comp = IntCol (default = 0, notNone = True)
	cat = IntCol (default = 0, notNone = True)
	inter = IntCol (default = 0, notNone = True)
	mvp = IntCol (default = 0, notNone = True)
	injury = EnumCol (enumValues = ['', 'BH', 'MNG', 'NI', '-1MA', '-1AV', '-1AG', '-1ST', 'DEAD'], default = '')


class Medal (BizObject):

	type = EnumCol (enumValues = ['GOLD', 'SILVER', 'BRONZE'], notNone = True)
	team = ForeignKey ('Team', notNone = True)


class Player (BizObject):
	class sqlmeta:
		defaultOrder = 'number'

	number = IntCol ()
	name = StringCol (length = 128, default = None)
	isJourneyman = BoolCol (default = 0)
	isRetired = BoolCol (default = 0)
	skills = RelatedJoin ('Skill')
	position = ForeignKey ('Position', notNone = True)
	team = ForeignKey ('Team')
	gamePlayers = MultipleJoin ('GameTeamPlayer')

	def MA (self):
		return self.position.ma + self.skills.count (maIncrease()) \
			- sum ([gamePlayer.injury == '-1MA' and 1 or 0 for gamePlayer in self.gamePlayers])

	def ST (self):
		return self.position.st + self.skills.count (stIncrease()) \
			- sum ([gamePlayer.injury == '-1ST' and 1 or 0 for gamePlayer in self.gamePlayers])

	def AG (self):
		return self.position.ag + self.skills.count (agIncrease()) \
			- sum ([gamePlayer.injury == '-1AG' and 1 or 0 for gamePlayer in self.gamePlayers])

	def AV (self):
		return self.position.av + self.skills.count (avIncrease()) \
			- sum ([gamePlayer.injury == '-1AV' and 1 or 0 for gamePlayer in self.gamePlayers])

	def edit (self):
		return self.team.edit() + '&player=%d' % self.id

	def eligibleSkill (self, skill):
		return skill not in self.skills \
			or (skill.category is SkillCategory.byName('Stat Increase') \
				and self.skills.count(skill) < 2)

	def htmlName (self):
		if self.isJourneyman:
			return '<i>Journeyman</i>'
		elif not self.name:
			return '<i>Unknown</i>'
		return self.name

	def isActive (self):
		return not self.isRetired and not self.isDead()

	def isDead (self):
		for gamePlayer in self.gamePlayers:
			if gamePlayer.injury == 'DEAD':
				return True
		return False

	def isMNG (self):
		if not self.isActive():
			return True
		lastBye = self.team.lastBye()
		lastGame = self.team.lastGame()
		if lastBye and lastGame and lastBye.date > lastGame.date:
			return False
		if lastGame:
			for gameTeam in lastGame.gameTeams:
				if gameTeam.team is self.team:
					for gamePlayer in gameTeam.players:
						if gamePlayer.player is self:
							return gamePlayer.injury not in ['','BH']
		return False

	def spp (self):
		spp = 0
		for gamePlayer in self.gamePlayers:
			spp += gamePlayer.td * 3
			spp += gamePlayer.cas * 2
			spp += gamePlayer.comp * 1
			spp += gamePlayer.inter * 2
			spp += gamePlayer.mvp * 5
		return spp

	def nonPositionSkills (self):
		return [skill for skill in self.skills if skill not in positionSkills(self.position) and skill != loner()]

	def needSkills (self):
		return self.spp() >= skillCutoff(len(self.nonPositionSkills()) + 1)

	def tooManySkills (self):
		return self.spp() < skillCutoff(len(self.nonPositionSkills()))

	def value (self):
		if self.isMNG():
			return 0
		total = self.position.cost
		for skill in self.nonPositionSkills():
			if skill == stIncrease():
				total += 50000
			elif skill == agIncrease():
				total += 40000
			elif skill == maIncrease():
				total += 30000
			elif skill == avIncrease():
				total += 30000
			elif skill.category in normalAccess(self.position):
				total += 20000
			else:
				total += 30000
		return total


class Position (BizObject):
	class sqlmeta:
		defaultOrder = 'cost'

	name = StringCol (length = 128, notNone = True)
	ma = IntCol (notNone = True)
	st = IntCol (notNone = True)
	ag = IntCol (notNone = True)
	av = IntCol (notNone = True)
	cost = IntCol (notNone = True)
	max = IntCol (notNone = True)
	race = ForeignKey ('Race')
	_skills = RelatedJoin ('Skill') # use positionSkills function
	players = MultipleJoin ('Player')
	_normalAccess = RelatedJoin ('SkillCategory', addRemoveName='NormalAccess', intermediateTable='normal_access') # use normalAccess function
	_doubleAccess = RelatedJoin ('SkillCategory', addRemoveName='DoubleAccess', intermediateTable='double_access') # use doubleAccess function


class Race (BizObject):
	class sqlmeta:
		defaultOrder = 'name'

	name = StringCol (alternateID = True, length = 128, notNone = True)
	rrCost = IntCol (default = None)
	positions = MultipleJoin ('Position')
	teams = MultipleJoin ('Team')


class Season (BizObject):
	class sqlmeta:
		defaultOrder = '-id'

	name = StringCol (length = 128, notNone = True)
	byes = MultipleJoin ('Bye')
	games = MultipleJoin ('Game')
	teams = RelatedJoin ('Team')

	def gamesAndByes(self):
		merged = self.byes[:] + self.games[:]
		merged.sort(key =  lambda x : x.date)
		return merged


class Skill (BizObject):
	class sqlmeta:
		defaultOrder = 'name'

	name = StringCol (alternateID = True, length = 128, notNone = True)
	description = StringCol (default = None)
	category = ForeignKey ('SkillCategory', notNone = True)
	players = RelatedJoin ('Player')
	positions = RelatedJoin ('Position')


class SkillCategory (BizObject):
	class sqlmeta:
		defaultOrder = 'id'

	name = StringCol (alternateID = True, length = 128, notNone = True)
	abbreviation = StringCol (alternateID = True, length = 1, notNone = True)
	skills = MultipleJoin ('Skill')


class Team (BizObject):
	class sqlmeta:
		defaultOrder = 'name'

	name = StringCol (length = 128, notNone = True)
	treasury = IntCol (default = 1000000, notNone = True)
	bank = IntCol (default = 0, notNone = True)
	ff = IntCol (default = 0, notNone = True)
	rr = IntCol (default = 0, notNone = True)
	assistantCoaches = IntCol (default = 0, notNone = True)
	cheerleaders = IntCol (default = 0, notNone = True)
	apothecary = BoolCol (default = 0)
	coach = ForeignKey ('Coach', notNone = True)
	race = ForeignKey ('Race', notNone = True)
	byes = MultipleJoin ('Bye')
	teamGames = MultipleJoin ('GameTeam')
	players = MultipleJoin ('Player')
	seasons = RelatedJoin ('Season')
	medals = MultipleJoin ('Medal')

	def activePlayers (self):
		return [p for p in self.players if p.isActive()]

	def availablePositions (self):
		available = []
		for position in self.race.positions:
			if self.positionCount(position) < position.max:
				available.append(position)
		return available

	def isNew (self):
		for teamGame in self.teamGames:
			if teamGame.game.isDone():
				return False
		return True

	def lastBye(self):
		last = None
		for bye in self.byes:
			if bye.date < datetime.datetime.now():
				if last is None or bye.date > last.date:
					last = bye
		return last

	def lastGame (self):
		last = None
		for teamGame in self.teamGames:
			if teamGame.game.isDone():
				if last is None or teamGame.game.date > last.date:
					last = teamGame.game
		return last

	def needsJourneymen (self):
		return not self.isNew() and len([p for p in self.players if not p.isMNG()]) < 11

	def positionCount (self, position):
		count = 0
		for player in self.players:
			if player.isActive() and player.position is position:
				count += 1
		return count

	def value (self):
		total = 0
		total += self.ff * 10000
		total += self.rr * self.race.rrCost
		total += self.treasury
		total += self.assistantCoaches * 10000
		total += self.cheerleaders * 10000
		if self.apothecary:
			total += 50000
		for player in self.players:
			total += player.value ()
		return total


### TABLE (RE)CREATION ####

def recreateTables():
	""" This now happens in order, so Postgres doesn't complain about preserving relationships. """
	dropTables()
	Season.createTable ()
	Race.createTable ()
	Coach.createTable ()
	Team.createTable ()
	Bye.createTable ()
	Game.createTable ()
	GameTeam.createTable ()
	Position.createTable ()
	Player.createTable ()
	GameTeamPlayer.createTable ()
	SkillCategory.createTable ()
	Skill.createTable ()

def dropTables():
	""" In reverse order """
	Skill.dropTable (True)
	SkillCategory.dropTable (True)
	GameTeamPlayer.dropTable (True)
	Player.dropTable (True)
	Position.dropTable (True)
	GameTeam.dropTable (True)
	Game.dropTable (True)
	Bye.dropTable (True)
	Team.dropTable (True)
	Coach.dropTable (True)
	Race.dropTable (True)
	Season.dropTable (True)



### DATA ###

def createSkills():
	# categories
	global GENERAL
	GENERAL = SkillCategory (name='General', abbreviation='G')
	global AGILITY
	AGILITY = SkillCategory (name='Agility', abbreviation='A')
	global PASSING
	PASSING = SkillCategory (name='Passing', abbreviation='P')
	global STRENGTH
	STRENGTH = SkillCategory (name='Strength', abbreviation='S')
	global MUTATION
	MUTATION = SkillCategory (name='Mutation', abbreviation='M')
	global EXTRAORDINARY
	EXTRAORDINARY = SkillCategory (name='Extraordinary', abbreviation='E')
	global STAT_INCREASE
	STAT_INCREASE = SkillCategory (name='Stat Increase', abbreviation='I')

	# stat increases
	global MA_INCREASE
	MA_INCREASE = Skill (name='+MA', categoryID=STAT_INCREASE.id)
	global ST_INCREASE
	ST_INCREASE = Skill (name='+ST', categoryID=STAT_INCREASE.id)
	global AG_INCREASE
	AG_INCREASE = Skill (name='+AG', categoryID=STAT_INCREASE.id)
	global AV_INCREASE
	AV_INCREASE = Skill (name='+AV', categoryID=STAT_INCREASE.id)

	# general skills
	global BLOCK
	BLOCK = Skill (name='Block', categoryID=GENERAL.id)
	global DAUNTLESS
	DAUNTLESS = Skill (name='Dauntless', categoryID=GENERAL.id)
	global DIRTY_PLAYER
	DIRTY_PLAYER = Skill (name='Dirty Player', categoryID=GENERAL.id)
	global FEND
	FEND = Skill (name='Fend', categoryID=GENERAL.id)
	global FRENZY
	FRENZY = Skill (name='Frenzy', categoryID=GENERAL.id)
	global KICK
	KICK = Skill (name='Kick', categoryID=GENERAL.id)
	global KICKOFF_RETURN
	KICKOFF_RETURN = Skill (name='Kick-off Return', categoryID=GENERAL.id)
	global PASS_BLOCK
	PASS_BLOCK = Skill (name='Pass Block', categoryID=GENERAL.id)
	global PRO
	PRO = Skill (name='Pro', categoryID=GENERAL.id)
	global SHADOWING
	SHADOWING = Skill (name='Shadowing', categoryID=GENERAL.id)
	global STRIP_BALL
	STRIP_BALL = Skill (name='Strip Ball', categoryID=GENERAL.id)
	global SURE_HANDS
	SURE_HANDS = Skill (name='Sure Hands', categoryID=GENERAL.id)
	global TACKLE
	TACKLE = Skill (name='Tackle', categoryID=GENERAL.id)
	global WRESTLE
	WRESTLE = Skill (name='Wrestle', categoryID=GENERAL.id)

	# agility skills
	global CATCH
	CATCH = Skill (name='Catch', categoryID=AGILITY.id)
	global DIVING_CATCH
	DIVING_CATCH = Skill (name='Diving Catch', categoryID=AGILITY.id)
	global DIVING_TACKLE
	DIVING_TACKLE = Skill (name='Diving Tackle', categoryID=AGILITY.id)
	global DODGE
	DODGE = Skill (name='Dodge', categoryID=AGILITY.id)
	global JUMP_UP
	JUMP_UP = Skill (name='Jump Up', categoryID=AGILITY.id)
	global LEAP
	LEAP = Skill (name='Leap', categoryID=AGILITY.id)
	global SIDE_STEP
	SIDE_STEP = Skill (name='Side Step', categoryID=AGILITY.id)
	global SNEAKY_GIT
	SNEAKY_GIT = Skill (name='Sneaky Git', categoryID=AGILITY.id)
	global SPRINT
	SPRINT = Skill (name='Sprint', categoryID=AGILITY.id)
	global SURE_FEET
	SURE_FEET = Skill (name='Sure Feet', categoryID=AGILITY.id)

	# passing skills
	global ACCURATE
	ACCURATE = Skill (name='Accurate', categoryID=PASSING.id)
	global DUMP_OFF
	DUMP_OFF = Skill (name='Dump-Off', categoryID=PASSING.id)
	global HAIL_MARY_PASS
	HAIL_MARY_PASS = Skill (name='Hail Mary Pass', categoryID=PASSING.id)
	global LEADER
	LEADER = Skill (name='Leader', categoryID=PASSING.id)
	global NERVES_OF_STEEL
	NERVES_OF_STEEL = Skill (name='Nerves of Steel', categoryID=PASSING.id)
	global PASS
	PASS = Skill (name='Pass', categoryID=PASSING.id)
	global SAFE_THROW
	SAFE_THROW = Skill (name='Safe Throw', categoryID=PASSING.id)

	# strength skills
	global BREAK_TACKLE
	BREAK_TACKLE = Skill (name='Break Tackle', categoryID=STRENGTH.id)
	global GRAB
	GRAB = Skill (name='Grab', categoryID=STRENGTH.id)
	global GUARD
	GUARD = Skill (name='Guard', categoryID=STRENGTH.id)
	global JUGGERNAUT
	JUGGERNAUT = Skill (name='Juggernaut', categoryID=STRENGTH.id)
	global MIGHTY_BLOW
	MIGHTY_BLOW = Skill (name='Mighty Blow', categoryID=STRENGTH.id)
	global MULTIPLE_BLOCK
	MULTIPLE_BLOCK = Skill (name='Multiple Block', categoryID=STRENGTH.id)
	global PILING_ON
	PILING_ON = Skill (name='Piling On', categoryID=STRENGTH.id)
	global STAND_FIRM
	STAND_FIRM = Skill (name='Stand Firm', categoryID=STRENGTH.id)
	global STRONG_ARM
	STRONG_ARM = Skill (name='Strong Arm', categoryID=STRENGTH.id)
	global THICK_SKULL
	THICK_SKULL = Skill (name='Thick Skull', categoryID=STRENGTH.id)

	# mutation skills
	global BIG_HAND
	BIG_HAND = Skill (name='Big Hand', categoryID=MUTATION.id)
	global CLAWS
	CLAWS = Skill (name='Claws', categoryID=MUTATION.id)
	global DISTURBING_PRESENCE
	DISTURBING_PRESENCE = Skill (name='Disturbing Presence', categoryID=MUTATION.id)
	global EXTRA_ARMS
	EXTRA_ARMS = Skill (name='Extra Arms', categoryID=MUTATION.id)
	global FOUL_APPEARANCE
	FOUL_APPEARANCE = Skill (name='Foul Appearance', categoryID=MUTATION.id)
	global HORNS
	HORNS = Skill (name='Horns', categoryID=MUTATION.id)
	global PREHENSILE_TAIL
	PREHENSILE_TAIL = Skill (name='Prehensile Tail', categoryID=MUTATION.id)
	global TENTACLES
	TENTACLES = Skill (name='Tentacles', categoryID=MUTATION.id)
	global TWO_HEADS
	TWO_HEADS = Skill (name='Two Heads', categoryID=MUTATION.id)
	global VERY_LONG_LEGS
	VERY_LONG_LEGS = Skill (name='Very Long Legs', categoryID=MUTATION.id)

	# extraordinary skills
	global ALWAYS_HUNGRY
	ALWAYS_HUNGRY = Skill (name='Always Hungry', categoryID=EXTRAORDINARY.id)
	global ANIMOSITY
	ANIMOSITY = Skill (name='Animosity', categoryID=EXTRAORDINARY.id)
	global BALL_AND_CHAIN
	BALL_AND_CHAIN = Skill (name='Ball & Chain', categoryID=EXTRAORDINARY.id)
	global BLOOD_LUST
	BLOOD_LUST = Skill (name='Blood Lust', categoryID=EXTRAORDINARY.id)
	global BOMBARDIER
	BOMBARDIER = Skill (name='Bombardier', categoryID=EXTRAORDINARY.id)
	global BONEHEAD
	BONEHEAD = Skill (name='Bonehead', categoryID=EXTRAORDINARY.id)
	global CHAINSAW
	CHAINSAW = Skill (name='Chainsaw', categoryID=EXTRAORDINARY.id)
	global DECAY
	DECAY = Skill (name='Decay', categoryID=EXTRAORDINARY.id)
	global EASILY_CONFUSED
	EASILY_CONFUSED = Skill (name='Easily Confused', categoryID=EXTRAORDINARY.id)
	global FAN_FAVORITE
	FAN_FAVORITE = Skill (name='Fan Favorite', categoryID=EXTRAORDINARY.id)
	global HYPNOTIC_GAZE
	HYPNOTIC_GAZE = Skill (name='Hypnotic Gaze', categoryID=EXTRAORDINARY.id)
	global LONER
	LONER = Skill (name='Loner', categoryID=EXTRAORDINARY.id)
	global NO_HANDS
	NO_HANDS = Skill (name='No Hands', categoryID=EXTRAORDINARY.id)
	global NURGLES_ROT
	NURGLES_ROT = Skill (name="Nurgle's Rot", categoryID=EXTRAORDINARY.id)
	global REALLY_STUPID
	REALLY_STUPID = Skill (name='Really Stupid', categoryID=EXTRAORDINARY.id)
	global REGENERATION
	REGENERATION = Skill (name='Regeneration', categoryID=EXTRAORDINARY.id)
	global RIGHT_STUFF
	RIGHT_STUFF = Skill (name='Right Stuff', categoryID=EXTRAORDINARY.id)
	global SECRET_WEAPON
	SECRET_WEAPON = Skill (name='Secret Weapon', categoryID=EXTRAORDINARY.id)
	global STAB
	STAB = Skill (name='Stab', categoryID=EXTRAORDINARY.id)
	global STAKES
	STAKES = Skill (name='Stakes', categoryID=EXTRAORDINARY.id)
	global STUNTY
	STUNTY = Skill (name='Stunty', categoryID=EXTRAORDINARY.id)
	global TAKE_ROOT
	TAKE_ROOT = Skill (name='Take Root', categoryID=EXTRAORDINARY.id)
	global THROW_TEAMMATE
	THROW_TEAMMATE = Skill (name='Throw Team-Mate', categoryID=EXTRAORDINARY.id)
	global TITCHY
	TITCHY = Skill (name='Titchy', categoryID=EXTRAORDINARY.id)
	global WILD_ANIMAL
	WILD_ANIMAL = Skill (name='Wild Animal', categoryID=EXTRAORDINARY.id)


def createAmazon():
	global AMAZON
	AMAZON = Race (name='Amazon', rrCost=50000)

	line = Position (raceID=AMAZON.id, name='Linewoman', ma=6, st=3, ag=3, av=7, cost=50000, max=16)
	line.addSkill(DODGE)
	line.addNormalAccess(GENERAL)
	line.addDoubleAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	catcher = Position (raceID=AMAZON.id, name='Catcher', ma=6, st=3, ag=3, av=7, cost=70000, max=2)
	catcher.addSkill(DODGE)
	catcher.addSkill(CATCH)
	catcher.addNormalAccess(GENERAL)
	catcher.addNormalAccess(AGILITY)
	catcher.addDoubleAccess(STRENGTH)
	catcher.addDoubleAccess(PASSING)

	thrower = Position (raceID=AMAZON.id, name='Thrower', ma=6, st=3, ag=3, av=7, cost=70000, max=2)
	thrower.addSkill(DODGE)
	thrower.addSkill(PASS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(AGILITY)
	thrower.addDoubleAccess(STRENGTH)

	blitzer = Position (raceID=AMAZON.id, name='Blitzer', ma=6, st=3, ag=3, av=7, cost=90000, max=4)
	blitzer.addSkill(BLOCK)
	blitzer.addSkill(DODGE)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(STRENGTH)
	blitzer.addDoubleAccess(AGILITY)
	blitzer.addDoubleAccess(PASSING)


def createChaos():
	global CHAOS
	CHAOS = Race (name='Chaos', rrCost=60000)

	beast = Position (raceID=CHAOS.id, name='Beastman', ma=6, st=3, ag=3, av=8, cost=60000, max=16)
	beast.addSkill(HORNS)
	beast.addNormalAccess(GENERAL)
	beast.addNormalAccess(STRENGTH)
	beast.addNormalAccess(MUTATION)
	beast.addDoubleAccess(AGILITY)
	beast.addDoubleAccess(PASSING)

	warrior = Position (raceID=CHAOS.id, name='Chaos Warrior', ma=5, st=4, ag=3, av=9, cost=100000, max=4)
	warrior.addNormalAccess(GENERAL)
	warrior.addNormalAccess(STRENGTH)
	warrior.addNormalAccess(MUTATION)
	warrior.addDoubleAccess(AGILITY)
	warrior.addDoubleAccess(PASSING)

	minotaur = Position (raceID=CHAOS.id, name='Minotaur', ma=5, st=5, ag=2, av=8, cost=150000, max=1)
	minotaur.addSkill(LONER)
	minotaur.addSkill(FRENZY)
	minotaur.addSkill(HORNS)
	minotaur.addSkill(MIGHTY_BLOW)
	minotaur.addSkill(THICK_SKULL)
	minotaur.addSkill(WILD_ANIMAL)
	minotaur.addNormalAccess(STRENGTH)
	minotaur.addNormalAccess(MUTATION)
	minotaur.addDoubleAccess(GENERAL)
	minotaur.addDoubleAccess(AGILITY)
	minotaur.addDoubleAccess(PASSING)


def createChaosDwarf():
	global CHAOS_DWARF
	CHAOS_DWARF = Race (name='Chaos Dwarf', rrCost=70000)

	hob = Position (raceID=CHAOS_DWARF.id, name='Hobgoblin', ma=6, st=3, ag=3, av=7, cost=40000, max=16)
	hob.addNormalAccess(GENERAL)
	hob.addDoubleAccess(AGILITY)
	hob.addDoubleAccess(STRENGTH)
	hob.addDoubleAccess(PASSING)

	cdb = Position (raceID=CHAOS_DWARF.id, name='Chaos Dwarf Blocker', ma=4, st=3, ag=2, av=9, cost=70000, max=6)
	cdb.addSkill(BLOCK)
	cdb.addSkill(TACKLE)
	cdb.addSkill(THICK_SKULL)
	cdb.addNormalAccess(GENERAL)
	cdb.addNormalAccess(STRENGTH)
	cdb.addDoubleAccess(AGILITY)
	cdb.addDoubleAccess(PASSING)
	cdb.addDoubleAccess(MUTATION)

	bc = Position (raceID=CHAOS_DWARF.id, name='Bull Centaur', ma=6, st=4, ag=2, av=9, cost=130000, max=2)
	bc.addSkill(SPRINT)
	bc.addSkill(SURE_FEET)
	bc.addSkill(THICK_SKULL)
	bc.addNormalAccess(GENERAL)
	bc.addNormalAccess(STRENGTH)
	bc.addDoubleAccess(AGILITY)
	bc.addDoubleAccess(PASSING)

	minotaur = Position (raceID=CHAOS_DWARF.id, name='Minotaur', ma=5, st=5, ag=2, av=8, cost=150000, max=1)
	minotaur.addSkill(LONER)
	minotaur.addSkill(FRENZY)
	minotaur.addSkill(HORNS)
	minotaur.addSkill(MIGHTY_BLOW)
	minotaur.addSkill(THICK_SKULL)
	minotaur.addSkill(WILD_ANIMAL)
	minotaur.addNormalAccess(STRENGTH)
	minotaur.addDoubleAccess(GENERAL)
	minotaur.addDoubleAccess(AGILITY)
	minotaur.addDoubleAccess(PASSING)
	minotaur.addDoubleAccess(MUTATION)


def createChaosPact():
	global CHAOS_PACT
	CHAOS_PACT = Race (name='Chaos Pact', rrCost=70000)

	marauder = Position (raceID=CHAOS_PACT.id, name='Marauder', ma=6, st=3, ag=3, av=8, cost=50000, max=12)
	marauder.addNormalAccess(GENERAL)
	marauder.addNormalAccess(STRENGTH)
	marauder.addNormalAccess(PASSING)
	marauder.addNormalAccess(MUTATION)
	marauder.addDoubleAccess(AGILITY)

	goblin = Position (raceID=CHAOS_PACT.id, name='Goblin Renegade', ma=6, st=2, ag=3, av=7, cost=40000, max=1)
	goblin.addSkill(ANIMOSITY)
	goblin.addSkill(DODGE)
	goblin.addSkill(RIGHT_STUFF)
	goblin.addSkill(STUNTY)
	goblin.addNormalAccess(AGILITY)
	goblin.addNormalAccess(MUTATION)
	goblin.addDoubleAccess(GENERAL)
	goblin.addDoubleAccess(STRENGTH)
	goblin.addDoubleAccess(PASSING)

	skaven = Position (raceID=CHAOS_PACT.id, name='Skaven Renegade', ma=7, st=3, ag=3, av=7, cost=50000, max=1)
	skaven.addSkill(ANIMOSITY)
	skaven.addNormalAccess(GENERAL)
	skaven.addNormalAccess(MUTATION)
	skaven.addDoubleAccess(AGILITY)
	skaven.addDoubleAccess(STRENGTH)
	skaven.addDoubleAccess(PASSING)

	elf = Position (raceID=CHAOS_PACT.id, name='Dark Elf Renegade', ma=6, st=3, ag=4, av=8, cost=70000, max=1)
	elf.addSkill(ANIMOSITY)
	elf.addNormalAccess(GENERAL)
	elf.addNormalAccess(AGILITY)
	elf.addNormalAccess(MUTATION)
	elf.addDoubleAccess(STRENGTH)
	elf.addDoubleAccess(PASSING)

	troll = Position (raceID=CHAOS_PACT.id, name='Chaos Troll', ma=4, st=5, ag=1, av=9, cost=110000, max=1)
	troll.addSkill(LONER)
	troll.addSkill(ALWAYS_HUNGRY)
	troll.addSkill(MIGHTY_BLOW)
	troll.addSkill(REALLY_STUPID)
	troll.addSkill(REGENERATION)
	troll.addSkill(THROW_TEAMMATE)
	troll.addNormalAccess(STRENGTH)
	troll.addDoubleAccess(GENERAL)
	troll.addDoubleAccess(AGILITY)
	troll.addDoubleAccess(PASSING)
	troll.addDoubleAccess(MUTATION)

	ogre = Position (raceID=CHAOS_PACT.id, name='Chaos Ogre', ma=5, st=5, ag=2, av=9, cost=140000, max=1)
	ogre.addSkill(LONER)
	ogre.addSkill(BONEHEAD)
	ogre.addSkill(MIGHTY_BLOW)
	ogre.addSkill(THICK_SKULL)
	ogre.addSkill(THROW_TEAMMATE)
	ogre.addNormalAccess(STRENGTH)
	ogre.addDoubleAccess(GENERAL)
	ogre.addDoubleAccess(AGILITY)
	ogre.addDoubleAccess(PASSING)
	ogre.addDoubleAccess(MUTATION)

	minotaur = Position (raceID=CHAOS_PACT.id, name='Minotaur', ma=5, st=5, ag=2, av=8, cost=150000, max=1)
	minotaur.addSkill(LONER)
	minotaur.addSkill(FRENZY)
	minotaur.addSkill(HORNS)
	minotaur.addSkill(MIGHTY_BLOW)
	minotaur.addSkill(THICK_SKULL)
	minotaur.addSkill(WILD_ANIMAL)
	minotaur.addNormalAccess(STRENGTH)
	minotaur.addDoubleAccess(GENERAL)
	minotaur.addDoubleAccess(AGILITY)
	minotaur.addDoubleAccess(PASSING)
	minotaur.addDoubleAccess(MUTATION)


def createDarkElf():
	global DARK_ELF
	DARK_ELF = Race(name='Dark Elf', rrCost=50000)

	line = Position(raceID=DARK_ELF.id, name='Lineman', ma=6, st=3, ag=4, av=8, cost=70000, max=16)
	line.addNormalAccess(GENERAL)
	line.addNormalAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	runner = Position(raceID=DARK_ELF.id, name='Runner', ma=7, st=3, ag=4, av=7, cost=80000, max=2)
	runner.addSkill(DUMP_OFF)
	runner.addNormalAccess(GENERAL)
	runner.addNormalAccess(AGILITY)
	runner.addNormalAccess(PASSING)
	runner.addDoubleAccess(STRENGTH)

	assassin = Position(raceID=DARK_ELF.id, name='Assassin', ma=6, st=3, ag=4, av=7, cost=90000, max=2)
	assassin.addSkill(SHADOWING)
	assassin.addSkill(STAB)
	assassin.addNormalAccess(GENERAL)
	assassin.addNormalAccess(AGILITY)
	assassin.addDoubleAccess(STRENGTH)
	assassin.addDoubleAccess(PASSING)

	blitzer = Position(raceID=DARK_ELF.id, name='Blitzer', ma=7, st=3, ag=4, av=8, cost=100000, max=4)
	blitzer.addSkill(BLOCK)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(AGILITY)
	blitzer.addDoubleAccess(STRENGTH)
	blitzer.addDoubleAccess(PASSING)

	witch = Position(raceID=DARK_ELF.id, name='Witch Elf', ma=7, st=3, ag=4, av=7, cost=110000, max=2)
	witch.addSkill(FRENZY)
	witch.addSkill(DODGE)
	witch.addSkill(JUMP_UP)
	witch.addNormalAccess(GENERAL)
	witch.addNormalAccess(AGILITY)
	witch.addDoubleAccess(STRENGTH)
	witch.addDoubleAccess(PASSING)


def createDwarf():
	global DWARF
	DWARF = Race(name='Dwarf', rrCost=50000)

	blocker = Position(raceID=DWARF.id, name='Blocker', ma=4, st=3, ag=2, av=9, cost=70000, max=16)
	blocker.addSkill(BLOCK)
	blocker.addSkill(TACKLE)
	blocker.addSkill(THICK_SKULL)
	blocker.addNormalAccess(GENERAL)
	blocker.addNormalAccess(STRENGTH)
	blocker.addDoubleAccess(AGILITY)
	blocker.addDoubleAccess(PASSING)

	runner = Position(raceID=DWARF.id, name='Runner', ma=6, st=3, ag=3, av=8, cost=80000, max=2)
	runner.addSkill(SURE_HANDS)
	runner.addSkill(THICK_SKULL)
	runner.addNormalAccess(GENERAL)
	runner.addNormalAccess(PASSING)
	runner.addDoubleAccess(AGILITY)
	runner.addDoubleAccess(STRENGTH)

	blitzer = Position(raceID=DWARF.id, name='Blitzer', ma=5, st=3, ag=3, av=9, cost=80000, max=2)
	blitzer.addSkill(BLOCK)
	blitzer.addSkill(THICK_SKULL)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(STRENGTH)
	blitzer.addDoubleAccess(AGILITY)
	blitzer.addDoubleAccess(PASSING)

	slayer = Position(raceID=DWARF.id, name='Troll Slayer', ma=5, st=3, ag=2, av=8, cost=90000, max=2)
	slayer.addSkill(BLOCK)
	slayer.addSkill(DAUNTLESS)
	slayer.addSkill(FRENZY)
	slayer.addSkill(THICK_SKULL)
	slayer.addNormalAccess(GENERAL)
	slayer.addNormalAccess(STRENGTH)
	slayer.addDoubleAccess(AGILITY)
	slayer.addDoubleAccess(PASSING)

	roller = Position(raceID=DWARF.id, name='Deathroller', ma=4, st=7, ag=1, av=10, cost=160000, max=1)
	roller.addSkill(BREAK_TACKLE)
	roller.addSkill(DIRTY_PLAYER)
	roller.addSkill(JUGGERNAUT)
	roller.addSkill(LONER)
	roller.addSkill(MIGHTY_BLOW)
	roller.addSkill(NO_HANDS)
	roller.addSkill(SECRET_WEAPON)
	roller.addSkill(STAND_FIRM)
	roller.addNormalAccess(STRENGTH)
	roller.addDoubleAccess(GENERAL)
	roller.addDoubleAccess(AGILITY)
	roller.addDoubleAccess(PASSING)


def createElf():
	global ELF
	ELF = Race(name='Elf', rrCost=50000)

	line = Position(raceID=ELF.id, name='Lineman', ma=6, st=3, ag=4, av=7, cost=60000, max=16)
	line.addNormalAccess(GENERAL)
	line.addNormalAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	thrower = Position(raceID=ELF.id, name='Thrower', ma=6, st=3, ag=4, av=7, cost=70000, max=2)
	thrower.addSkill(PASS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(AGILITY)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(STRENGTH)

	catcher = Position(raceID=ELF.id, name='Catcher', ma=8, st=3, ag=4, av=7, cost=100000, max=4)
	catcher.addSkill(CATCH)
	catcher.addSkill(NERVES_OF_STEEL)
	catcher.addNormalAccess(GENERAL)
	catcher.addNormalAccess(AGILITY)
	catcher.addDoubleAccess(STRENGTH)
	catcher.addDoubleAccess(PASSING)

	blitzer = Position(raceID=ELF.id, name='Blitzer', ma=7, st=3, ag=4, av=8, cost=110000, max=2)
	blitzer.addSkill(BLOCK)
	blitzer.addSkill(SIDE_STEP)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(AGILITY)
	blitzer.addDoubleAccess(STRENGTH)
	blitzer.addDoubleAccess(PASSING)


def createGoblin():
	global GOBLIN
	GOBLIN = Race(name='Goblin', rrCost=60000)

	gobbo = Position(raceID=GOBLIN.id, name='Goblin', ma=6, st=2, ag=3, av=7, cost=40000, max=16)
	gobbo.addSkill(DODGE)
	gobbo.addSkill(RIGHT_STUFF)
	gobbo.addSkill(STUNTY)
	gobbo.addNormalAccess(AGILITY)
	gobbo.addDoubleAccess(GENERAL)
	gobbo.addDoubleAccess(STRENGTH)
	gobbo.addDoubleAccess(PASSING)

	bomb = Position(raceID=GOBLIN.id, name='Bombardier', ma=6, st=2, ag=3, av=7, cost=40000, max=1)
	bomb.addSkill(BOMBARDIER)
	bomb.addSkill(DODGE)
	bomb.addSkill(SECRET_WEAPON)
	bomb.addSkill(STUNTY)
	bomb.addNormalAccess(AGILITY)
	bomb.addDoubleAccess(GENERAL)
	bomb.addDoubleAccess(STRENGTH)
	bomb.addDoubleAccess(PASSING)

	pogo = Position(raceID=GOBLIN.id, name='Pogoer', ma=7, st=2, ag=3, av=7, cost=40000, max=1)
	pogo.addSkill(DODGE)
	pogo.addSkill(LEAP)
	pogo.addSkill(SECRET_WEAPON)
	pogo.addSkill(STUNTY)
	pogo.addSkill(VERY_LONG_LEGS)
	pogo.addNormalAccess(AGILITY)
	pogo.addDoubleAccess(GENERAL)
	pogo.addDoubleAccess(STRENGTH)
	pogo.addDoubleAccess(PASSING)

	loon = Position(raceID=GOBLIN.id, name='Looney', ma=6, st=2, ag=3, av=7, cost=40000, max=1)
	loon.addSkill(CHAINSAW)
	loon.addSkill(SECRET_WEAPON)
	loon.addSkill(STUNTY)
	loon.addNormalAccess(AGILITY)
	loon.addDoubleAccess(GENERAL)
	loon.addDoubleAccess(STRENGTH)
	loon.addDoubleAccess(PASSING)

	fanatic = Position(raceID=GOBLIN.id, name='Fanatic', ma=3, st=7, ag=3, av=7, cost=70000, max=1)
	fanatic.addSkill(BALL_AND_CHAIN)
	fanatic.addSkill(NO_HANDS)
	fanatic.addSkill(SECRET_WEAPON)
	fanatic.addSkill(STUNTY)
	fanatic.addNormalAccess(STRENGTH)
	fanatic.addDoubleAccess(GENERAL)
	fanatic.addDoubleAccess(AGILITY)
	fanatic.addDoubleAccess(PASSING)

	troll = Position(raceID=GOBLIN.id, name='Troll', ma=4, st=5, ag=1, av=9, cost=110000, max=2)
	troll.addSkill(LONER)
	troll.addSkill(ALWAYS_HUNGRY)
	troll.addSkill(MIGHTY_BLOW)
	troll.addSkill(REALLY_STUPID)
	troll.addSkill(REGENERATION)
	troll.addSkill(THROW_TEAMMATE)
	troll.addNormalAccess(STRENGTH)
	troll.addDoubleAccess(GENERAL)
	troll.addDoubleAccess(AGILITY)
	troll.addDoubleAccess(PASSING)


def createHalfling():
	global HALFLING
	HALFLING = Race(name='Halfling', rrCost=60000)

	ling = Position(raceID=HALFLING.id, name='Halfling', ma=5, st=2, ag=3, av=6, cost=30000, max=16)
	ling.addSkill(DODGE)
	ling.addSkill(RIGHT_STUFF)
	ling.addSkill(STUNTY)
	ling.addNormalAccess(AGILITY)
	ling.addDoubleAccess(GENERAL)
	ling.addDoubleAccess(STRENGTH)
	ling.addDoubleAccess(PASSING)

	tree = Position(raceID=HALFLING.id, name='Treeman', ma=2, st=6, ag=1, av=10, cost=120000, max=2)
	tree.addSkill(MIGHTY_BLOW)
	tree.addSkill(STAND_FIRM)
	tree.addSkill(STRONG_ARM)
	tree.addSkill(TAKE_ROOT)
	tree.addSkill(THICK_SKULL)
	tree.addSkill(THROW_TEAMMATE)
	tree.addNormalAccess(STRENGTH)
	tree.addDoubleAccess(GENERAL)
	tree.addDoubleAccess(AGILITY)
	tree.addDoubleAccess(PASSING)


def createHighElf():
	global HIGH_ELF
	HIGH_ELF = Race(name='High Elf', rrCost=50000)

	line = Position(raceID=HIGH_ELF.id, name='Lineman', ma=6, st=3, ag=4, av=8, cost=70000, max=16)
	line.addNormalAccess(GENERAL)
	line.addNormalAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	thrower = Position(raceID=HIGH_ELF.id, name='Thrower', ma=6, st=3, ag=4, av=8, cost=90000, max=2)
	thrower.addSkill(PASS)
	thrower.addSkill(SAFE_THROW)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(AGILITY)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(STRENGTH)

	catcher = Position(raceID=HIGH_ELF.id, name='Catcher', ma=8, st=3, ag=4, av=7, cost=90000, max=4)
	catcher.addSkill(CATCH)
	catcher.addNormalAccess(GENERAL)
	catcher.addNormalAccess(AGILITY)
	catcher.addDoubleAccess(STRENGTH)
	catcher.addDoubleAccess(PASSING)

	blitzer = Position(raceID=HIGH_ELF.id, name='Blitzer', ma=7, st=3, ag=4, av=8, cost=100000, max=2)
	blitzer.addSkill(BLOCK)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(AGILITY)
	blitzer.addDoubleAccess(STRENGTH)
	blitzer.addDoubleAccess(PASSING)


def createHuman():
	global HUMAN
	HUMAN = Race(name='Human', rrCost=50000)

	line = Position(raceID=HUMAN.id, name='Lineman', ma=6, st=3, ag=3, av=8, cost=50000, max=16)
	line.addNormalAccess(GENERAL)
	line.addDoubleAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	catcher = Position(raceID=HUMAN.id, name='Catcher', ma=8, st=2, ag=3, av=7, cost=70000, max=4)
	catcher.addSkill(CATCH)
	catcher.addSkill(DODGE)
	catcher.addNormalAccess(GENERAL)
	catcher.addNormalAccess(AGILITY)
	catcher.addDoubleAccess(STRENGTH)
	catcher.addDoubleAccess(PASSING)

	thrower = Position(raceID=HUMAN.id, name='Thrower', ma=6, st=3, ag=3, av=8, cost=70000, max=2)
	thrower.addSkill(SURE_HANDS)
	thrower.addSkill(PASS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(AGILITY)
	thrower.addDoubleAccess(STRENGTH)

	blitzer = Position(raceID=HUMAN.id, name='Blitzer', ma=7, st=3, ag=3, av=8, cost=90000, max=4)
	blitzer.addSkill(BLOCK)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(STRENGTH)
	blitzer.addDoubleAccess(AGILITY)
	blitzer.addDoubleAccess(PASSING)

	ogre = Position(raceID=HUMAN.id, name='Ogre', ma=5, st=5, ag=2, av=9, cost=140000, max=1)
	ogre.addSkill(LONER)
	ogre.addSkill(BONEHEAD)
	ogre.addSkill(MIGHTY_BLOW)
	ogre.addSkill(THICK_SKULL)
	ogre.addSkill(THROW_TEAMMATE)
	ogre.addNormalAccess(STRENGTH)
	ogre.addDoubleAccess(GENERAL)
	ogre.addDoubleAccess(AGILITY)
	ogre.addDoubleAccess(PASSING)


def createKhemri():
	global KHEMRI
	KHEMRI = Race(name='Khemri', rrCost=70000)

	skelly = Position(raceID=KHEMRI.id, name='Skeleton', ma=5, st=3, ag=2, av=7, cost=40000, max=16)
	skelly.addSkill(REGENERATION)
	skelly.addSkill(THICK_SKULL)
	skelly.addNormalAccess(GENERAL)
	skelly.addDoubleAccess(AGILITY)
	skelly.addDoubleAccess(STRENGTH)
	skelly.addDoubleAccess(PASSING)

	throra = Position(raceID=KHEMRI.id, name='Thro-Ra', ma=6, st=3, ag=2, av=7, cost=70000, max=2)
	throra.addSkill(PASS)
	throra.addSkill(REGENERATION)
	throra.addSkill(SURE_HANDS)
	throra.addNormalAccess(GENERAL)
	throra.addNormalAccess(PASSING)
	throra.addDoubleAccess(AGILITY)
	throra.addDoubleAccess(STRENGTH)

	blitzra = Position(raceID=KHEMRI.id, name='Blitz-Ra', ma=6, st=3, ag=2, av=8, cost=90000, max=2)
	blitzra.addSkill(BLOCK)
	blitzra.addSkill(REGENERATION)
	blitzra.addNormalAccess(GENERAL)
	blitzra.addNormalAccess(STRENGTH)
	blitzra.addDoubleAccess(AGILITY)
	blitzra.addDoubleAccess(PASSING)

	mummy = Position(raceID=KHEMRI.id, name='Tomb Guardian', ma=4, st=5, ag=1, av=9, cost=100000, max=4)
	mummy.addSkill(DECAY)
	mummy.addSkill(REGENERATION)
	mummy.addNormalAccess(STRENGTH)
	mummy.addDoubleAccess(AGILITY)
	mummy.addDoubleAccess(GENERAL)
	mummy.addDoubleAccess(PASSING)


def createLizardman():
	global LIZARDMAN
	LIZARDMAN = Race(name='Lizardman', rrCost=60000)

	skink = Position(raceID=LIZARDMAN.id, name='Skink', ma=8, st=2, ag=3, av=7, cost=60000, max=16)
	skink.addSkill(DODGE)
	skink.addSkill(STUNTY)
	skink.addNormalAccess(AGILITY)
	skink.addDoubleAccess(GENERAL)
	skink.addDoubleAccess(STRENGTH)
	skink.addDoubleAccess(PASSING)

	saurus = Position(raceID=LIZARDMAN.id, name='Saurus', ma=6, st=4, ag=1, av=9, cost=80000, max=6)
	saurus.addNormalAccess(GENERAL)
	saurus.addNormalAccess(STRENGTH)
	saurus.addDoubleAccess(AGILITY)
	saurus.addDoubleAccess(PASSING)

	krox = Position(raceID=LIZARDMAN.id, name='Kroxigor', ma=6, st=5, ag=1, av=9, cost=140000, max=1)
	krox.addSkill(LONER)
	krox.addSkill(BONEHEAD)
	krox.addSkill(MIGHTY_BLOW)
	krox.addSkill(PREHENSILE_TAIL)
	krox.addSkill(THICK_SKULL)
	krox.addNormalAccess(STRENGTH)
	krox.addDoubleAccess(GENERAL)
	krox.addDoubleAccess(AGILITY)
	krox.addDoubleAccess(PASSING)


def createNecromantic():
	global NECROMANTIC
	NECROMANTIC = Race(name='Necromantic', rrCost=70000)

	zomb = Position(raceID=NECROMANTIC.id, name='Zombie', ma=4, st=3, ag=2, av=8, cost=40000, max=16)
	zomb.addSkill(REGENERATION)
	zomb.addNormalAccess(GENERAL)
	zomb.addDoubleAccess(AGILITY)
	zomb.addDoubleAccess(STRENGTH)
	zomb.addDoubleAccess(PASSING)

	ghoul = Position(raceID=NECROMANTIC.id, name='Ghoul', ma=7, st=3, ag=3, av=7, cost=70000, max=2)
	ghoul.addSkill(DODGE)
	ghoul.addNormalAccess(GENERAL)
	ghoul.addNormalAccess(AGILITY)
	ghoul.addDoubleAccess(STRENGTH)
	ghoul.addDoubleAccess(PASSING)

	wight = Position(raceID=NECROMANTIC.id, name='Wight', ma=6, st=3, ag=3, av=8, cost=90000, max=2)
	wight.addSkill(BLOCK)
	wight.addSkill(REGENERATION)
	wight.addNormalAccess(GENERAL)
	wight.addNormalAccess(STRENGTH)
	wight.addDoubleAccess(AGILITY)
	wight.addDoubleAccess(PASSING)

	flesh = Position(raceID=NECROMANTIC.id, name='Flesh Golem', ma=4, st=4, ag=2, av=9, cost=100000, max=2)
	flesh.addSkill(REGENERATION)
	flesh.addSkill(STAND_FIRM)
	flesh.addSkill(THICK_SKULL)
	flesh.addNormalAccess(GENERAL)
	flesh.addNormalAccess(STRENGTH)
	flesh.addDoubleAccess(AGILITY)
	flesh.addDoubleAccess(PASSING)

	were = Position(raceID=NECROMANTIC.id, name='Werewolf', ma=8, st=3, ag=3, av=8, cost=120000, max=2)
	were.addSkill(CLAWS)
	were.addSkill(FRENZY)
	were.addSkill(REGENERATION)
	were.addNormalAccess(GENERAL)
	were.addNormalAccess(AGILITY)
	were.addDoubleAccess(STRENGTH)
	were.addDoubleAccess(PASSING)


def createNorse():
	global NORSE
	NORSE = Race(name='Norse', rrCost=60000)

	line = Position(raceID=NORSE.id, name='Lineman', ma=6, st=3, ag=3, av=7, cost=50000, max=16)
	line.addSkill(BLOCK)
	line.addNormalAccess(GENERAL)
	line.addDoubleAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	thrower = Position(raceID=NORSE.id, name='Thrower', ma=6, st=3, ag=3, av=7, cost=70000, max=2)
	thrower.addSkill(BLOCK)
	thrower.addSkill(PASS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(AGILITY)
	thrower.addDoubleAccess(STRENGTH)

	runner = Position(raceID=NORSE.id, name='Runner', ma=7, st=3, ag=3, av=7, cost=90000, max=2)
	runner.addSkill(BLOCK)
	runner.addSkill(DAUNTLESS)
	runner.addNormalAccess(GENERAL)
	runner.addNormalAccess(AGILITY)
	runner.addDoubleAccess(STRENGTH)
	runner.addDoubleAccess(PASSING)

	berserker = Position(raceID=NORSE.id, name='Berserker', ma=6, st=3, ag=3, av=7, cost=90000, max=2)
	berserker.addSkill(BLOCK)
	berserker.addSkill(FRENZY)
	berserker.addSkill(JUMP_UP)
	berserker.addNormalAccess(GENERAL)
	berserker.addNormalAccess(STRENGTH)
	berserker.addDoubleAccess(AGILITY)
	berserker.addDoubleAccess(PASSING)

	ulfwerener = Position(raceID=NORSE.id, name='Ulfwerener', ma=6, st=4, ag=2, av=8, cost=110000, max=2)
	ulfwerener.addSkill(FRENZY)
	ulfwerener.addNormalAccess(GENERAL)
	ulfwerener.addNormalAccess(STRENGTH)
	ulfwerener.addDoubleAccess(AGILITY)
	ulfwerener.addDoubleAccess(PASSING)

	troll = Position(raceID=NORSE.id, name='Snow Troll', ma=5, st=5, ag=1, av=8, cost=140000, max=1)
	troll.addSkill(LONER)
	troll.addSkill(CLAWS)
	troll.addSkill(DISTURBING_PRESENCE)
	troll.addSkill(FRENZY)
	troll.addSkill(WILD_ANIMAL)
	troll.addNormalAccess(STRENGTH)
	troll.addDoubleAccess(GENERAL)
	troll.addDoubleAccess(AGILITY)
	troll.addDoubleAccess(PASSING)


def createNurgle():
	global NURGLE
	NURGLE = Race(name='Nurgle', rrCost=70000)

	rotter = Position(raceID=NURGLE.id, name='Rotter', ma=5, st=3, ag=3, av=8, cost=40000, max=16)
	rotter.addSkill(DECAY)
	rotter.addSkill(NURGLES_ROT)
	rotter.addNormalAccess(GENERAL)
	rotter.addNormalAccess(MUTATION)
	rotter.addDoubleAccess(AGILITY)
	rotter.addDoubleAccess(STRENGTH)
	rotter.addDoubleAccess(PASSING)

	pestigor = Position(raceID=NURGLE.id, name='Pestigor', ma=6, st=3, ag=3, av=8, cost=80000, max=4)
	pestigor.addSkill(HORNS)
	pestigor.addSkill(NURGLES_ROT)
	pestigor.addSkill(REGENERATION)
	pestigor.addNormalAccess(GENERAL)
	pestigor.addNormalAccess(STRENGTH)
	pestigor.addNormalAccess(MUTATION)
	pestigor.addDoubleAccess(AGILITY)
	pestigor.addDoubleAccess(PASSING)

	warrior = Position(raceID=NURGLE.id, name='Nurgle Warrior', ma=4, st=4, ag=2, av=9, cost=110000, max=4)
	warrior.addSkill(DISTURBING_PRESENCE)
	warrior.addSkill(FOUL_APPEARANCE)
	warrior.addSkill(NURGLES_ROT)
	warrior.addSkill(REGENERATION)
	warrior.addNormalAccess(GENERAL)
	warrior.addNormalAccess(STRENGTH)
	warrior.addNormalAccess(MUTATION)
	warrior.addDoubleAccess(AGILITY)
	warrior.addDoubleAccess(PASSING)

	beast = Position(raceID=NURGLE.id, name='Beast of Nurgle', ma=4, st=5, ag=1, av=9, cost=140000, max=1)
	beast.addSkill(LONER)
	beast.addSkill(DISTURBING_PRESENCE)
	beast.addSkill(FOUL_APPEARANCE)
	beast.addSkill(MIGHTY_BLOW)
	beast.addSkill(NURGLES_ROT)
	beast.addSkill(REALLY_STUPID)
	beast.addSkill(REGENERATION)
	beast.addSkill(TENTACLES)
	beast.addNormalAccess(STRENGTH)
	beast.addDoubleAccess(GENERAL)
	beast.addDoubleAccess(AGILITY)
	beast.addDoubleAccess(PASSING)
	beast.addDoubleAccess(MUTATION)


def createOgre():
	global OGRE
	OGRE = Race(name='Ogre', rrCost=70000)

	snot = Position(raceID=OGRE.id, name='Snotling', ma=5, st=1, ag=3, av=5, cost=20000, max=16)
	snot.addSkill(DODGE)
	snot.addSkill(RIGHT_STUFF)
	snot.addSkill(SIDE_STEP)
	snot.addSkill(STUNTY)
	snot.addSkill(TITCHY)
	snot.addNormalAccess(AGILITY)
	snot.addDoubleAccess(GENERAL)
	snot.addDoubleAccess(STRENGTH)
	snot.addDoubleAccess(PASSING)

	ogre = Position(raceID=OGRE.id, name='Ogre', ma=5, st=5, ag=2, av=9, cost=140000, max=6)
	ogre.addSkill(BONEHEAD)
	ogre.addSkill(MIGHTY_BLOW)
	ogre.addSkill(THICK_SKULL)
	ogre.addSkill(THROW_TEAMMATE)
	ogre.addNormalAccess(STRENGTH)
	ogre.addDoubleAccess(GENERAL)
	ogre.addDoubleAccess(AGILITY)
	ogre.addDoubleAccess(PASSING)


def createOrc():
	global ORC
	ORC = Race(name='Orc', rrCost=60000)

	line = Position(raceID=ORC.id, name='Lineman', ma=5, st=3, ag=3, av=9, cost=50000, max=16)
	line.addNormalAccess(GENERAL)
	line.addDoubleAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	gobbo = Position(raceID=ORC.id, name='Goblin', ma=6, st=2, ag=3, av=7, cost=40000, max=4)
	gobbo.addSkill(DODGE)
	gobbo.addSkill(RIGHT_STUFF)
	gobbo.addSkill(STUNTY)
	gobbo.addNormalAccess(AGILITY)
	gobbo.addDoubleAccess(GENERAL)
	gobbo.addDoubleAccess(STRENGTH)
	gobbo.addDoubleAccess(PASSING)

	thrower = Position(raceID=ORC.id, name='Thrower', ma=5, st=3, ag=3, av=8, cost=70000, max=2)
	thrower.addSkill(SURE_HANDS)
	thrower.addSkill(PASS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(AGILITY)
	thrower.addDoubleAccess(STRENGTH)

	blocker = Position(raceID=ORC.id, name='Blocker', ma=4, st=4, ag=2, av=9, cost=80000, max=4)
	blocker.addNormalAccess(GENERAL)
	blocker.addNormalAccess(STRENGTH)
	blocker.addDoubleAccess(AGILITY)
	blocker.addDoubleAccess(PASSING)

	blitzer = Position(raceID=ORC.id, name='Blitzer', ma=6, st=3, ag=3, av=9, cost=80000, max=4)
	blitzer.addSkill(BLOCK)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(STRENGTH)
	blitzer.addDoubleAccess(AGILITY)
	blitzer.addDoubleAccess(PASSING)

	troll = Position(raceID=ORC.id, name='Troll', ma=4, st=5, ag=1, av=9, cost=110000, max=1)
	troll.addSkill(LONER)
	troll.addSkill(ALWAYS_HUNGRY)
	troll.addSkill(MIGHTY_BLOW)
	troll.addSkill(REALLY_STUPID)
	troll.addSkill(REGENERATION)
	troll.addSkill(THROW_TEAMMATE)
	troll.addNormalAccess(STRENGTH)
	troll.addDoubleAccess(GENERAL)
	troll.addDoubleAccess(AGILITY)
	troll.addDoubleAccess(PASSING)


def createSkaven():
	global SKAVEN
	SKAVEN = Race(name='Skaven', rrCost=60000)

	line = Position(raceID=SKAVEN.id, name='Lineman', ma=7, st=3, ag=3, av=7, cost=50000, max=16)
	line.addNormalAccess(GENERAL)
	line.addDoubleAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)
	line.addDoubleAccess(MUTATION)

	thrower = Position(raceID=SKAVEN.id, name='Thrower', ma=7, st=3, ag=3, av=7, cost=70000, max=2)
	thrower.addSkill(PASS)
	thrower.addSkill(SURE_HANDS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(AGILITY)
	thrower.addDoubleAccess(STRENGTH)
	thrower.addDoubleAccess(MUTATION)

	runner = Position(raceID=SKAVEN.id, name='Runner', ma=9, st=2, ag=4, av=7, cost=80000, max=4)
	runner.addSkill(DODGE)
	runner.addNormalAccess(GENERAL)
	runner.addNormalAccess(AGILITY)
	runner.addDoubleAccess(STRENGTH)
	runner.addDoubleAccess(PASSING)
	runner.addDoubleAccess(MUTATION)

	blitzer = Position(raceID=SKAVEN.id, name='Blitzer', ma=7, st=3, ag=3, av=8, cost=90000, max=2)
	blitzer.addSkill(BLOCK)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(STRENGTH)
	blitzer.addDoubleAccess(AGILITY)
	blitzer.addDoubleAccess(PASSING)
	blitzer.addDoubleAccess(MUTATION)

	ogre = Position (raceID=SKAVEN.id, name='Rat Ogre', ma=6, st=5, ag=2, av=8, cost=150000, max=1)
	ogre.addSkill(LONER)
	ogre.addSkill(FRENZY)
	ogre.addSkill(MIGHTY_BLOW)
	ogre.addSkill(PREHENSILE_TAIL)
	ogre.addSkill(WILD_ANIMAL)
	ogre.addNormalAccess(STRENGTH)
	ogre.addDoubleAccess(GENERAL)
	ogre.addDoubleAccess(AGILITY)
	ogre.addDoubleAccess(PASSING)
	ogre.addDoubleAccess(MUTATION)


def createSlann():
	global SLANN
	SLANN = Race(name='Slann', rrCost=50000)

	line = Position(raceID=SLANN.id, name='Lineman', ma=6, st=3, ag=3, av=8, cost=60000, max=16)
	line.addSkill(LEAP)
	line.addSkill(VERY_LONG_LEGS)
	line.addNormalAccess(GENERAL)
	line.addDoubleAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	catcher = Position(raceID=SLANN.id, name='Catcher', ma=7, st=2, ag=4, av=7, cost=80000, max=4)
	catcher.addSkill(DIVING_CATCH)
	catcher.addSkill(LEAP)
	catcher.addSkill(VERY_LONG_LEGS)
	catcher.addNormalAccess(AGILITY)
	catcher.addNormalAccess(GENERAL)
	catcher.addDoubleAccess(STRENGTH)
	catcher.addDoubleAccess(PASSING)

	blitzer = Position(raceID=SLANN.id, name='Blitzer', ma=7, st=3, ag=3, av=8, cost=110000, max=4)
	blitzer.addSkill(DIVING_TACKLE)
	blitzer.addSkill(JUMP_UP)
	blitzer.addSkill(LEAP)
	blitzer.addSkill(VERY_LONG_LEGS)
	blitzer.addNormalAccess(AGILITY)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(STRENGTH)
	blitzer.addDoubleAccess(PASSING)

	krox = Position(raceID=SLANN.id, name='Kroxigor', ma=6, st=5, ag=1, av=9, cost=140000, max=1)
	krox.addSkill(LONER)
	krox.addSkill(BONEHEAD)
	krox.addSkill(MIGHTY_BLOW)
	krox.addSkill(PREHENSILE_TAIL)
	krox.addSkill(THICK_SKULL)
	krox.addNormalAccess(STRENGTH)
	krox.addDoubleAccess(GENERAL)
	krox.addDoubleAccess(AGILITY)
	krox.addDoubleAccess(PASSING)


def createUndead():
	global UNDEAD
	UNDEAD = Race(name='Undead', rrCost=70000)

	skelly = Position(raceID=UNDEAD.id, name='Skeleton', ma=5, st=3, ag=2, av=7, cost=40000, max=16)
	skelly.addSkill(REGENERATION)
	skelly.addSkill(THICK_SKULL)
	skelly.addNormalAccess(GENERAL)
	skelly.addDoubleAccess(AGILITY)
	skelly.addDoubleAccess(STRENGTH)
	skelly.addDoubleAccess(PASSING)

	zomb = Position(raceID=UNDEAD.id, name='Zombie', ma=4, st=3, ag=2, av=8, cost=40000, max=16)
	zomb.addSkill(REGENERATION)
	zomb.addNormalAccess(GENERAL)
	zomb.addDoubleAccess(AGILITY)
	zomb.addDoubleAccess(STRENGTH)
	zomb.addDoubleAccess(PASSING)

	ghoul = Position(raceID=UNDEAD.id, name='Ghoul', ma=7, st=3, ag=3, av=7, cost=70000, max=4)
	ghoul.addSkill(DODGE)
	ghoul.addNormalAccess(GENERAL)
	ghoul.addNormalAccess(AGILITY)
	ghoul.addDoubleAccess(STRENGTH)
	ghoul.addDoubleAccess(PASSING)

	wight = Position(raceID=UNDEAD.id, name='Wight', ma=6, st=3, ag=3, av=8, cost=90000, max=2)
	wight.addSkill(BLOCK)
	wight.addSkill(REGENERATION)
	wight.addNormalAccess(GENERAL)
	wight.addDoubleAccess(AGILITY)
	wight.addDoubleAccess(STRENGTH)
	wight.addDoubleAccess(PASSING)

	mummy = Position(raceID=UNDEAD.id, name='Mummy', ma=3, st=5, ag=1, av=9, cost=120000, max=2)
	mummy.addSkill(MIGHTY_BLOW)
	mummy.addSkill(REGENERATION)
	mummy.addNormalAccess(STRENGTH)
	mummy.addDoubleAccess(AGILITY)
	mummy.addDoubleAccess(GENERAL)
	mummy.addDoubleAccess(PASSING)


def createUnderworld():
	global UNDERWORLD
	UNDERWORLD = Race(name='Underworld', rrCost=70000)

	gobbo = Position(raceID=UNDERWORLD.id, name='Underworld Goblin', ma=6, st=2, ag=3, av=7, cost=40000, max=12)
	gobbo.addSkill(RIGHT_STUFF)
	gobbo.addSkill(DODGE)
	gobbo.addSkill(STUNTY)
	gobbo.addNormalAccess(AGILITY)
	gobbo.addNormalAccess(MUTATION)
	gobbo.addDoubleAccess(GENERAL)
	gobbo.addDoubleAccess(STRENGTH)
	gobbo.addDoubleAccess(PASSING)

	line = Position(raceID=UNDERWORLD.id, name='Skaven Lineman', ma=7, st=3, ag=3, av=7, cost=50000, max=2)
	line.addSkill(ANIMOSITY)
	line.addNormalAccess(GENERAL)
	line.addNormalAccess(MUTATION)
	line.addDoubleAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	thrower = Position(raceID=UNDERWORLD.id, name='Skaven Thrower', ma=7, st=3, ag=3, av=7, cost=70000, max=2)
	thrower.addSkill(ANIMOSITY)
	thrower.addSkill(PASS)
	thrower.addSkill(SURE_HANDS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(MUTATION)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(AGILITY)
	thrower.addDoubleAccess(STRENGTH)

	blitzer = Position(raceID=UNDERWORLD.id, name='Skaven Blitzer', ma=7, st=3, ag=3, av=8, cost=90000, max=2)
	blitzer.addSkill(ANIMOSITY)
	blitzer.addSkill(BLOCK)
	blitzer.addNormalAccess(GENERAL)
	blitzer.addNormalAccess(MUTATION)
	blitzer.addNormalAccess(STRENGTH)
	blitzer.addDoubleAccess(AGILITY)
	blitzer.addDoubleAccess(PASSING)

	troll = Position (raceID=UNDERWORLD.id, name='Warpstone Troll', ma=4, st=5, ag=1, av=9, cost=110000, max=1)
	troll.addSkill(LONER)
	troll.addSkill(ALWAYS_HUNGRY)
	troll.addSkill(MIGHTY_BLOW)
	troll.addSkill(REALLY_STUPID)
	troll.addSkill(REGENERATION)
	troll.addSkill(THROW_TEAMMATE)
	troll.addNormalAccess(STRENGTH)
	troll.addNormalAccess(MUTATION)
	troll.addDoubleAccess(GENERAL)
	troll.addDoubleAccess(AGILITY)
	troll.addDoubleAccess(PASSING)


def createVampire():
	global VAMPIRE
	VAMPIRE = Race(name='Vampire', rrCost=70000)

	thrall = Position(raceID=VAMPIRE.id, name='Thrall', ma=6, st=3, ag=3, av=7, cost=40000, max=16)
	thrall.addNormalAccess(GENERAL)
	thrall.addDoubleAccess(AGILITY)
	thrall.addDoubleAccess(STRENGTH)
	thrall.addDoubleAccess(PASSING)

	vamp = Position(raceID=VAMPIRE.id, name='Vampire', ma=6, st=4, ag=4, av=8, cost=110000, max=6)
	vamp.addSkill(BLOOD_LUST)
	vamp.addSkill(HYPNOTIC_GAZE)
	vamp.addSkill(REGENERATION)
	vamp.addNormalAccess(GENERAL)
	vamp.addNormalAccess(AGILITY)
	vamp.addNormalAccess(STRENGTH)
	vamp.addDoubleAccess(PASSING)


def createWoodElf():
	global WOOD_ELF
	WOOD_ELF = Race(name='Wood Elf', rrCost=50000)

	line = Position(raceID=WOOD_ELF.id, name='Lineman', ma=7, st=3, ag=4, av=7, cost=70000, max=16)
	line.addNormalAccess(GENERAL)
	line.addNormalAccess(AGILITY)
	line.addDoubleAccess(STRENGTH)
	line.addDoubleAccess(PASSING)

	catcher = Position(raceID=WOOD_ELF.id, name='Catcher', ma=8, st=2, ag=4, av=7, cost=90000, max=4)
	catcher.addSkill(CATCH)
	catcher.addSkill(DODGE)
	catcher.addSkill(SPRINT)
	catcher.addNormalAccess(GENERAL)
	catcher.addNormalAccess(AGILITY)
	catcher.addDoubleAccess(STRENGTH)
	catcher.addDoubleAccess(PASSING)

	thrower = Position(raceID=WOOD_ELF.id, name='Thrower', ma=7, st=3, ag=4, av=7, cost=90000, max=2)
	thrower.addSkill(PASS)
	thrower.addNormalAccess(GENERAL)
	thrower.addNormalAccess(AGILITY)
	thrower.addNormalAccess(PASSING)
	thrower.addDoubleAccess(STRENGTH)

	dancer = Position(raceID=WOOD_ELF.id, name='Wardancer', ma=8, st=3, ag=4, av=7, cost=120000, max=2)
	dancer.addSkill(BLOCK)
	dancer.addSkill(DODGE)
	dancer.addSkill(LEAP)
	dancer.addNormalAccess(GENERAL)
	dancer.addNormalAccess(AGILITY)
	dancer.addDoubleAccess(STRENGTH)
	dancer.addDoubleAccess(PASSING)

	tree = Position(raceID=WOOD_ELF.id, name='Treeman', ma=2, st=6, ag=1, av=10, cost=120000, max=1)
	tree.addSkill(LONER)
	tree.addSkill(MIGHTY_BLOW)
	tree.addSkill(STAND_FIRM)
	tree.addSkill(STRONG_ARM)
	tree.addSkill(TAKE_ROOT)
	tree.addSkill(THICK_SKULL)
	tree.addSkill(THROW_TEAMMATE)
	tree.addNormalAccess(STRENGTH)
	tree.addDoubleAccess(GENERAL)
	tree.addDoubleAccess(AGILITY)
	tree.addDoubleAccess(PASSING)


### MAIN ###

if __name__ == '__main__':
	# tables
	recreateTables()
	# rules data
	createSkills()
	# teams
	createAmazon()
	createChaos()
	createChaosDwarf()
	createChaosPact()
	createDarkElf()
	createDwarf()
	createElf()
	createGoblin()
	createHalfling()
	createHighElf()
	createHuman()
	createKhemri()
	createLizardman()
	createNecromantic()
	createNorse()
	createNurgle()
	createOgre()
	createOrc()
	createSkaven()
	createSlann()
	createUndead()
	createUnderworld()
	createVampire()
	createWoodElf()
	# create nuffle/admin coach
	Coach(username='nuffle', password='nuffle', realname='Nuffle', role='ADMIN')
	# create sample season
	Season(id=1, name='My First Season')
