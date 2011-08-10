-- Begin undead.sql

-- Undead

INSERT INTO races VALUES ('Undead',70000);

-- Skeleton

INSERT INTO race_positions VALUES ('Undead','Skeleton',0,12,30000);
INSERT INTO positions VALUES ('Skeleton','Regular',5,3,2,7,'General');
INSERT INTO position_skills VALUES ('Skeleton','Regeneration');

-- Zombie

INSERT INTO race_positions VALUES ('Undead','Zombie',0,12,30000);
INSERT INTO positions VALUES ('Zombie','Regular',4,3,2,8,'General');
INSERT INTO position_skills VALUES ('Zombie','Regeneration');

-- Ghoul

INSERT INTO race_positions VALUES ('Undead','Ghoul',0,4,70000);
INSERT INTO positions VALUES ('Ghoul','Regular',7,3,3,7,'General,Agility');
INSERT INTO position_skills VALUES ('Ghoul','Dodge');

-- Wight

INSERT INTO race_positions VALUES ('Undead','Wight',0,4,90000);
INSERT INTO positions VALUES ('Wight','Regular',6,3,3,8,'General');
INSERT INTO position_skills VALUES ('Wight','Block');
INSERT INTO position_skills VALUES ('Wight','Regeneration');

-- Mummy

INSERT INTO race_positions VALUES ('Undead','Mummy',0,2,100000);
INSERT INTO positions VALUES ('Mummy','Regular',3,5,1,9,'General,Strength');
INSERT INTO position_skills VALUES ('Mummy','Mighty Blow');
INSERT INTO position_skills VALUES ('Mummy','Regeneration');

-- Staff

INSERT INTO race_positions VALUES ('Undead','Necromancer',1,1,0);
INSERT INTO race_positions VALUES ('Undead','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Undead','Cheerleader',0,0,10000);

-- End undead.sql
