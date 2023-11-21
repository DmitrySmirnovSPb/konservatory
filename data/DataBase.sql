DROP DATABASE IF EXISTS `polytechstroy`;

-- Создать базу данных polytechstroy если она еще не создана

CREATE DATABASE IF NOT EXISTS `polytechstroy` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

USE `polytechstroy`;

-- Комментарии к подразделам

CREATE TABLE `notes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `note` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `note` (`note`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- наименование работ и материалов

CREATE TABLE `name_of_works_and_materials` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text,
  PRIMARY KEY (`id`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- обоснование расценки

CREATE TABLE `justification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `position` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `position` (`position`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- Номера локальных смет

CREATE TABLE `estimate_number` (
  `id` int NOT NULL AUTO_INCREMENT,
  `estimate` varchar(512) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `estimate` (`estimate`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- Подрядные организации

CREATE TABLE `contractor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `full_name` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- Сотрудники подрядных организаций

CREATE TABLE `people` (
  `id` int NOT NULL AUTO_INCREMENT,
  `f_name` varchar(32) NOT NULL,
  `l_name` varchar(32) NOT NULL,
  `m_name` varchar(32) NOT NULL,
  `initials` varchar(6) NOT NULL,
  `position` varchar(24) NOT NULL,
  `email` varchar(32) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `company_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  CONSTRAINT `company_id` FOREIGN KEY (`company_id`) REFERENCES `contractor` (`id`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- Разделы сметы

CREATE TABLE `chapter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- Исполнительная документация

CREATE TABLE `executive_documentation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_contractor` int NOT NULL,
  `val_number` varchar(32) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `passed` date DEFAULT NULL,
  `dttc` date DEFAULT NULL,
  `notes_id` int DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_contractor` (`id_contractor`),
  CONSTRAINT `id_contractor` FOREIGN KEY (`id_contractor`) REFERENCES `contractor` (`id`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;

-- Смета консерватории

CREATE TABLE `basic_estimate` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chapter_id` int NOT NULL,
  `number_in_order` varchar(12) DEFAULT NULL,
  `estimate_id` int DEFAULT NULL,
  `estimate_number` varchar(6) DEFAULT NULL,
  `justification_id` int DEFAULT NULL,
  `Year` int NOT NULL,
  `notes_id` int DEFAULT NULL,
  `mini_header` int DEFAULT NULL,
  `grey` tinyint(1) NOT NULL DEFAULT (0),
  `name_id` int NOT NULL,
  `contractor_id` int DEFAULT NULL,
  `uom` int DEFAULT NULL,
  `value` float DEFAULT NULL,
  `cost` float DEFAULT NULL,
  `tbas` tinyint(1) NOT NULL DEFAULT (1),
  `wpi` tinyint(1) NOT NULL DEFAULT (1),
  `executive_documentation` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `chapter_id` (`chapter_id`),
  KEY `estimate_id` (`estimate_id`),
  KEY `justification_id` (`justification_id`),
  KEY `notes_id` (`notes_id`),
  KEY `name_id` (`name_id`),
  KEY `contractor_id` (`contractor_id`),
  KEY `executive_documentation` (`executive_documentation`),
  CONSTRAINT `chapter_id` FOREIGN KEY (`chapter_id`) REFERENCES `chapter` (`id`),
  CONSTRAINT `contractor_id` FOREIGN KEY (`contractor_id`) REFERENCES `contractor` (`id`),
  CONSTRAINT `estimate_id` FOREIGN KEY (`estimate_id`) REFERENCES `estimate_number` (`id`),
  CONSTRAINT `executive_documentation` FOREIGN KEY (`executive_documentation`) REFERENCES `executive_documentation` (`id`),
  CONSTRAINT `justification_id` FOREIGN KEY (`justification_id`) REFERENCES `justification` (`id`),
  CONSTRAINT `name_id` FOREIGN KEY (`name_id`) REFERENCES `name_of_works_and_materials` (`id`),
  CONSTRAINT `notes_id` FOREIGN KEY (`notes_id`) REFERENCES `notes` (`id`)
) ENGINE = `InnoDB` DEFAULT CHARSET = `utf8mb4` COLLATE = `utf8mb4_0900_ai_ci`;