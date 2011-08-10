#!/usr/bin/env python2.4
__doc__ = '''Nuffle Blood Bowl Web Manager web server.'''

import ConfigParser
import datetime
import elo
import glicko
import os.path
import sys
import time
import traceback
from data import *

# Read in the nuffle configuration so we can determine
# where our third party python libraries have been
# installed.
cfg = ConfigParser.ConfigParser()
cfg.read('nuffle.cfg')
sys.path.insert(0, cfg.get('nuffle', 'dir.lib.python'))
import cherrypy
from cherrytemplate import renderTemplate
from sqlobject import sqlbuilder


### FUNCTIONS ###

def gpFormat(gp):
	gp = str(int(gp))
	s = ''
	while len(gp) > 3 and not (len(gp) == 4 and gp[0] == '-'):
		chunk = gp[-3:]
		s = ',' + chunk + s
		gp = gp[:-3]
	s = gp + s
	return '%sgp' % s

def coach_elo():
	coach_elo = {}
	for game in Game.select(sqlbuilder.IN(Game.q.id, sqlbuilder.Select(
			GameTeam.q.gameID, where=GameTeam.q.score>0)), orderBy='date'):

		pre_game = []
		for gameTeam in game.gameTeams:
			pre_game.append((gameTeam.team.coach, coach_elo.get(gameTeam.team.coach.id, elo.start_r), gameTeam.score))
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

		coach_elo[coacha.id] = elo.r(ra, [(rb, sa)], elo.k)
		coach_elo[coachb.id] = elo.r(rb, [(ra, sb)], elo.k)

	return coach_elo

def race_elo():
	race_elo = {}
	for game in Game.select(sqlbuilder.IN(Game.q.id, sqlbuilder.Select(
			GameTeam.q.gameID, where=GameTeam.q.score>0)), orderBy='date'):

		pre_game = []
		for gameTeam in game.gameTeams:
			pre_game.append((gameTeam.team.race, race_elo.get(gameTeam.team.race.id, elo.start_r), gameTeam.score))
		assert len(pre_game) == 2, 'Should have exactly two races in game'

		(racea, ra, scorea), (raceb, rb, scoreb) = pre_game
		if racea.id == raceb.id:
			continue # skip games that are between the same race
		if scorea > scoreb:
			sa = 1
			sb = 0
		elif scorea == scoreb:
			sa = .5
			sb = .5
		else:
			sa = 0
			sb = 1

		race_elo[racea.id] = elo.r(ra, [(rb, sa)], elo.k)
		race_elo[raceb.id] = elo.r(rb, [(ra, sb)], elo.k)

	return race_elo

def team_elo():
	team_elo = {}
	for game in Game.select(sqlbuilder.IN(Game.q.id, sqlbuilder.Select(
			GameTeam.q.gameID, where=GameTeam.q.score>0)), orderBy='date'):

		pre_game = []
		for gameTeam in game.gameTeams:
			pre_game.append((gameTeam.team, team_elo.get(gameTeam.team.id, elo.start_r), gameTeam.score))
		assert len(pre_game) == 2, 'Should have exactly two teams in game'

		(teama, ra, scorea), (teamb, rb, scoreb) = pre_game
		if scorea > scoreb:
			sa = 1
			sb = 0
		elif scorea == scoreb:
			sa = .5
			sb = .5
		else:
			sa = 0
			sb = 1

		team_elo[teama.id] = elo.r(ra, [(rb, sa)], elo.k)
		team_elo[teamb.id] = elo.r(rb, [(ra, sb)], elo.k)

	return team_elo

def cmp_stats(win_index, tie_index, game_index):
	def win_percent(stat_row):
		if stat_row[game_index] <= 0:
			return None
		w = float(stat_row[win_index])
		w += 0.5 * float(stat_row[tie_index])
		return w / float(stat_row[game_index])
	return lambda x, y : cmp(win_percent(y), win_percent(x))

def compute_glicko_pre_rd(rd, t):
	return glicko.pre_rd(rd, glicko.c, t)

def compute_glicko(t, r, rd, opponents):
	rd = compute_glicko_pre_rd(rd, t)
	return glicko.post_r(r, rd, opponents), glicko.post_rd(r, rd, opponents)

def coach_glicko():
	coach_glicko = {}
	for game in Game.select(sqlbuilder.IN(Game.q.id, sqlbuilder.Select(
			GameTeam.q.gameID, where=GameTeam.q.score>0)), orderBy='date'):

		pre_game = []
		for gameTeam in game.gameTeams:
			r, rd, t0 = coach_glicko.get(gameTeam.team.coach.id, (glicko.start_r, glicko.start_rd, datetime.datetime.now()))
			t = max((game.date - t0).days, 1)
			pre_game.append((gameTeam.team.coach, r, rd, t, gameTeam.score))
		assert len(pre_game) == 2, 'Should have exactly two coaches in game'

		(coacha, ra, rda, ta, scorea), (coachb, rb, rdb, tb, scoreb) = pre_game
		if scorea > scoreb:
			sa = 1
			sb = 0
		elif scorea == scoreb:
			sa = .5
			sb = .5
		else:
			sa = 0
			sb = 1

		xa, ya = compute_glicko(ta, ra, rda, [(rb, rdb, sa)])
		xb, yb = compute_glicko(tb, rb, rdb, [(ra, rda, sb)])
		coach_glicko[coacha.id] = (xa, ya, game.date)
		coach_glicko[coachb.id] = (xb, yb, game.date)

	for key, (r, rd, t0) in coach_glicko.iteritems():
		t = max((datetime.datetime.now() - t0).days, 1)
		rd = compute_glicko_pre_rd(rd, t)
		coach_glicko[key] = (r, rd, t0)

	return coach_glicko

def race_glicko():
	race_glicko = {}
	for game in Game.select(sqlbuilder.IN(Game.q.id, sqlbuilder.Select(
			GameTeam.q.gameID, where=GameTeam.q.score>0)), orderBy='date'):

		pre_game = []
		for gameTeam in game.gameTeams:
			r, rd, t0 = race_glicko.get(gameTeam.team.race.id, (glicko.start_r, glicko.start_rd, datetime.datetime.now()))
			t = max((game.date - t0).days, 1)
			pre_game.append((gameTeam.team.race, r, rd, t, gameTeam.score))
		assert len(pre_game) == 2, 'Should have exactly two teams in game'

		(racea, ra, rda, ta, scorea), (raceb, rb, rdb, tb, scoreb) = pre_game
		if racea.id == raceb.id:
			continue # skip games that are between the same race
		if scorea > scoreb:
			sa = 1
			sb = 0
		elif scorea == scoreb:
			sa = .5
			sb = .5
		else:
			sa = 0
			sb = 1

		xa, ya = compute_glicko(ta, ra, rda, [(rb, rdb, sa)])
		xb, yb = compute_glicko(tb, rb, rdb, [(ra, rda, sb)])
		race_glicko[racea.id] = (xa, ya, game.date)
		race_glicko[raceb.id] = (xb, yb, game.date)

	for key, (r, rd, t0) in race_glicko.iteritems():
		t = max((datetime.datetime.now() - t0).days, 1)
		rd = compute_glicko_pre_rd(rd, t)
		race_glicko[key] = (r, rd, t0)

	return race_glicko

def team_glicko():
	team_glicko = {}
	for game in Game.select(sqlbuilder.IN(Game.q.id, sqlbuilder.Select(
			GameTeam.q.gameID, where=GameTeam.q.score>0)), orderBy='date'):

		pre_game = []
		for gameTeam in game.gameTeams:
			r, rd, t0 = team_glicko.get(gameTeam.team.id, (glicko.start_r, glicko.start_rd, datetime.datetime.now()))
			t = max((game.date - t0).days, 1)
			pre_game.append((gameTeam.team, r, rd, t, gameTeam.score))
		assert len(pre_game) == 2, 'Should have exactly two teams in game'

		(teama, ra, rda, ta, scorea), (teamb, rb, rdb, tb, scoreb) = pre_game
		if scorea > scoreb:
			sa = 1
			sb = 0
		elif scorea == scoreb:
			sa = .5
			sb = .5
		else:
			sa = 0
			sb = 1

		xa, ya = compute_glicko(ta, ra, rda, [(rb, rdb, sa)])
		xb, yb = compute_glicko(tb, rb, rdb, [(ra, rda, sb)])
		team_glicko[teama.id] = (xa, ya, game.date)
		team_glicko[teamb.id] = (xb, yb, game.date)

	for key, (r, rd, t0) in team_glicko.iteritems():
		t = max((datetime.datetime.now() - t0).days, 1)
		rd = compute_glicko_pre_rd(rd, t)
		team_glicko[key] = (r, rd, t0)

	return team_glicko

### PAGE CLASSES ###

class BasePage:

	def _cpOnError(self):
		try:
			raise
		except cherrypy.NotFound:
			cherrypy.response.headerMap ['Status'] = '404 Not Found'
			cherrypy.response.body = ['<h1>Page Not Found</h1>']
		except:
			cherrypy.response.body = renderTemplate(file = 'html/error.html')

	def _kwargs(self, kwargs):
		for(key, value) in kwargs.items():
			value = str(value)
			value = value.strip()
			if len(value) <= 0:
				value = None
			if key.startswith('INT'):
				del kwargs [key]
				if value is None:
					kwargs [key [3:]] = value
				else:
					kwargs [key [3:]] = int(value)


class FrontPage(BasePage):

	@cherrypy.expose
	def index(self):
		return renderTemplate(file = 'html/front.html')

	@cherrypy.expose
	def login(self, username, password):
		aCoach = Coach.byUsername(username)
		assert aCoach.password == password, 'Incorrect password!'
		cherrypy.session['username'] = aCoach.username
		return self.index()

	@cherrypy.expose
	def logout(self):
		if cherrypy.session.has_key('username'):
			del cherrypy.session['username']
		return self.index()


class AdminPage(BasePage):

	@cherrypy.expose
	def index(self):
		return renderTemplate(file = 'html/admin.html')


class CoachPage(BasePage):

	@cherrypy.expose
	def admin(self):
		coaches = Coach.select()
		return renderTemplate(file = 'html/admin_coach.html')

	@cherrypy.expose
	def create(self, **kwargs):
		self._kwargs(kwargs)
		assert kwargs ['password'] == kwargs.pop('password2'), 'Passwords do not match!'
		Coach(**kwargs)
		return self.admin()

	@cherrypy.expose
	def edit(self, id, **kwargs):
		self._kwargs(kwargs)
		if kwargs.has_key('password2'):
			assert kwargs ['password'] == kwargs.pop('password2'), 'Passwords do not match!'
		coach = Coach.get(id)
		if kwargs:
			coach.set(**kwargs)
		return renderTemplate(file = 'html/edit_coach.html')

	@cherrypy.expose
	def default(self, key, value):
		if key == 'id':
			coach = Coach.get(value)
		else:
			coach = eval('Coach.by%s(value)' % key.capitalize())
		assert coach is not None
		return renderTemplate(file = 'html/view_coach.html')

	@cherrypy.expose
	def stats(self):
		return renderTemplate(file = 'html/stats_coach.html')


class GamePage(BasePage):

	@cherrypy.expose
	def edit(self, id, **kwargs):
		self._kwargs(kwargs)
		game = Game.get(id)
		if kwargs:
			kwargs ['date'] = datetime.datetime(kwargs.pop('year'), kwargs.pop('month'), kwargs.pop('day'))
			game.set(**kwargs)
		return renderTemplate(file = 'html/edit_game.html')

	@cherrypy.expose
	def editGameTeam(self, id, **kwargs):
		self._kwargs(kwargs)
		gameTeam = GameTeam.get(id)
		if kwargs:
			for player in gameTeam.team.players:
				# BUG: This breaks when games are entered out of sequence
				if not player.isMNG():
					if not GameTeamPlayer.selectBy(gameTeamID=gameTeam.id, playerID=player.id).count():
						GameTeamPlayer(gameTeamID=gameTeam.id, playerID=player.id)
			if kwargs.has_key('winnings') and kwargs['winnings'] != gameTeam.winnings:
				gameTeam.team.treasury += kwargs['winnings'] - gameTeam.winnings
			if kwargs.has_key('ffChange') and kwargs['ffChange'] != gameTeam.ffChange:
				gameTeam.team.ff += int(kwargs['ffChange']) - int(gameTeam.ffChange)
			gameTeam.set(**kwargs)
		return self.edit(gameTeam.game.id)

	@cherrypy.expose
	def editGameTeamPlayers(self, **kwargs):
		self._kwargs(kwargs)

		gameTeamPlayers = {}
		for key, value in kwargs.items():
			gtpID = int(key[:9].strip())
			column = key[9:]
			if not gameTeamPlayers.has_key(gtpID):
				gameTeamPlayers[gtpID]= {}
			gameTeamPlayers[gtpID][column] = value

		for gtpID, values in gameTeamPlayers.items():
			gtp = GameTeamPlayer.get(gtpID)
			gtp.set(**values)

		return self.edit(gtp.gameTeam.game.id)

	@cherrypy.expose
	def default(self, key, value):
		if key == 'id':
			game = Game.get(value)
		else:
			game = eval('Game.by%s(value)' % key.capitalize())
		return renderTemplate(file = 'html/view_game.html')


class LeaguePage(BasePage):

	@cherrypy.expose
	def index(self):
		return renderTemplate(file = 'html/league.html')


class MedalPage(BasePage):

	@cherrypy.expose
	def add(self, **kwargs):
		self._kwargs(kwargs)
		Medal(**kwargs)
		return self.admin()

	@cherrypy.expose
	def admin(self):
		teams = Team.select()
		return renderTemplate(file = 'html/admin_medal.html')

	@cherrypy.expose
	def delete(self, id):
		Medal.delete(id)
		return self.admin()


class PrintPage(BasePage):

	@cherrypy.expose
	def default(self, key, value):
		if key == 'id':
			team = Team.get(value)
		else:
			team = eval('Team.by%s(value)' % key.capitalize())
		return renderTemplate(file = 'html/print_team.html')


class RacePage(BasePage):

	@cherrypy.expose
	def default(self, key, value):
		if key == 'id':
			race = Race.get(value)
		else:
			race = eval('Race.by%s(value)' % key.capitalize())
		return renderTemplate(file = 'html/view_race.html')

	@cherrypy.expose
	def stats(self):
		return renderTemplate(file = 'html/stats_race.html')


class SeasonPage(BasePage):

	def addBye(self, season, team, year, month, day):
		byeDate = datetime.datetime(int(year), int(month), int(day))
		Bye(seasonID = season, teamID = team.id, date = byeDate)
		return self.edit(season)

	@cherrypy.expose
	def addGame(self, season, team1, team2, year, month, day):
		team1 = Team.get(team1)
		if team2 == 'BYE':
			return self.addBye(season, team1, year, month, day)
		team2 = Team.get(team2)
		assert team1 is not team2, 'Teams cannot play games against themselves!'
		gameDate = datetime.datetime(int(year), int(month), int(day))
		game = Game(seasonID = season, date = gameDate)
		GameTeam(teamID = team1.id, gameID = game.id)
		GameTeam(teamID = team2.id, gameID = game.id)
		return self.edit(season)

	@cherrypy.expose
	def addTeam(self, season, team):
		season = Season.get(season)
		team = Team.get(team)
		season.addTeam(team)
		return self.edit(season.id)

	@cherrypy.expose
	def admin(self):
		seasons = Season.select()
		return renderTemplate(file = 'html/admin_season.html')

	@cherrypy.expose
	def create(self, **kwargs):
		self._kwargs(kwargs)
		Season(**kwargs)
		return self.admin()

	@cherrypy.expose
	def edit(self, id, **kwargs):
		self._kwargs(kwargs)
		season = Season.get(id)
		if kwargs:
			season.set(**kwargs)
		return renderTemplate(file = 'html/edit_season.html')

	@cherrypy.expose
	def default(self, key, value):
		if key == 'id':
			season = Season.get(value)
		else:
			season = eval('Season.by%s(value)' % key.capitalize())
		return renderTemplate(file = 'html/view_season.html')

	@cherrypy.expose
	def removeBye(self, season, bye):
		Bye.delete(bye)
		return self.edit(season)

	@cherrypy.expose
	def removeGame(self, season, game):
		game = Game.get(game)
		for gameTeam in game.gameTeams:
			GameTeam.delete(gameTeam.id)
		game.destroySelf()
		return self.edit(season)

	@cherrypy.expose
	def removeTeam(self, season, team):
		season = Season.get(season)
		team = Team.get(team)
		season.removeTeam(team)
		return self.edit(season.id)


class TeamPage(BasePage):

	@cherrypy.expose
	def bankTransfer(self, id, amount):
		amount = int(amount)
		team = Team.get(id)
		assert (team.treasury - amount) >= 0, 'Not enough money in treasury!'
		assert 0 <= (team.bank + amount), 'Not enough money in bank!'
		team.treasury -= amount
		team.bank += amount
		return self.edit(id)

	@cherrypy.expose
	def buyApothecary(self, id):
		cost = 50000
		team = Team.get(id)
		assert not team.apothecary, 'You already have an apothecary!'
		assert team.treasury >= cost, 'You cannot afford apothecary!'
		team.treasury -= cost
		team.apothecary = 1 # True
		return self.edit(id)

	@cherrypy.expose
	def buyAssistantCoach(self, id):
		cost = 10000
		team = Team.get(id)
		assert team.treasury >= cost, 'You cannot afford assistant coach!'
		team.treasury -= cost
		team.assistantCoaches += 1
		return self.edit(id)

	@cherrypy.expose
	def buyCheerleader(self, id):
		cost = 10000
		team = Team.get(id)
		assert team.treasury >= cost, 'You cannot afford cheerleader!'
		team.treasury -= cost
		team.cheerleaders += 1
		return self.edit(id)

	@cherrypy.expose
	def buyFF(self, id):
		cost = 10000
		team = Team.get(id)
		assert team.treasury >= cost, 'You cannot afford fan factor!'
		team.treasury -= cost
		team.ff += 1
		return self.edit(id)

	@cherrypy.expose
	def buyJourneyman(self, id):
		player = Player.get(id)
		assert player.isJourneyman, 'This player is not a Journeyman!'
		team = player.team
		playerCount = len(team.activePlayers())
		assert playerCount < 16, 'You already have %d players!' % playerCount
		position = player.position
		assert team.treasury >= position.cost, 'You cannot afford %s!' % position.name
		team.treasury -= position.cost
		player.isJourneyman = 0 # False
		player.removeSkill(loner().id)
		return self.edit(team.id)

	@cherrypy.expose
	def buyPlayer(self, **kwargs):
		self._kwargs(kwargs)
		team = Team.get(kwargs ['teamID'])
		playerCount = len(team.activePlayers())
		assert playerCount < 16, 'You already have %d players!' % playerCount
		position = Position.get(kwargs ['positionID'])
		assert team.positionCount(position) < position.max, 'You already have %d %ss!' % (team.positionCount(position), position.name)
		assert team.treasury >= position.cost, 'You cannot afford %s!' % position.name
		team.treasury -= position.cost
		player = Player(**kwargs)
		for skill in positionSkills(position):
			player.addSkill(skill)
		return self.edit(team.id)

	@cherrypy.expose
	def buyRR(self, id):
		team = Team.get(id)
		cost = team.race.rrCost
		if not team.isNew():
			cost *= 2
		assert team.treasury >= cost, 'You cannot afford reroll!'
		team.treasury -= cost
		team.rr += 1
		return self.edit(id)

	@cherrypy.expose
	def create(self, **kwargs):
		self._kwargs(kwargs)
		assert kwargs.has_key('name') and kwargs['name'], 'Team must be named!'
		team = Team(**kwargs)
		return self.edit(team.id)

	@cherrypy.expose
	def edit(self, id, player = None, changeName = False, **kwargs):
		self._kwargs(kwargs)
		team = Team.get(id)
		editPlayer = None
		if player:
			editPlayer = Player.get(player)
			if kwargs:
				skill = kwargs.pop('skill')
				if skill and editPlayer.eligibleSkill(Skill.get(skill)):
					editPlayer.addSkill(skill)
				editPlayer.set(**kwargs)
				editPlayer = None
		else:
			if kwargs:
				team.set(**kwargs)
		return renderTemplate(file = 'html/edit_team.html')

	@cherrypy.expose
	def default(self, key, value):
		if key == 'id':
			team = Team.get(value)
		else:
			team = eval('Team.by%s(value)' % key.capitalize())
		return renderTemplate(file = 'html/view_team.html')

	@cherrypy.expose
	def delete(self, id):
		team = Team.get(id)
		assert not team.byes, 'Team cannot be deleted with a bye!'
		assert not team.teamGames, 'Team cannot be deleted with games!'
		for player in team.players:
			self.sellPlayer(player.id)
		team.destroySelf()
		return cherrypy.root.coach.edit(team.coach.id)

	@cherrypy.expose
	def freebootJourneyman(self, **kwargs):
		self._kwargs(kwargs)
		team = Team.get(kwargs ['teamID'])
		assert team.needsJourneymen(), 'You have too many players for a Journeyman!'
		position = Position.get(kwargs ['positionID'])
		player = Player(isJourneyman=True, **kwargs)
		player.addSkill(loner())
		for skill in positionSkills(position):
			player.addSkill(skill)
		return self.edit(team.id)

	@cherrypy.expose
	def retirePlayer(self, id):
		player = Player.get(id)
		player.isRetired = 1 # True
		return self.edit(player.team.id)

	@cherrypy.expose
	def sellApothecary(self, id):
		cost = 50000
		team = Team.get(id)
		team.treasury += cost
		team.apothecary = 0 # False
		return self.edit(id)

	@cherrypy.expose
	def sellAssistantCoach(self, id):
		cost = 10000
		team = Team.get(id)
		team.treasury += cost
		team.assistantCoaches -= 1
		return self.edit(id)

	@cherrypy.expose
	def sellCheerleader(self, id):
		cost = 10000
		team = Team.get(id)
		team.treasury += cost
		team.cheerleaders -= 1
		return self.edit(id)

	@cherrypy.expose
	def sellFF(self, id):
		cost = 10000
		team = Team.get(id)
		team.treasury += cost
		team.ff -= 1
		return self.edit(id)

	@cherrypy.expose
	def sellPlayer(self, id):
		player = Player.get(id)
		assert not player.gamePlayers, '%s has already played %d games!' % (player.htmlName(), len(player.gamePlayers))
		player.destroySelf()
		player.team.treasury += player.position.cost
		return self.edit(player.team.id)

	@cherrypy.expose
	def sellRR(self, id):
		team = Team.get(id)
		cost = team.race.rrCost
		if not team.isNew():
			cost *= 2
		team.treasury += cost
		team.rr -= 1
		return self.edit(id)

	@cherrypy.expose
	def stats(self):
		return renderTemplate(file = 'html/stats_team.html')


### MAIN ###

def daemonize(cwd, pidfile):
	def replumb(f, mode, *bufferSize):
		devnull = file(os.devnull, mode, *bufferSize)
		os.dup2(devnull.fileno(), f.fileno())
		devnull.close()
	# ensure we're not process group leader
	if os.fork() > 0:
		os._exit(0)
	# drop control tty
	os.setsid()
	# abdicate session leader, orphan ourself
	if os.fork() > 0:
		os._exit(0)
	# set current working directory
	os.chdir(cwd)
	# avoid inheriting a umask
	os.umask(0)
	# release stdin, stdout, stderr
	replumb(sys.stdin, 'r')
	replumb(sys.stdout, 'a')
	replumb(sys.stderr, 'a+', 0)
	# write our new pid
	file(pidfile, 'wt').write("%d\n" % os.getpid())


if __name__ == '__main__':
	# daemonize ourself
	daemonize(cfg.get('nuffle', 'dir.root'), cfg.get('nuffle', 'pidfile'))

	# establish web root
	cherrypy.root = FrontPage()
	cherrypy.root.admin = AdminPage()
	cherrypy.root.coach = CoachPage()
	cherrypy.root.game = GamePage()
	cherrypy.root.league = LeaguePage()
	cherrypy.root.medal = MedalPage()
	cherrypy.root.race = RacePage()
	cherrypy.root.season = SeasonPage()
	cherrypy.root.team = TeamPage()
	cherrypy.root.teamPrint = PrintPage()

	# start the web server
	cherrypy.config.update(file = os.path.join(cfg.get('nuffle', 'dir.root'), 'cherrypy.cfg'))
	cherrypy.server.start()
