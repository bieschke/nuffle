-- Begin chaos.sql

-- Chaos

INSERT INTO races VALUES ('Chaos',70000);

-- Beastman

INSERT INTO race_positions VALUES ('Chaos','Chaos Beastman',0,12,60000);
INSERT INTO positions VALUES ('Chaos Beastman','Regular',6,3,3,8,'General,Strength,Physical');
INSERT INTO position_skills VALUES ('Chaos Beastman','Horns');

-- Chaos Warrior

INSERT INTO race_positions VALUES ('Chaos','Chaos Warrior',0,1,100000);
INSERT INTO positions VALUES ('Chaos Warrior','Regular',5,4,3,9,'General,Strength,Physical');

-- Staff

INSERT INTO race_positions VALUES ('Chaos','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Chaos','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Chaos','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Chaos','Cheerleader',0,0,10000);

-- Big Guys

INSERT INTO race_positions VALUES ('Chaos','Minotaur',0,1,110000);
INSERT INTO race_positions VALUES ('Chaos','Ogre',0,1,120000);
INSERT INTO race_positions VALUES ('Chaos','Troll',0,1,100000);

-- End chaos.sql
