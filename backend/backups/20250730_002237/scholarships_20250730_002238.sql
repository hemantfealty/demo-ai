-- Table structure for scholarships
CREATE TABLE `scholarships` (
  `scholarship_id` int(11) NOT NULL AUTO_INCREMENT,
  `scholarship_name` varchar(100) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`scholarship_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Data for scholarships
INSERT INTO `scholarships` (`scholarship_id`, `scholarship_name`, `amount`) VALUES (1, 'Merit Scholarship', 5000.00);
INSERT INTO `scholarships` (`scholarship_id`, `scholarship_name`, `amount`) VALUES (2, 'Sports Scholarship', 3000.00);
INSERT INTO `scholarships` (`scholarship_id`, `scholarship_name`, `amount`) VALUES (3, 'Need‑Based Scholarship', 7000.00);
