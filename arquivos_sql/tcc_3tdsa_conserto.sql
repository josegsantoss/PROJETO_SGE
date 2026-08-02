CREATE DATABASE  IF NOT EXISTS `tcc_3tdsa` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `tcc_3tdsa`;
-- MySQL dump 10.13  Distrib 8.0.46, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: tcc_3tdsa
-- ------------------------------------------------------
-- Server version	9.7.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '9e45e8cc-8c32-11f1-bd08-2e2d5524b624:1-266';

--
-- Table structure for table `conserto`
--

DROP TABLE IF EXISTS `conserto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conserto` (
  `id_conserto` int NOT NULL AUTO_INCREMENT,
  `nome_cliente` varchar(150) NOT NULL,
  `equipamento` varchar(150) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `defeito` varchar(255) NOT NULL,
  `prioridade` varchar(20) NOT NULL,
  `status_servico` varchar(50) NOT NULL,
  `valor_estimado` decimal(10,2) DEFAULT '0.00',
  `observacoes` text,
  `data_entrada` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_conserto`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conserto`
--

LOCK TABLES `conserto` WRITE;
/*!40000 ALTER TABLE `conserto` DISABLE KEYS */;
INSERT INTO `conserto` VALUES (1,'Pedro','Iphone 18 ','celular','Queimou a tela','media','recebido',1000.00,'Quero tambem que troque a capa dele.','2026-08-01 20:20:01'),(2,'Pedro','Iphone 18 ','celular','Queimou a tela','media','recebido',1000.00,'Quero tambem que troque a capa dele.','2026-08-01 20:20:08'),(3,'Pedro','Iphone 18 ','celular','Queimou a tela','media','recebido',1000.00,'Quero tambem que troque a capa dele.','2026-08-01 20:20:13'),(4,'Pedro','Iphone 18 ','celular','Queimou a tela','media','recebido',1000.00,'Quero tambem que troque a capa dele.','2026-08-01 20:28:25'),(5,'Pedro','Iphone 18 ','celular','Queimou a tela','media','recebido',1000.00,'Quero tambem que troque a capa dele.','2026-08-01 20:29:12'),(6,'Pedro','Iphone 18 ','celular','Queimou a tela','media','recebido',1000.00,'Quero tambem que troque a capa dele.','2026-08-01 20:30:21'),(7,'Pedro','Iphone 18 ','celular','Queimou a tela','media','recebido',1000.00,'Quero tambem que troque a capa dele.','2026-08-01 20:37:12'),(8,'Arthur','Positivo Master','notebook','Derramei uranio enriquecido e cesio-137 no meu computador','baixa','recebido',1000000.00,'','2026-08-01 20:38:21'),(9,'Messi','Bola de futebol','outros','Furou a bola','alta','conserto',1000.00,'Hola tengo 8 bolas de oro, e duas de carne quieres ver','2026-08-01 21:26:29');
/*!40000 ALTER TABLE `conserto` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-02  0:22:28
