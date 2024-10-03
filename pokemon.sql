-- pokemon_database_creation
CREATE DATABASE Pokemon;

-- pokemon_table_creation.sql
CREATE TABLE pokemon_data_test_3 (
    id INTEGER PRIMARY KEY DEFAULT nextval('pokemon_data_id_seq'::regclass),
    name VARCHAR(40),
    type_1 VARCHAR(40),
    type_2 VARCHAR(40),
    total INTEGER,
    hp INTEGER,
    attack INTEGER,
    defense INTEGER,
    sp_atk INTEGER,
    sp_def INTEGER,
    speed INTEGER,
    generation INTEGER,
    legendary BOOLEAN
);

-- pokemon_table_insert.sql
INSERT INTO pokemon_data_test_3 (name, type_1, type_2, total, hp, attack, defense, sp_atk, sp_def, speed, generation, legendary)
VALUES
    ('Bulbasaur', 'Grass', 'Poison', 318, 45, 49, 49, 65, 65, 45, 1, false),
    ('Pikachu', 'Electric', NULL, 320, 35, 55, 40, 50, 50, 90, 1, false)

-- pokemon_table_delete_by_id.sql
DELETE FROM pokemon_data_test_3 WHERE id = 1;
DELETE FROM pokemon_data_test_3 WHERE name = 'Pikachu';
