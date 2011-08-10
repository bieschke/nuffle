-- Begin db_init.sql

--
-- This file should be executed exactly once for every installation
-- of the Blood Bowl Web Manager.
-- 
-- First this script creates all of the tables. Second, it populates
-- these tables with basic data.
--
-- The following versions of MySQL are used by the developers, and are
-- known to function correctly with this script.
-- 
-- Server version	3.23.36  (eshin)
-- Server version	3.23.54  (oberon7)
--

--
-- Common fields:
--
--  profile : public data (for display on web)
--  notes : private data (for internal use)
--

--
-- Table structure for table 'coaches'
--
--  password : encrypted using crypt(); NULL means no password required
--  sid : session cookie for authentication
--  admin : sys admin status
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ coaches (
  username varchar(8) NOT NULL default '',
  password varchar(32) binary default NULL,
  realname varchar(50) default NULL,
  email varchar(50) default NULL,
  phone varchar(10) default NULL,
  address1 varchar(50) default NULL,
  address2 varchar(50) default NULL,
  city varchar(50) default NULL,
  state varchar(50) default NULL,
  zip varchar(10) default NULL,
  country varchar(50) default NULL,
  url varchar(128) default NULL,
  admin tinyint(1) unsigned NOT NULL default '0',
  profile text,
  notes text,
  PRIMARY KEY  (username)
) TYPE=MyISAM;

--
-- Table structure for table 'division_teams'
--
--  division_id -> divisions.division_id
--  team_id -> teams.team_id
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ division_teams (
  division_id int(6) unsigned NOT NULL,
  team_id int(6) unsigned NOT NULL,
  PRIMARY KEY  (division_id, team_id)
) TYPE=MyISAM;

--
-- Table structure for table 'divisions'
--
--  league -> leagues.handle
--  season -> seasons.num
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ divisions (
  division_id int(6) unsigned NOT NULL auto_increment,
  league varchar(8) NOT NULL default '',
  season int(6) unsigned NOT NULL default '0',
  name varchar(50) default NULL,
  profile text,
  notes text,
  PRIMARY KEY  (division_id)
) TYPE=MyISAM;

--
-- Table structure for table 'game_players'
--
--  game_id -> games.game_id
--  player_id -> players.game_id
--  missed : player missed game (e.g. due to injury or handicap, but not niggler)
--  niggler : player failed niggler roll
--  thrown_out : player / coach got thrown out
--  injury_id -> injuries.injury_id
--  td : touchdowns
--  cas : casualties
--  comp : completions
--  cat : catches
--  inter : interceptions
--  mvp : MVPs
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ game_players (
  game_id int(6) unsigned NOT NULL default '0',
  player_id int(6) unsigned NOT NULL default '0',
  missed tinyint(1) unsigned NOT NULL default '0',
  niggler tinyint(1) unsigned NOT NULL default '0',
  thrown_out tinyint(1) unsigned NOT NULL default '0',
  injury_id tinyint(3) unsigned NOT NULL default '0',
  td tinyint(1) unsigned NOT NULL default '0',
  cas tinyint(1) unsigned NOT NULL default '0',
  comp tinyint(1) unsigned NOT NULL default '0',
  cat tinyint(1) unsigned NOT NULL default '0',
  inter tinyint(1) unsigned NOT NULL default '0',
  mvp tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (game_id,player_id)
) TYPE=MyISAM;

--
-- Table structure for table 'game_teams'
--
--  game_id -> games.game_id
--  tr : team rating before match
--  score : score for this 
--  ff : change in fan factor (e.g. '-1', '0', or '1')
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ game_teams (
  game_id int(6) unsigned NOT NULL default '0',
  team_id int(6) unsigned NOT NULL default '0',
  tr smallint(3) unsigned default NULL,
  score tinyint(1) unsigned default NULL,
  winnings int(8) default NULL,
  ff tinyint(1) default NULL,
  profile text,
  notes text,
  PRIMARY KEY  (game_id,team_id)
) TYPE=MyISAM;

--
-- Table structure for table 'games'
--
--  league -> league.handle
--  season -> seasons.num
--  week : sets order of games
--  deadline : optional deadline set by commish
--  date_played : actual date game was played
--  periods : number of periods played (no OT = 2)
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ games (
  game_id int(6) unsigned NOT NULL auto_increment,
  league varchar(8) NOT NULL default '',
  season int(6) unsigned NOT NULL default '0',
  week tinyint(2) unsigned NOT NULL default '0',
  deadline date default NULL,
  date_played date default NULL,
  gate mediumint(8) unsigned default NULL,
  periods tinyint(1) unsigned default NULL,
  verified tinyint(1) unsigned NOT NULL default '0',
  profile text,
  notes text,
  PRIMARY KEY  (game_id)
) TYPE=MyISAM;

--
-- Table structure for table 'injuries'
--
--  name : description of injury (e.g. 'Smashed Hand')
--  aging : boolean; denotes injury due to aging
--  roll : dice roll required for injury
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ injuries (
  injury_id tinyint(3) unsigned NOT NULL auto_increment,
  name varchar(30) NOT NULL default '',
  aging tinyint(1) unsigned NOT NULL default '0',
  roll varchar(5) NOT NULL default '',
  effect enum('Miss Next Game','Niggling Injury','-1 MA','-1 ST','-1 AG','-1 AV','Dead') NOT NULL default 'Miss Next Game',
  PRIMARY KEY  (injury_id)
) TYPE=MyISAM;

--
-- Table structure for table 'league_admins'
--
--  league -> leagues.handle
--  coach -> coaches.username
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ league_admins (
  league varchar(8) NOT NULL default '',
  coach varchar(8) NOT NULL default '',
  PRIMARY KEY  (league,coach)
) TYPE=MyISAM;

--
-- Table structure for table 'leagues'
--
--  curr_season -> current seasons.num
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ leagues (
  handle varchar(8) NOT NULL default '',
  name varchar(50) default NULL,
  curr_season int(6) unsigned NOT NULL default '0',
  profile text,
  notes text,
  PRIMARY KEY  (handle)
) TYPE=MyISAM;

--
-- Table structure for table 'levels'
--
--  spp : minimum spp required to reach level
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ levels (
  name varchar(30) NOT NULL default '',
  spp tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (name)
) TYPE=MyISAM;

--
-- Table structure for table 'news'
--
--  league -> leagues.handle
--  weight -> news ordered by weight DESC
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ news (
  story_id int(6) unsigned NOT NULL auto_increment,
  league varchar(8) NOT NULL default '',
  status enum('Breaking News','Archive','Hidden') NOT NULL default 'Breaking News',
  story_date timestamp(14) NOT NULL,
  story_weight tinyint(2) unsigned NOT NULL default '0',
  headline varchar(100) default NULL,
  lead text,
  PRIMARY KEY  (story_id)
) TYPE=MyISAM;

--
-- Table structure for table 'player_advances'
--
--  player_id -> players.player_id
--  num : number of advance (order)
--  advance : NULL if not rolled yet
--  skill -> skills.name ('' if no skill, NULL if skill not yet picked)
--  injury_id -> injuries.injury_id ('' if no aging, NULL if not rolled yet)
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ player_advances (
  player_id int(6) unsigned NOT NULL default '0',
  num tinyint(3) unsigned NOT NULL auto_increment,
  advance enum('Skill','+1 MA','+1 AG','+1 ST') default NULL,
  skill varchar(50) default NULL,
  injury_id tinyint(3) unsigned default NULL,
  PRIMARY KEY  (player_id,num)
) TYPE=MyISAM;

--
-- Table structure for table 'players'
--
--  position -> positions.name
--  team_id -> teams.team_id (NULL if no current team, e.g. unhired Star Player)
--  pos : position number (e.g. 1-16)
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ players (
  player_id int(6) unsigned NOT NULL auto_increment,
  position varchar(30) NOT NULL default '',
  team_id int(6) unsigned default NULL,
  name varchar(50) default NULL,
  pos char(3) default NULL,
  status enum('Active','Injured','Retired','Dead') NOT NULL default 'Active',
  profile text,
  notes text,
  PRIMARY KEY  (player_id)
) TYPE=MyISAM;

--
-- Table structure for table 'position_skills'
--
--  position -> positions.name
--  skill -> skills.name
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ position_skills (
  position varchar(30) NOT NULL default '',
  skill varchar(30) NOT NULL default '',
  PRIMARY KEY  (position,skill)
) TYPE=MyISAM;

--
-- Table structure for table 'positions'
--
--  ma : starting MA
--  st : starting ST
--  ag : starting AG
--  av : starting AV
--  skill_class : skill classes allowed
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ positions (
  name varchar(30) NOT NULL default '',
  class enum('Regular','Big Guy','Star Player','Staff') NOT NULL default 'Regular',
  ma tinyint(1) unsigned default NULL,
  st tinyint(1) unsigned default NULL,
  ag tinyint(1) unsigned default NULL,
  av tinyint(1) unsigned default NULL,
  skill_class set('General','Agility','Strength','Passing','Physical') NOT NULL default '',
  PRIMARY KEY  (name)
) TYPE=MyISAM;

--
-- Table structure for table 'race_positions'
--
--  race -> races.name
--  position -> positions.name
--  min : minimum number of this position required
--  max : maximum number of this position allowed (0 = no max)
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ race_positions (
  race varchar(30) NOT NULL default '',
  position varchar(30) NOT NULL default '',
  min tinyint(2) unsigned NOT NULL default '0',
  max tinyint(2) unsigned NOT NULL default '0',
  cost mediumint(8) unsigned NOT NULL default '0',
  PRIMARY KEY  (race,position)
) TYPE=MyISAM;

--
-- Table structure for table 'races'
--
--  rr_cost : cost for rerolls
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ races (
  name varchar(30) NOT NULL default '',
  rr_cost mediumint(8) unsigned NOT NULL default '0',
  PRIMARY KEY  (name)
) TYPE=MyISAM;

--
-- Table structure for table 'seasons'
--
--  league -> leagues.handle
--  num : order of season
--  startdate : optional start date of season
--  enddate : optional end date of season
--  open : boolean; denotes open type season (no set schedule)
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ seasons (
  league varchar(8) NOT NULL default '',
  num int(6) unsigned NOT NULL auto_increment,
  name varchar(50) default NULL,
  startdate date default NULL,
  enddate date default NULL,
  open tinyint(1) unsigned default '0',
  curr_week tinyint(2) unsigned NOT NULL default '0',
  profile text,
  format text,
  rules text,
  notes text,
  PRIMARY KEY  (league,num)
) TYPE=MyISAM;

--
-- Table structure for table 'skills'
--
--  copy : text of skill
--  notes : notes on rulings
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ skills (
  name varchar(30) NOT NULL default '',
  class enum('General','Agility','Strength','Passing','Physical','Racial Characteristic','Secret Weapon','Staff Ability') NOT NULL default 'General',
  trait tinyint(1) unsigned default '0',
  copy text,
  notes text,
  PRIMARY KEY  (name)
) TYPE=MyISAM;

--
-- Table structure for table 'team_log'
--
--  team_id -> teams.team_id
--  ts : timestamp of entry
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ team_log (
  log_id int(6) unsigned NOT NULL auto_increment,
  team_id int(6) unsigned NOT NULL default '0',
  ts timestamp(14) NOT NULL,
  entry text,
  PRIMARY KEY  (log_id)
) TYPE=MyISAM;

--
-- Table structure for table 'teams'
--
--  division_id -> divisions.division_id
--  coach -> coaches.username
--  race -> races.name
--  treasury : current treasury
--  ff : current fan factor
--  rr : current rerolls
--

CREATE TABLE /*!32312 IF NOT EXISTS*/ teams (
  team_id int(6) unsigned NOT NULL auto_increment,
  coach varchar(8) NOT NULL default '',
  race varchar(30) NOT NULL default '',
  name varchar(50) default NULL,
  treasury mediumint(8) unsigned NOT NULL default '0',
  ff tinyint(3) unsigned NOT NULL default '0',
  rr tinyint(3) unsigned NOT NULL default '0',
  retired tinyint(1) unsigned NOT NULL default '0',
  profile text,
  notes text,
  PRIMARY KEY  (team_id)
) TYPE=MyISAM;

--
-- Now that all the tables have been created, populate
-- them with some meaningful baseline data.
--

SOURCE data/amazons.sql;
SOURCE data/bg.sql;
SOURCE data/chaos.sql;
SOURCE data/chaos_dwarf.sql;
SOURCE data/coaches.sql;
SOURCE data/dark_elf.sql;
SOURCE data/dwarf.sql;
SOURCE data/goblin.sql;
SOURCE data/halfling.sql;
SOURCE data/high_elf.sql;
SOURCE data/human.sql;
SOURCE data/injuries.sql;
SOURCE data/leagues.sql;
SOURCE data/levels.sql;
SOURCE data/lizardman.sql;
SOURCE data/norse.sql;
SOURCE data/orc.sql;
SOURCE data/skaven.sql;
SOURCE data/skills.sql;
SOURCE data/staff.sql;
SOURCE data/undead.sql;
SOURCE data/wood_elf.sql;


-- End db_init.sql
