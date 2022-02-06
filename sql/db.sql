CREATE TABLE `crawl` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL,
  `date` datetime NOT NULL,
  `status_code` smallint unsigned NOT NULL,
  `headers` mediumtext NOT NULL,
  `content` mediumtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url_date_UNIQUE` (`url`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `history` (
  `id` bigint unsigned NOT NULL,
  `entity` varchar(16) NOT NULL,
  `property` varchar(16) NOT NULL,
  `value` varchar(128) NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_property` (`entity`,`property`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
