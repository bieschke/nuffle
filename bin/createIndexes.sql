create index coach_realname_idx on coach (realname);
create index double_access_position_id_idx on double_access (position_id);
create index double_access_skill_category_id_idx on double_access (skill_category_id);
create index game_date_idx on game (date);
create index game_season_id_idx on game (season_id);
create index game_team_game_id_idx on game_team (game_id);
create index game_team_team_id_idx on game_team (team_id);
create index game_team_score_idx on game_team (score);
create index game_team_player_game_team_id_idx on game_team_player (game_team_id);
create index game_team_player_player_id_idx on game_team_player (player_id);
create index normal_access_position_id_idx on normal_access (position_id);
create index normal_access_skill_category_id_idx on normal_access (skill_category_id);
create index player_position_id_idx on player (position_id);
create index player_team_id_idx on player (team_id);
create index player_number_idx on player (number);
create index player_skill_player_id_idx on player_skill (player_id);
create index player_skill_skill_id_idx on player_skill (skill_id);
create index position_race_id_idx on position (race_id);
create index position_skill_position_id_idx on position_skill (position_id);
create index position_skill_skill_id_idx on position_skill (skill_id);
create index race_name_idx on race (name);
create index season_team_season_id_idx on season_team (season_id);
create index season_team_team_id_idx on season_team (team_id);
create index skill_category_id_idx on skill (category_id);
create index skill_name_idx on skill (name);
create index team_coach_id_idx on team (coach_id);
create index team_race_id_idx on team (race_id);
create index team_name_idx on team (name);
