-- Begin wood_elf.sql

-- Wood Elf

INSERT INTO races VALUES ('Wood Elf',50000);

-- Lineman

INSERT INTO race_positions VALUES ('Wood Elf','Wood Elf Lineman',0,12,70000);
INSERT INTO positions VALUES ('Wood Elf Lineman','Regular',7,3,4,7,'General,Agility');

-- Catcher

INSERT INTO race_positions VALUES ('Wood Elf','Wood Elf Catcher',0,4,90000);
INSERT INTO positions VALUES ('Wood Elf Catcher','Regular',9,2,4,7,'General,Agility');
INSERT INTO position_skills VALUES ('Wood Elf Catcher','Catch');
INSERT INTO position_skills VALUES ('Wood Elf Catcher','Dodge');

-- Thrower

INSERT INTO race_positions VALUES ('Wood Elf','Wood Elf Thrower',0,2,90000);
INSERT INTO positions VALUES ('Wood Elf Thrower','Regular',7,3,4,7,'General,Agility,Passing');
INSERT INTO position_skills VALUES ('Wood Elf Thrower','Pass');

-- Wardancer

INSERT INTO race_positions VALUES ('Wood Elf','Wardancer',0,2,120000);
INSERT INTO positions VALUES ('Wardancer','Regular',8,3,4,7,'General,Agility');
INSERT INTO position_skills VALUES ('Wardancer','Block');
INSERT INTO position_skills VALUES ('Wardancer','Dodge');
INSERT INTO position_skills VALUES ('Wardancer','Leap');

-- Big Guys

INSERT INTO race_positions VALUES ('Wood Elf','Treeman',0,1,110000);

-- Staff

INSERT INTO race_positions VALUES ('Wood Elf','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Wood Elf','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Wood Elf','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Wood Elf','Cheerleader',0,0,10000);

-- End wood_elf.sql
