-- Table structure for parents
CREATE TABLE `parents` (
  `parent_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_roll_no` int(11) NOT NULL,
  `parent_name` varchar(200) NOT NULL,
  `relation` varchar(50) NOT NULL,
  PRIMARY KEY (`parent_id`),
  KEY `fk_parents_student` (`student_roll_no`),
  CONSTRAINT `fk_parents_student` FOREIGN KEY (`student_roll_no`) REFERENCES `students` (`roll_no`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for parents
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (1, 101, 'Mrs. Sunita Verma', 'Mother');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (2, 101, 'Mr. Rajesh Verma', 'Father');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (3, 102, 'Mrs. Nisha Shah', 'Mother');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (4, 102, 'Mr. Rakesh Shah', 'Father');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (5, 103, 'Mrs. Meena Patel', 'Mother');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (6, 103, 'Mr. Anil Patel', 'Father');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (7, 104, 'Mrs. Neetu Singh', 'Mother');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (8, 104, 'Mr. Vikram Singh', 'Father');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (9, 105, 'Mrs. Sushma Kumar', 'Mother');
INSERT INTO `parents` (`parent_id`, `student_roll_no`, `parent_name`, `relation`) VALUES (10, 105, 'Mr. Ajay Kumar', 'Father');
