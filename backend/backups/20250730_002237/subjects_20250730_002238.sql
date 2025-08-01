-- Table structure for subjects
CREATE TABLE `subjects` (
  `subject_id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_name` varchar(100) NOT NULL,
  PRIMARY KEY (`subject_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for subjects
INSERT INTO `subjects` (`subject_id`, `subject_name`) VALUES (1, 'Mathematics');
INSERT INTO `subjects` (`subject_id`, `subject_name`) VALUES (2, 'English');
INSERT INTO `subjects` (`subject_id`, `subject_name`) VALUES (3, 'Science');
INSERT INTO `subjects` (`subject_id`, `subject_name`) VALUES (4, 'History');
