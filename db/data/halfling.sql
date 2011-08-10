-- Begin halfling.sql

-- Halfling

INSERT INTO races VALUES ('Halfling',60000);

-- Halfling

INSERT INTO race_positions VALUES ('Halfling','Halfling',0,16,30000);
INSERT INTO positions VALUES ('Halfling','Regular',5,2,3,6,'Agility');
INSERT INTO position_skills VALUES ('Halfling','Dodge');
INSERT INTO position_skills VALUES ('Halfling','Right Stuff');
INSERT INTO position_skills VALUES ('Halfling','Stunty');

-- Big Guys

INSERT INTO race_positions VALUES ('Halfling','Ogre',0,2,120000);
INSERT INTO race_positions VALUES ('Halfling','Treeman',0,2,110000);

-- Staff

INSERT INTO race_positions VALUES ('Halfling','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Halfling','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Halfling','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Halfling','Cheerleader',0,0,10000);

-- End halfling.sql
