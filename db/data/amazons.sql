-- Begin amazons.sql

-- Amazons

INSERT INTO races VALUES ('Amazons',40000);

-- Linewoman

INSERT INTO race_positions VALUES ('Amazons','Amazon Linewoman',0,12,50000);
INSERT INTO positions VALUES ('Amazon Linewoman','Regular',6,3,3,7,'General');
INSERT INTO position_skills VALUES ('Amazon Linewoman','Dodge');

-- Catcher

INSERT INTO race_positions VALUES ('Amazons','Amazon Catcher',0,2,70000);
INSERT INTO positions VALUES ('Amazon Catcher','Regular',6,3,3,7,'General,Agility');
INSERT INTO position_skills VALUES ('Amazon Catcher','Catch');
INSERT INTO position_skills VALUES ('Amazon Catcher','Dodge');

-- Thrower

INSERT INTO race_positions VALUES ('Amazons','Amazon Thrower',0,2,70000);
INSERT INTO positions VALUES ('Amazon Thrower','Regular',6,3,3,7,'General,Passing');
INSERT INTO position_skills VALUES ('Amazon Thrower','Dodge');
INSERT INTO position_skills VALUES ('Amazon Thrower','Pass');

-- Amazon Blitzer

INSERT INTO positions VALUES ('Amazon Blitzer','Regular',6,3,3,7,'General,Strength');
INSERT INTO race_positions VALUES ('Amazons','Amazon Blitzer',0,4,90000);
INSERT INTO position_skills VALUES ('Amazon Blitzer','Block');
INSERT INTO position_skills VALUES ('Amazon Blitzer','Dodge');

-- Staff

INSERT INTO race_positions VALUES ('Amazons','Head Coach',1,1,0);
INSERT INTO race_positions VALUES ('Amazons','Apothecary',0,1,50000);
INSERT INTO race_positions VALUES ('Amazons','Assistant Coach',0,0,10000);
INSERT INTO race_positions VALUES ('Amazons','Cheerleader',0,0,10000);

-- End amazons.sql
