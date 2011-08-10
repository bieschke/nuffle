#!/usr/bin/env python2.4
__doc__ = '''Read data from a legacy schema, and insert data into the new schema.'''

import MySQLdb, sys


def coach(legacy, db):
	lc = legacy.cursor()
	try:
		lc.execute("select username, username, realname, email, phone, if(admin!=0, 'ADMIN', 'USER') from coaches")
		values = lc.fetchall()
	finally:
		lc.close()
	dc = db.cursor()
	try:
		dc.executemany('insert into coach (username, password, realname, email, phone, role) values (%s, %s, %s, %s, %s, %s)', values)
	finally:
		dc.close()


def coachMap(db):
	map = {}
	dc = db.cursor()
	try:
		dc.execute('select id, username from coach')
		while True:
			row = dc.fetchone()
			if not row:
				break
			map[row[1]] = row[0]
	finally:
		dc.close()
	return map


def gameTeamId(db, gameId, playerId):
	dc = db.cursor()
	try:
		dc.execute('select gt.id from game_team gt, player p where gt.game_id=%s and gt.team_id=p.team_id and p.id=%s', (gameId, playerId))
		row = dc.fetchone()
		assert row, 'game=%d ; player=%d' % (gameId, playerId)
		return row[0]
	finally:
		dc.close()

def gamePlayerRow(db, row):
	row = list(row)
	row[0] = gameTeamId(db, row[0], row[1])
	injury = row[-1]
	if injury == 0:
		row[-1] = ''
	elif 1 <= injury <= 6:
		row[-1] = 'MNG'
	elif 7 <= injury <= 11:
		row[-1] = 'NI'
	elif 12 <= injury <= 13:
		row[-1] = '-1MA'
	elif 16 <= injury <= 17:
		row[-1] = '-1AV'
	elif 15 == injury:
		row[-1] = '-1AG'
	elif 14 == injury:
		row[-1] = '-1ST'
	elif injury == 23:
		row[-1] = 'DEAD'
	else:
		raise ValueError, `injury`
	return tuple(row)

def gameRow(row, seasonMap):
	row = list(row)
	season = row.pop()
	league = row.pop()
	row.append(seasonMap[(league, season)])
	return tuple(row)

def game(legacy, db, seasonMap):
	# basic game data
	lc = legacy.cursor()
	try:
		lc.execute('select g.game_id, coalesce(g.date_played,now()), g.gate, g.periods=3, g.profile, g.league, g.season from games g, game_teams gt where g.game_id=gt.game_id group by g.game_id having count(*)=2')
		values = lc.fetchall()
	finally:
		lc.close()
	values = [gameRow(row, seasonMap) for row in values]
	dc = db.cursor()
	try:
		dc.executemany('insert into game (id, date, gate, overtime, description, season_id) values (%s, %s, %s, %s, %s, %s)', values)
	finally:
		dc.close()
	# game teams
	lc = legacy.cursor()
	try:
		lc.execute("select game_id, team_id, score, winnings, if(ff is null, '0', concat(ff)) from game_teams gt0 where exists (select * from games g, game_teams gt where gt0.game_id=g.game_id and g.game_id=gt.game_id group by g.game_id having count(*)=2)")
		values = lc.fetchall()
	finally:
		lc.close()
	dc = db.cursor()
	try:
		dc.executemany('insert into game_team (game_id, team_id, score, winnings, ff_change) values (%s, %s, %s, %s, %s)', values)
	finally:
		dc.close()
	# game players
	lc = legacy.cursor()
	try:
		lc.execute("select gp.game_id, gp.player_id, gp.td, gp.cas, gp.comp, gp.cat, gp.inter, gp.mvp, gp.injury_id from game_players gp left outer join injuries i on gp.injury_id=i.injury_id where gp.missed=0 and exists (select * from players p where p.player_id=gp.player_id) and exists (select * from games g, game_teams gt where gp.game_id=g.game_id and g.game_id=gt.game_id group by g.game_id having count(*)=2) and not exists (select * from players p, positions o where gp.player_id=p.player_id and p.position=o.name and o.class='Staff')")
		values = lc.fetchall()
	finally:
		lc.close()
	values = [gamePlayerRow(db, row) for row in values]
	dc = db.cursor()
	try:
		dc.executemany('insert into game_team_player (game_team_id, player_id, td, cas, comp, cat, inter, mvp, injury) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', values)
	finally:
		dc.close()


def playerRow(row, positionMap):
	row = list(row)
	row[-3] = positionMap[row[-3]]
	return tuple(row)

def skillRow(row, skillMap):
	row = list(row)
	row[-1] = skillMap[row[-1]]
	return tuple(row)

def player(legacy, db, positionMap, skillMap):
	# basic player data
	lc = legacy.cursor()
	try:
		lc.execute("select player_id, pos, name, position, team_id, status='Retired' from players where not exists (select * from positions where positions.name = players.position and positions.class='Staff')")
		values = lc.fetchall()
	finally:
		lc.close()
	values = [playerRow(row, positionMap) for row in values if positionMap.has_key(row[-3])]
	dc = db.cursor()
	try:
		dc.executemany('insert into player (id, number, name, position_id, team_id, is_retired) values (%s, %s, %s, %s, %s, %s)', values)
	finally:
		dc.close()
	# positional skills
	dc = db.cursor()
	try:
		dc.execute('insert into player_skill (player_id, skill_id) select p.id, os.skill_id from player p, position_skill os where p.position_id=os.position_id')
	finally:
		dc.close()
	# advancement skills
	lc = legacy.cursor()
	try:
		lc.execute("select player_id, skill from player_advances where skill is not null and skill !='NULL' and skill != 'Razor Sharp Claws'")
		values = lc.fetchall()
	finally:
		lc.close()
	values = [skillRow(row, skillMap) for row in values]
	dc = db.cursor()
	try:
		dc.executemany('insert into player_skill (player_id, skill_id) values (%s, %s)', values)
	finally:
		dc.close()
	# stat upgrades
	lc = legacy.cursor()
	try:
		lc.execute("select player_id, advance from player_advances where advance in ('+1 MA','+1 AG','+1 ST')")
		values = lc.fetchall()
	finally:
		lc.close()
	values = [skillRow(row, skillMap) for row in values]
	dc = db.cursor()
	try:
		dc.executemany('insert into player_skill (player_id, skill_id) values (%s, %s)', values)
	finally:
		dc.close()


def positionId(db, raceId, positionName):
	dc = db.cursor()
	try:
		dc.execute('select id from position where race_id=%s and name=%s', (raceId, positionName))
		row = dc.fetchone()
		assert row, 'race=%d ; position=%s' % (raceId, positionName)
		return row[0]
	finally:
		dc.close()

def positionMap(db, raceMap):
	map = {}
	map['Amazon Blitzer'] = positionId(db, raceMap['Amazon'], 'Blitzer')
	map['Amazon Catcher'] = positionId(db, raceMap['Amazon'], 'Catcher')
	map['Amazon Linewoman'] = positionId(db, raceMap['Amazon'], 'Linewoman')
	map['Amazon Thrower'] = positionId(db, raceMap['Amazon'], 'Thrower')
	map['Beast of Nurgle'] = positionId(db, raceMap['Nurgle'], 'Beast of Nurgle')
	map['Black Orc Blocker'] = positionId(db, raceMap['Orc'], 'Blocker')
	map['Blitz-Ra'] = positionId(db, raceMap['Khemri'], 'Blitz-Ra')
	map['Bull Centaur'] = positionId(db, raceMap['Chaos Dwarf'], 'Bull Centaur')
	map['Chaos Beastman'] = positionId(db, raceMap['Chaos'], 'Beastman')
	map['Chaos Dwarf Blocker'] = positionId(db, raceMap['Chaos Dwarf'], 'Chaos Dwarf Blocker')
	map['Chaos Warrior'] = positionId(db, raceMap['Chaos'], 'Chaos Warrior')
	map['Dark Elf Blitzer'] = positionId(db, raceMap['Dark Elf'], 'Blitzer')
	map['Dark Elf Lineman'] = positionId(db, raceMap['Dark Elf'], 'Lineman')
	map['Dark Elf Thrower'] = positionId(db, raceMap['Dark Elf'], 'Thrower')
	map['Dragon Warrior'] = positionId(db, raceMap['High Elf'], 'Blitzer')
	map['Dwarf Blitzer'] = positionId(db, raceMap['Dwarf'], 'Blitzer')
	map['Dwarf Runner'] = positionId(db, raceMap['Dwarf'], 'Runner')
	map['Elf Blitzer'] = positionId(db, raceMap['Elf'], 'Blitzer')
	map['Elf Catcher'] = positionId(db, raceMap['Elf'], 'Catcher')
	map['Elf Lineman'] = positionId(db, raceMap['Elf'], 'Lineman')
	map['Elf Thrower'] = positionId(db, raceMap['Elf'], 'Thrower')
	map['Flesh Golem'] = positionId(db, raceMap['Necromantic'], 'Flesh Golem')
	map['Ghoul'] = positionId(db, raceMap['Undead'], 'Ghoul') # ???
	map['Goblin'] = positionId(db, raceMap['Goblin'], 'Goblin') # ???
	map['Gutter Runner'] = positionId(db, raceMap['Skaven'], 'Runner')
	map['High Elf Lineman'] = positionId(db, raceMap['High Elf'], 'Lineman')
	map['Hobgoblin'] = positionId(db, raceMap['Chaos Dwarf'], 'Hobgoblin')
	map['Human Blitzer'] = positionId(db, raceMap['Human'], 'Blitzer')
	map['Human Catcher'] = positionId(db, raceMap['Human'], 'Catcher')
	map['Human Kicker'] = positionId(db, raceMap['Human'], 'Thrower') # BUG
	map['Human Lineman'] = positionId(db, raceMap['Human'], 'Lineman')
	map['Human Thrower'] = positionId(db, raceMap['Human'], 'Thrower')
	map['Kroxigor'] = positionId(db, raceMap['Lizardman'], 'Kroxigor')
	map['Lion Warrior'] = positionId(db, raceMap['High Elf'], 'Catcher')
	map['Long Beard'] = positionId(db, raceMap['Dwarf'], 'Blocker')
	map['Minotaur'] = positionId(db, raceMap['Chaos'], 'Minotaur') # ???
	map['Mummy'] = positionId(db, raceMap['Khemri'], 'Mummy') # ???
	map['Norse Blitzer'] = positionId(db, raceMap['Norse'], 'Berserker')
	map['Norse Catcher'] = positionId(db, raceMap['Norse'], 'Catcher')
	map['Norse Lineman'] = positionId(db, raceMap['Norse'], 'Lineman')
	map['Norse Thrower'] = positionId(db, raceMap['Norse'], 'Thrower')
	map['Ogre'] = positionId(db, raceMap['Ogre'], 'Ogre') # ???
	map['Ogre Lineman'] = positionId(db, raceMap['Ogre'], 'Ogre') # ???
	map['Orc Blitzer'] = positionId(db, raceMap['Orc'], 'Blitzer')
	map['Orc Lineman'] = positionId(db, raceMap['Orc'], 'Lineman')
	map['Orc Thrower'] = positionId(db, raceMap['Orc'], 'Thrower')
	map['Phoenix Warrior'] = positionId(db, raceMap['High Elf'], 'Thrower')
	map['Rat Ogre'] = positionId(db, raceMap['Skaven'], 'Rat Ogre')
	map['Rotter'] = positionId(db, raceMap['Nurgle'], 'Rotter')
	map['Saurus'] = positionId(db, raceMap['Lizardman'], 'Saurus')
	map['Skaven Lineman'] = positionId(db, raceMap['Skaven'], 'Lineman')
	map['Skaven Thrower'] = positionId(db, raceMap['Skaven'], 'Thrower')
	map['Skeleton'] = positionId(db, raceMap['Khemri'], 'Skeleton') # ???
	map['Skink'] = positionId(db, raceMap['Lizardman'], 'Skink')
	map['Storm Vermin'] = positionId(db, raceMap['Skaven'], 'Blitzer')
	map['Thrall'] = positionId(db, raceMap['Vampire'], 'Thrall')
	map['Thro-Ra'] = positionId(db, raceMap['Khemri'], 'Thro-Ra')
	map['Treeman'] = positionId(db, raceMap['Halfling'], 'Treeman') # ???
	map['Troll'] = positionId(db, raceMap['Goblin'], 'Troll') # ???
	map['Troll Slayer'] = positionId(db, raceMap['Dwarf'], 'Troll Slayer')
	map['Vampire'] = positionId(db, raceMap['Vampire'], 'Vampire')
	map['Wardancer'] = positionId(db, raceMap['Wood Elf'], 'Wardancer')
	map['Werewolf'] = positionId(db, raceMap['Necromantic'], 'Werewolf')
	map['Wight'] = positionId(db, raceMap['Undead'], 'Wight') # ???
	map['Witch Elf'] = positionId(db, raceMap['Dark Elf'], 'Witch Elf')
	map['Wood Elf Catcher'] = positionId(db, raceMap['Wood Elf'], 'Catcher')
	map['Wood Elf Lineman'] = positionId(db, raceMap['Wood Elf'], 'Lineman')
	map['Wood Elf Thrower'] = positionId(db, raceMap['Wood Elf'], 'Thrower')
	map['Zombie'] = positionId(db, raceMap['Necromantic'], 'Zombie') # ???
	return map


def teamRow(row, coachMap, raceMap):
	row = list(row)
	row[-1] = raceMap[row[-1]]
	row[-2] = coachMap[row[-2]]
	return tuple(row)

def team(legacy, db, coachMap, raceMap):
	# basic data first
	lc = legacy.cursor()
	try:
		lc.execute("select team_id, name, treasury, ff, rr, coach, race from teams")
		values = lc.fetchall()
	finally:
		lc.close()
	values = [teamRow(row, coachMap, raceMap) for row in values]
	dc = db.cursor()
	try:
		dc.executemany('insert into team (id, name, treasury, ff, rr, coach_id, race_id) values (%s, %s, %s, %s, %s, %s, %s)', values)
	finally:
		dc.close()
	# staff data second
	lc = legacy.cursor()
	try:
		lc.execute("select sum(case when p.position='Assistant Coach' then 1 else 0 end), sum(case when p.position='Cheerleader' then 1 else 0 end), sum(p.position='Apothecary'), p.team_id from players p, positions o where p.position = o.name and o.class='Staff' group by p.team_id")
		values = lc.fetchall()
	finally:
		lc.close()
	dc = db.cursor()
	try:
		for value in values:
			dc.execute('update team set assistant_coaches=%s, cheerleaders=%s, apothecary=%s where id=%s', value)
	finally:
		dc.close()


def raceMap(db):
	map = {}
	dc = db.cursor()
	try:
		dc.execute("select id, name from race")
		while True:
			row = dc.fetchone()
			if not row:
				break
			if row[1] == 'Amazon':
				map['Amazons'] = row[0]
			elif row[1] == 'Human':
				map['Human (Pub)'] = row[0]
			elif row[1] == 'Necromantic':
				map['Necromatic'] = row[0]
			elif row[1] == 'Ogre':
				map['Ogres'] = row[0]
			map[row[1]] = row[0]
	finally:
		dc.close()
	return map


def seasonId(db, seasonName):
	dc = db.cursor()
	try:
		dc.execute('select id from season where name=%s', (seasonName,))
		row = dc.fetchone()
		assert row, 'season=%s' % seasonName
		return row[0]
	finally:
		dc.close()

def season(legacy, db):
	# basic season data
	lc = legacy.cursor()
	try:
		lc.execute('select league, num, name from seasons')
		values = lc.fetchall()
	finally:
		lc.close()
	dc = db.cursor()
	try:
		dc.executemany('insert into season (name) values (%s)', [row[2] for row in values])
	finally:
		dc.close()
	# season map
	map = {}
	for row in values:
		map[(row[0], row[1])] = seasonId(db, row[2])
	# season teams
	lc = legacy.cursor()
	try:
		lc.execute('select d.league, d.season, dt.team_id from divisions d, division_teams dt where d.division_id=dt.division_id and exists (select * from teams t where t.team_id=dt.team_id)')
		values = lc.fetchall()
	finally:
		lc.close()
	dc = db.cursor()
	try:
		dc.executemany('insert into season_team (season_id, team_id) values (%s, %s)', [(map[(row[0], row[1])], row[2]) for row in values])
	finally:
		dc.close()
	return map


def skillMap(db):
	map = {}
	dc = db.cursor()
	try:
		dc.execute("select id, name from skill")
		while True:
			row = dc.fetchone()
			if not row:
				break
			if row[1] == 'Claws':
				map['Claw'] = row[0]
			elif row[1] == '+MA':
				map['+1 MA'] = row[0]
			elif row[1] == '+AV':
				map['+1 AV'] = row[0]
				map['Spikes'] = row[0]
			elif row[1] == '+AG':
				map['+1 AG'] = row[0]
			elif row[1] == '+ST':
				map['+1 ST'] = row[0]
			map[row[1]] = row[0]
	finally:
		dc.close()
	return map


if __name__ == '__main__':
	assert len(sys.argv) == 7, 'USAGE: %s <legacyDb> <legacyUser> <legacyPass> <newDb> <newUser> <newPass>' % sys.argv[0]
	legacyDb, legacyUser, legacyPass, newDb, newUser, newPass = sys.argv[1:]
	legacy = MySQLdb.connect(db=legacyDb, user=legacyUser, passwd=legacyPass)
	try:
		db = MySQLdb.connect(db=newDb, user=newUser, passwd=newPass)
		try:
			raceMap = raceMap(db)
			coach(legacy, db)
			coachMap = coachMap(db)
			team(legacy, db, coachMap, raceMap)
			positionMap = positionMap(db, raceMap)
			skillMap = skillMap(db)
			player(legacy, db, positionMap, skillMap)
			seasonMap = season(legacy, db)
			game(legacy, db, seasonMap)
		finally:
			db.close()
	finally:
		legacy.close()
