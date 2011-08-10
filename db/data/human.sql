-- Begin human.sql

-- Human

INSERT INTO races VALUES ('Human',50000);

-- Lineman

INSERT INTO race_positions VALUES ('Human','Human Lineman',0,12,50000);
INSERT INTO positions VALUES ('Human Lineman','Regular',6,3,3,8,'General');

-- Catcher

INSERT INTO race_positions VALUES ('Human','Human Catcher',0,4,70000);
INSERT INTO positions VALUES ('Human Catcher','Regular',8,2,3,7,'General,Agility');
INSERT INTO position_skills VALUES ('Human Catcher','Catch');
INSERT INTO position_skills VALUES ('Human Catcher','Dodge');

-- Thrower

INSERT INTO race_positions VALUES ('Human','Human Thrower',0,2,70000);
INSERT INTO positions VALUES ('Human Thrower','Regular',6,3,3,8,'General,Passing');
INSERT INTO position_skills VALUES ('Human Thrower','Pass');
INSERT INTO position_skills VALUES ('Human Thrower','Sure Hands');

-- Blitzer

INSERT INTO race_positions VALUES ('Human','Human Blitzer',0,4,90000);
INSERT INTO positions VALUES ('Human Blitzer','Regular',7,3,3,8,'General,Strength');
INSERT INTO position_skills VALUES ('Human Blitzer','Block');

-- Big Guys

INSERT INTO race_positions VALUES ('Human','Human Blocker',0,1,120000);

-- Staff

INSERT INTO race_positions VALUES ('Human','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Human','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Human','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Human','Cheerleader',0,0,10000);

-- End human.sql
