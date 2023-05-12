-- DROP DATABASE study_db ;
CREATE DATABASE study_db;
USE study_db;

CREATE TABLE info(username VARCHAR(200), password VARCHAR(500), name VARCHAR(100), profile INT, phone VARCHAR(32), time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(username));

CREATE TABLE plans(name VARCHAR(100), topics VARCHAR(100), name_livros VARCHAR(100) ,PRIMARY KEY(name));

CREATE TABLE professors(username VARCHAR(200), PRIMARY KEY(username), FOREIGN KEY(username) references info(username));

CREATE TABLE alunos(username VARCHAR(200), plan VARCHAR(100), professor VARCHAR(200), PRIMARY KEY(username), FOREIGN KEY(username) references info(username), FOREIGN KEY(plan) references plans(name), FOREIGN KEY(professor) references professors(username));

CREATE TABLE secretaria(username VARCHAR(200), PRIMARY KEY(username), FOREIGN KEY(username) references info(username));

CREATE TABLE progress(username VARCHAR(200), date DATE, daily_result VARCHAR(200), rate VARCHAR(200), time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(username, date), FOREIGN KEY(username) references alunos(username));

CREATE TABLE livros(name VARCHAR(200), count INT,PRIMARY KEY(name));

INSERT INTO info(username, password, name, profile, phone) VALUES('hiago', '$5$rounds=535000$CUiEsvrYrO/d.JfC$2p44wvE.pdj7TGhHWJE3XUM2lGz/5Y57BtFuqF4bJ23', 'Hiago Lopes', 1, 123456789); -- password: admin1
INSERT INTO plans( name) VALUES('Machine learning');
INSERT INTO plans( name) VALUES('Engenharia de Software');
INSERT INTO plans( name) VALUES('Linhas de produto de software');


SELECT * FROM info;
SELECT * FROM alunos;
SELECT * FROM professors;
SELECT * FROM secretaria;
SELECT * FROM livros;
SELECT * FROM plans;
SELECT * FROM progress;


