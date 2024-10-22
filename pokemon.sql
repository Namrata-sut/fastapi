-- pokemon_database_creation
CREATE DATABASE Pokemon;

-- pokemon_database_seq_creation.sql
CREATE SEQUENCE pokemon_data_id_seq;

-- pokemon_table_creation.sql
CREATE TABLE pokemon_data_test_3 (
--    id INTEGER PRIMARY KEY DEFAULT nextval('pokemon_data_id_seq'::regclass),
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    type_1 VARCHAR(40) NOT NULL,
    type_2 VARCHAR(40),
    total INTEGER NOT NULL,
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    sp_atk INTEGER NOT NULL,
    sp_def INTEGER NOT NULL,
    speed INTEGER NOT NULL,
    generation INTEGER NOT NULL,
    legendary BOOLEAN NOT NULL
);

-- pokemon_table_insert.sql
INSERT INTO pokemon_data_test_3 (name, type_1, type_2, total, hp, attack, defense, sp_atk, sp_def, speed, generation, legendary)
VALUES
    ('Bulbasaur', 'Grass', 'Poison', 318, 45, 49, 49, 65, 65, 45, 1, false),
    ('Pikachu', 'Electric', NULL, 320, 35, 55, 40, 50, 50, 90, 1, false)

-- pokemon_table_delete_by_id.sql
DELETE FROM pokemon_data_test_3 WHERE id = 1;
DELETE FROM pokemon_data_test_3 WHERE name = 'Pikachu';
