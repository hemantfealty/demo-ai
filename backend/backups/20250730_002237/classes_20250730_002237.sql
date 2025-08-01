-- Table structure for classes
CREATE TABLE `classes` (
  `class_id` int(11) NOT NULL AUTO_INCREMENT,
  `class_name` varchar(50) NOT NULL,
  `section_id` int(11) NOT NULL,
  PRIMARY KEY (`class_id`),
  KEY `fk_classes_section` (`section_id`),
  CONSTRAINT `fk_classes_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for classes
INSERT INTO `classes` (`class_id`, `class_name`, `section_id`) VALUES (1, 'Grade 10', 1);
INSERT INTO `classes` (`class_id`, `class_name`, `section_id`) VALUES (2, 'Grade 10', 2);
INSERT INTO `classes` (`class_id`, `class_name`, `section_id`) VALUES (3, 'Grade 11', 1);
INSERT INTO `classes` (`class_id`, `class_name`, `section_id`) VALUES (4, 'Grade 11', 3);
