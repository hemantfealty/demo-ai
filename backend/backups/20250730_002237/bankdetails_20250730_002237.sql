-- Table structure for bankdetails
CREATE TABLE `bankdetails` (
  `bank_account_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_roll_no` int(11) NOT NULL,
  `bank_name` varchar(100) NOT NULL,
  `account_number` varchar(30) NOT NULL,
  `ifsc_code` varchar(20) NOT NULL,
  PRIMARY KEY (`bank_account_id`),
  KEY `fk_bankdetails_student` (`student_roll_no`),
  CONSTRAINT `fk_bankdetails_student` FOREIGN KEY (`student_roll_no`) REFERENCES `students` (`roll_no`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for bankdetails
INSERT INTO `bankdetails` (`bank_account_id`, `student_roll_no`, `bank_name`, `account_number`, `ifsc_code`) VALUES (1, 101, 'State Bank of India', 'SBIN0001234', 'SBIN0001');
INSERT INTO `bankdetails` (`bank_account_id`, `student_roll_no`, `bank_name`, `account_number`, `ifsc_code`) VALUES (2, 102, 'HDFC Bank', 'HDFC0005678', 'HDFC0005');
INSERT INTO `bankdetails` (`bank_account_id`, `student_roll_no`, `bank_name`, `account_number`, `ifsc_code`) VALUES (3, 103, 'ICICI Bank', 'ICIC0009012', 'ICIC0009');
INSERT INTO `bankdetails` (`bank_account_id`, `student_roll_no`, `bank_name`, `account_number`, `ifsc_code`) VALUES (4, 104, 'Axis Bank', 'UTIB0003456', 'UTIB0003');
INSERT INTO `bankdetails` (`bank_account_id`, `student_roll_no`, `bank_name`, `account_number`, `ifsc_code`) VALUES (5, 105, 'Punjab National Bank', 'PUNB0007890', 'PUNB0007');
