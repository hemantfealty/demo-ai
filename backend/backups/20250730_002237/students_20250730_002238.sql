-- Table structure for students
CREATE TABLE `students` (
  `roll_no` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `age` tinyint(3) unsigned NOT NULL,
  `class_id` int(11) NOT NULL,
  `section_id` int(11) NOT NULL,
  `scholarship_id` int(11) DEFAULT NULL,
  `bank_account_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`roll_no`),
  KEY `fk_students_class` (`class_id`),
  KEY `fk_students_section` (`section_id`),
  KEY `fk_students_scholarship` (`scholarship_id`),
  KEY `fk_students_bank` (`bank_account_id`),
  CONSTRAINT `fk_students_bank` FOREIGN KEY (`bank_account_id`) REFERENCES `bankdetails` (`bank_account_id`),
  CONSTRAINT `fk_students_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`),
  CONSTRAINT `fk_students_scholarship` FOREIGN KEY (`scholarship_id`) REFERENCES `scholarships` (`scholarship_id`),
  CONSTRAINT `fk_students_section` FOREIGN KEY (`section_id`) REFERENCES `sections` (`section_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for students
INSERT INTO `students` (`roll_no`, `first_name`, `last_name`, `age`, `class_id`, `section_id`, `scholarship_id`, `bank_account_id`) VALUES (101, 'Riya', 'Verma', 15, 1, 1, 1, 1);
INSERT INTO `students` (`roll_no`, `first_name`, `last_name`, `age`, `class_id`, `section_id`, `scholarship_id`, `bank_account_id`) VALUES (102, 'Amit', 'Shah', 15, 1, 2, 2, 2);
INSERT INTO `students` (`roll_no`, `first_name`, `last_name`, `age`, `class_id`, `section_id`, `scholarship_id`, `bank_account_id`) VALUES (103, 'Sneha', 'Patel', 16, 3, 1, NULL, 3);
INSERT INTO `students` (`roll_no`, `first_name`, `last_name`, `age`, `class_id`, `section_id`, `scholarship_id`, `bank_account_id`) VALUES (104, 'Karan', 'Singh', 16, 3, 3, 3, 4);
INSERT INTO `students` (`roll_no`, `first_name`, `last_name`, `age`, `class_id`, `section_id`, `scholarship_id`, `bank_account_id`) VALUES (105, 'Pooja', 'Kumar', 15, 2, 2, 1, 5);
