-- saep_db.sql | MySQL 8+ | Uso: mysql -u root -p < saep_db.sql
DROP DATABASE IF EXISTS saep_db;
CREATE DATABASE saep_db_v1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE saep_db_v1;

CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  login VARCHAR(50) NOT NULL UNIQUE,
  senha_hash CHAR(60) NOT NULL,            -- bcrypt
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120) NOT NULL,
  cpf_hash CHAR(60) NOT NULL,              -- CPF criptografado com bcrypt (LGPD)
  telefone VARCHAR(20),
  email VARCHAR(120),
  endereco VARCHAR(200),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE veiculos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id INT NOT NULL,
  placa VARCHAR(7) NOT NULL UNIQUE,
  marca VARCHAR(50) NOT NULL,
  modelo VARCHAR(50) NOT NULL,
  ano SMALLINT NOT NULL,
  cor VARCHAR(30),
  CONSTRAINT fk_veiculo_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE servicos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  descricao VARCHAR(100) NOT NULL,
  valor DECIMAL(10,2) NOT NULL
);

CREATE TABLE agendamentos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  veiculo_id INT NOT NULL,
  servico_id INT NOT NULL,
  data_agendamento DATETIME NOT NULL,
  status ENUM('AGENDADO','EM_ANDAMENTO','CONCLUIDO','CANCELADO') NOT NULL DEFAULT 'AGENDADO',
  observacao VARCHAR(255),
  CONSTRAINT fk_ag_veiculo FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
  CONSTRAINT fk_ag_servico FOREIGN KEY (servico_id) REFERENCES servicos(id)
);

-- Senhas de teste: admin/admin123 | carlos/carlos123 | ana/ana12345
INSERT INTO usuarios (nome, login, senha_hash) VALUES
('Administrador','admin','$2b$10$qizaoAEHzt5Hz/vRqXSL.uYENkSH9GpokflvL.8V1mn3QEBTyXZiO'),
('Carlos Mecânico','carlos','$2b$10$r32LnLIp2cB54XivPH1Nau70ftffbmF3BPyPm8.VZIBkgD4MR.KTK'),
('Ana Atendente','ana','$2b$10$UWZ0bg.GPd50uIKOhkyUqu3.n4ceo3X8ZX.P1S.wQlNfqh88D6mTO');

-- CPFs de teste (válidos): 529.982.247-25 | 111.444.777-35 | 390.533.447-05
INSERT INTO clientes (nome, cpf_hash, telefone, email, endereco) VALUES
('João da Silva','$2b$10$KhQB9kIqUe31KTL6YcE3ouJPBhHvYgzEdile2lXILS36A55FGFk7W','(11) 98888-1111','joao@email.com','Rua das Flores, 100 - São Paulo/SP'),
('Maria Oliveira','$2b$10$bsggD78dGRaHNDAG42jEwu7aPq/utYq/OIk1bqaDFPECHp2yoTthG','(11) 97777-2222','maria@email.com','Av. Paulista, 2000 - São Paulo/SP'),
('Pedro Santos','$2b$10$hceDyXaqS2nBr69H/FWUZuwqw3sBhxfin.Zzi4tVisZ4NWCNZVC3K','(11) 96666-3333','pedro@email.com','Rua Augusta, 350 - São Paulo/SP');

INSERT INTO veiculos (cliente_id, placa, marca, modelo, ano, cor) VALUES
(1,'ABC1D23','Fiat','Uno',2015,'Branco'),
(2,'EFG4H56','Volkswagen','Gol',2018,'Prata'),
(3,'IJK7L89','Chevrolet','Onix',2021,'Preto');

INSERT INTO servicos (descricao, valor) VALUES
('Troca de óleo e filtro',180.00),
('Alinhamento e balanceamento',150.00),
('Revisão de freios',320.00);

INSERT INTO agendamentos (veiculo_id, servico_id, data_agendamento, status, observacao) VALUES
(1,1,'2026-11-03 09:00:00','AGENDADO','Cliente prefere atendimento pela manhã'),
(2,3,'2026-11-01 14:30:00','AGENDADO','Barulho ao frear'),
(3,2,'2026-11-05 10:00:00','AGENDADO',NULL);
