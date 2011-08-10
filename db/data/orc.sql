-- Begin orc.sql

-- Orc

INSERT INTO races VALUES ('Orc',60000);

-- Lineman

INSERT INTO race_positions VALUES ('Orc','Orc Lineman',0,12,50000);
INSERT INTO positions VALUES ('Orc Lineman','Regular',5,3,3,9,'General');

-- Thrower

INSERT INTO race_positions VALUES ('Orc','Orc Thrower',0,2,70000);
INSERT INTO positions VALUES ('Orc Thrower','Regular',5,3,3,8,'General,Passing');
INSERT INTO position_skills VALUES ('Orc Thrower','Pass');
INSERT INTO position_skills VALUES ('Orc Thrower','Sure Hands');

-- Black Orc

INSERT INTO race_positions VALUES ('Orc','Black Orc Blocker',0,4,80000);
INSERT INTO positions VALUES ('Black Orc Blocker','Regular',4,4,2,9,'General,Strength');

-- Blitzer

INSERT INTO race_positions VALUES ('Orc','Orc Blitzer',0,4,80000);
INSERT INTO positions VALUES ('Orc Blitzer','Regular',6,3,3,9,'General,Strength');
INSERT INTO position_skills VALUES ('Orc Blitzer','Block');

-- Allies

INSERT INTO race_positions VALUES ('Orc','Goblin',0,4,40000);

-- Big Guys

INSERT INTO race_positions VALUES ('Orc','Ogre',0,1,120000);
INSERT INTO race_positions VALUES ('Orc','Troll',0,1,100000);

-- Staff

INSERT INTO race_positions VALUES ('Orc','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Orc','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Orc','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Orc','Cheerleader',0,0,10000);

-- End orc.sql
