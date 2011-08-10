-- Begin goblin.sql

-- Goblin

INSERT INTO races VALUES ('Goblin',60000);

-- Goblin

INSERT INTO race_positions VALUES ('Goblin','Goblin',0,16,40000);
INSERT INTO positions VALUES ('Goblin','Regular',6,2,3,7,'Agility');
INSERT INTO position_skills VALUES ('Goblin','Dodge');
INSERT INTO position_skills VALUES ('Goblin','Right Stuff');
INSERT INTO position_skills VALUES ('Goblin','Stunty');

-- Big Guys

INSERT INTO race_positions VALUES ('Goblin','Ogre',0,2,120000);
INSERT INTO race_positions VALUES ('Goblin','Troll',0,2,100000);

-- Staff

INSERT INTO race_positions VALUES ('Goblin','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Goblin','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Goblin','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Goblin','Cheerleader',0,0,10000);

-- End goblin.sql
