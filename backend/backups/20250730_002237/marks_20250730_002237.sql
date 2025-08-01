-- Table structure for marks
CREATE TABLE `marks` (
  `mark_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_roll_no` int(11) NOT NULL,
  `subject_id` int(11) NOT NULL,
  `marks_obtained` decimal(5,2) NOT NULL,
  PRIMARY KEY (`mark_id`),
  KEY `fk_marks_student` (`student_roll_no`),
  KEY `fk_marks_subject` (`subject_id`),
  CONSTRAINT `fk_marks_student` FOREIGN KEY (`student_roll_no`) REFERENCES `students` (`roll_no`),
  CONSTRAINT `fk_marks_subject` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`subject_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for marks
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (1, 101, 1, 88.50);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (2, 101, 2, 92.00);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (3, 102, 1, 76.25);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (4, 102, 3, 81.75);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (5, 103, 2, 69.00);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (6, 103, 4, 74.50);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (7, 104, 1, 95.00);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (8, 104, 3, 89.25);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (9, 105, 2, 83.00);
INSERT INTO `marks` (`mark_id`, `student_roll_no`, `subject_id`, `marks_obtained`) VALUES (10, 105, 4, 78.50);
