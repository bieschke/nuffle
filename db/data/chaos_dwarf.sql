-- Begin chaos_dwarf.sql

-- Chaos Dwarf

INSERT INTO races VALUES ('Chaos Dwarf',50000);

-- Hobgoblin

INSERT INTO race_positions VALUES ('Chaos Dwarf','Hobgoblin',0,12,40000);
INSERT INTO positions VALUES ('Hobgoblin','Regular',6,3,3,7,'General');

-- Chaos Dwarf Blocker

INSERT INTO race_positions VALUES ('Chaos Dwarf','Chaos Dwarf Blocker',0,6,70000);
INSERT INTO positions VALUES ('Chaos Dwarf Blocker','Regular',4,3,2,9,'General,Strength');
INSERT INTO position_skills VALUES ('Chaos Dwarf Blocker','Block');
INSERT INTO position_skills VALUES ('Chaos Dwarf Blocker','Tackle');
INSERT INTO position_skills VALUES ('Chaos Dwarf Blocker','Thick Skull');

-- Bull Centaur

INSERT INTO positions VALUES ('Bull Centaur','Regular',6,4,2,9,'General,Strength');
INSERT INTO race_positions VALUES ('Chaos Dwarf','Bull Centaur',0,2,130000);
INSERT INTO position_skills VALUES ('Bull Centaur','Sprint');
INSERT INTO position_skills VALUES ('Bull Centaur','Sure Feet');
INSERT INTO position_skills VALUES ('Bull Centaur','Thick Skull');

-- Big Guys

INSERT INTO race_positions VALUES ('Chaos Dwarf','Minotaur',0,1,110000);
INSERT INTO race_positions VALUES ('Chaos Dwarf','Troll',0,1,100000);

-- Staff

INSERT INTO race_positions VALUES ('Chaos Dwarf','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Chaos Dwarf','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Chaos Dwarf','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Chaos Dwarf','Cheerleader',0,0,10000);

-- End chaos_dwarf.sql
