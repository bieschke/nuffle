-- Begin dark_elf.sql

-- Dark Elf

INSERT INTO races VALUES ('Dark Elf',50000);

-- Lineman

INSERT INTO race_positions VALUES ('Dark Elf','Dark Elf Lineman',0,12,70000);
INSERT INTO positions VALUES ('Dark Elf Lineman','Regular',6,3,4,8,'General,Agility');

-- Thrower

INSERT INTO race_positions VALUES ('Dark Elf','Dark Elf Thrower',0,2,90000);
INSERT INTO positions VALUES ('Dark Elf Thrower','Regular',6,3,4,8,'General,Agility,Passing');
INSERT INTO position_skills VALUES ('Dark Elf Thrower','Pass');

-- Blitzer

INSERT INTO race_positions VALUES ('Dark Elf','Dark Elf Blitzer',0,4,100000);
INSERT INTO positions VALUES ('Dark Elf Blitzer','Regular',7,3,4,8,'General,Agility');
INSERT INTO position_skills VALUES ('Dark Elf Blitzer','Block');

-- Witch Elf

INSERT INTO race_positions VALUES ('Dark Elf','Witch Elf',0,2,110000);
INSERT INTO positions VALUES ('Witch Elf','Regular',7,3,4,7,'General,Agility');
INSERT INTO position_skills VALUES ('Witch Elf','Dodge');
INSERT INTO position_skills VALUES ('Witch Elf','Frenzy');
INSERT INTO position_skills VALUES ('Witch Elf','Jump Up');

-- Staff

INSERT INTO race_positions VALUES ('Dark Elf','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Dark Elf','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Dark Elf','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Dark Elf','Cheerleader',0,0,10000);

-- End dark_elf.sql
