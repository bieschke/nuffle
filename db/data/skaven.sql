-- Begin skaven.sql

-- Skaven

INSERT INTO races VALUES ('Skaven',60000);

-- Lineman

INSERT INTO race_positions VALUES ('Skaven','Skaven Lineman',0,12,50000);
INSERT INTO positions VALUES ('Skaven Lineman','Regular',7,3,3,7,'General,Physical');

-- Thrower

INSERT INTO race_positions VALUES ('Skaven','Skaven Thrower',0,2,70000);
INSERT INTO positions VALUES ('Skaven Thrower','Regular',7,3,3,7,'General,Passing,Physical');
INSERT INTO position_skills VALUES ('Skaven Thrower','Pass');
INSERT INTO position_skills VALUES ('Skaven Thrower','Sure Hands');

-- Gutter Runner

INSERT INTO race_positions VALUES ('Skaven','Gutter Runner',0,4,80000);
INSERT INTO positions VALUES ('Gutter Runner','Regular',9,2,4,7,'General,Agility,Physical');
INSERT INTO position_skills VALUES ('Gutter Runner','Dodge');

-- Storm Vermin

INSERT INTO race_positions VALUES ('Skaven','Storm Vermin',0,2,90000);
INSERT INTO positions VALUES ('Storm Vermin','Regular',7,3,3,8,'General,Strength,Physical');
INSERT INTO position_skills VALUES ('Storm Vermin','Block');

-- Big Guys

INSERT INTO race_positions VALUES ('Skaven','Rat Ogre',0,1,130000);

-- Staff

INSERT INTO race_positions VALUES ('Skaven','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Skaven','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Skaven','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Skaven','Cheerleader',0,0,10000);

-- End skaven.sql
