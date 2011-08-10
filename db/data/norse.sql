-- Begin norse.sql

-- Norse

INSERT INTO races VALUES ('Norse',60000);

-- Lineman

INSERT INTO race_positions VALUES ('Norse','Norse Lineman',0,12,50000);
INSERT INTO positions VALUES ('Norse Lineman','Regular',6,3,3,7,'General');
INSERT INTO position_skills VALUES ('Norse Lineman','Block');

-- Catcher

INSERT INTO race_positions VALUES ('Norse','Norse Catcher',0,2,70000);
INSERT INTO positions VALUES ('Norse Catcher','Regular',6,3,3,7,'General,Agility');
INSERT INTO position_skills VALUES ('Norse Catcher','Block');
INSERT INTO position_skills VALUES ('Norse Catcher','Catch');

-- Thrower

INSERT INTO race_positions VALUES ('Norse','Norse Thrower',0,2,70000);
INSERT INTO positions VALUES ('Norse Thrower','Regular',6,3,3,7,'General,Passing');
INSERT INTO position_skills VALUES ('Norse Thrower','Block');
INSERT INTO position_skills VALUES ('Norse Thrower','Pass');

-- Blitzer

INSERT INTO race_positions VALUES ('Norse','Norse Blitzer',0,4,90000);
INSERT INTO positions VALUES ('Norse Blitzer','Regular',6,3,3,7,'General,Strength');
INSERT INTO position_skills VALUES ('Norse Blitzer','Block');
INSERT INTO position_skills VALUES ('Norse Blitzer','Frenzy');
INSERT INTO position_skills VALUES ('Norse Blitzer','Jump Up');

-- Big Guys

INSERT INTO race_positions VALUES ('Norse','Minotaur',0,1,110000);
INSERT INTO race_positions VALUES ('Norse','Ogre',0,1,120000);

-- Staff

INSERT INTO race_positions VALUES ('Norse','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Norse','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Norse','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Norse','Cheerleader',0,0,10000);

-- End norse.sql
