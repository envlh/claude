CREATE TABLE `crawl` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL,
  `date` datetime NOT NULL,
  `status_code` smallint unsigned NOT NULL,
  `headers` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL,
  `content` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url_date_UNIQUE` (`url`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;

CREATE TABLE `history` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `entity` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL,
  `property` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL,
  `value` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_cs_0900_as_cs NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_property` (`entity`,`property`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_cs;
