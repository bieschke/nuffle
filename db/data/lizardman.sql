-- Begin lizardman.sql

-- Lizardman

INSERT INTO races VALUES ('Lizardman',60000);

-- Skink

INSERT INTO race_positions VALUES ('Lizardman','Skink',0,12,60000);
INSERT INTO positions VALUES ('Skink','Regular',8,2,3,7,'Agility');
INSERT INTO position_skills VALUES ('Skink','Dodge');
INSERT INTO position_skills VALUES ('Skink','Stunty');

-- Saurus

INSERT INTO race_positions VALUES ('Lizardman','Saurus',0,6,80000);
INSERT INTO positions VALUES ('Saurus','Regular',6,4,1,9,'General,Strength');

-- Big Guys

INSERT INTO race_positions VALUES ('Lizardman','Kroxigor',0,1,130000);

-- Staff

INSERT INTO race_positions VALUES ('Lizardman','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Lizardman','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Lizardman','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Lizardman','Cheerleader',0,0,10000);

-- End lizardman.sql
