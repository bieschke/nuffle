-- Begin dwarf.sql

-- Dwarf

INSERT INTO races VALUES ('Dwarf',40000);

-- Long Beard

INSERT INTO race_positions VALUES ('Dwarf','Long Beard',0,12,70000);
INSERT INTO positions VALUES ('Long Beard','Regular',4,3,2,9,'General,Strength');
INSERT INTO position_skills VALUES ('Long Beard','Block');
INSERT INTO position_skills VALUES ('Long Beard','Tackle');
INSERT INTO position_skills VALUES ('Long Beard','Thick Skull');

-- Runner

INSERT INTO race_positions VALUES ('Dwarf','Dwarf Runner',0,2,80000);
INSERT INTO positions VALUES ('Dwarf Runner','Regular',6,3,3,8,'General,Passing');
INSERT INTO position_skills VALUES ('Dwarf Runner','Sure Hands');
INSERT INTO position_skills VALUES ('Dwarf Runner','Thick Skull');

-- Blitzer

INSERT INTO race_positions VALUES ('Dwarf','Dwarf Blitzer',0,2,80000);
INSERT INTO positions VALUES ('Dwarf Blitzer','Regular',5,3,3,9,'General,Strength');
INSERT INTO position_skills VALUES ('Dwarf Blitzer','Block');
INSERT INTO position_skills VALUES ('Dwarf Blitzer','Thick Skull');

-- Troll Slayer

INSERT INTO race_positions VALUES ('Dwarf','Troll Slayer',0,2,90000);
INSERT INTO positions VALUES ('Troll Slayer','Regular',5,3,2,8,'General,Strength');
INSERT INTO position_skills VALUES ('Troll Slayer','Block');
INSERT INTO position_skills VALUES ('Troll Slayer','Dauntless');
INSERT INTO position_skills VALUES ('Troll Slayer','Frenzy');
INSERT INTO position_skills VALUES ('Troll Slayer','Thick Skull');

-- Big Guys

INSERT INTO race_positions VALUES ('Dwarf','Ogre',0,1,120000);

-- Staff

INSERT INTO race_positions VALUES ('Dwarf','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Dwarf','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Dwarf','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Dwarf','Cheerleader',0,0,10000);

-- End dwarf.sql
