-- Begin high_elf.sql

-- High Elf

INSERT INTO races VALUES ('High Elf',50000);

-- Lineman

INSERT INTO race_positions VALUES ('High Elf','High Elf Lineman',0,12,70000);
INSERT INTO positions VALUES ('High Elf Lineman','Regular',6,3,4,8,'General,Agility');

-- Phoenix Warrior

INSERT INTO race_positions VALUES ('High Elf','Phoenix Warrior',0,2,80000);
INSERT INTO positions VALUES ('Phoenix Warrior','Regular',6,3,4,8,'General,Agility,Passing');
INSERT INTO position_skills VALUES ('Phoenix Warrior','Pass');

-- Lion Warrior

INSERT INTO race_positions VALUES ('High Elf','Lion Warrior',0,4,90000);
INSERT INTO positions VALUES ('Lion Warrior','Regular',8,3,4,7,'General,Agility');
INSERT INTO position_skills VALUES ('Lion Warrior','Catch');

-- Dragon Warrior

INSERT INTO race_positions VALUES ('High Elf','Dragon Warrior',0,2,100000);
INSERT INTO positions VALUES ('Dragon Warrior','Regular',7,3,4,8,'General,Agility');
INSERT INTO position_skills VALUES ('Dragon Warrior','Block');

-- Staff

INSERT INTO race_positions VALUES ('High Elf','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('High Elf','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('High Elf','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('High Elf','Cheerleader',0,0,10000);

-- End high_elf.sql
