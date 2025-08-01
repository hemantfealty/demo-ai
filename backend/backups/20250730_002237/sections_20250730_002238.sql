-- Table structure for sections
CREATE TABLE `sections` (
  `section_id` int(11) NOT NULL AUTO_INCREMENT,
  `section_name` char(1) NOT NULL,
  PRIMARY KEY (`section_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for sections
INSERT INTO `sections` (`section_id`, `section_name`) VALUES (1, 'A');
INSERT INTO `sections` (`section_id`, `section_name`) VALUES (2, 'B');
INSERT INTO `sections` (`section_id`, `section_name`) VALUES (3, 'C');
