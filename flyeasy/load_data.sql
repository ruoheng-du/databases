--
-- Setting
--

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('China Eastern'),
('Air China');


--
-- Dumping data for table `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`, `isAdmin`, `isOperator`) VALUES
('lilei', 'e19d5cd5af0378da05f63f891c7467af', 'Lei', 'Li', '2000-07-10', 'China Eastern', 1, 1);
-- password: abcd1234


--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
('China Eastern', 747, 365),
('China Eastern', 320, 158),
('Air China', 380, 366);


--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
('JFK', 'New York City'),
('PVG', 'Shanghai'),
('LHR', 'London'),
('HKG', 'Hong Kong'),
('SFO', 'San Francisco'),
('PEK', 'Beijing');


--
-- Dumping data for table `booking_agent`
--

INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`, `airline_name`) VALUES
('meimeihan@booking.com', 'e19d5cd5af0378da05f63f891c7467af', 20240123, 'China Eastern'),
('meimeihan@booking.com', 'e19d5cd5af0378da05f63f891c7467af', 20240123, 'Air China');
-- password: abcd1234

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('rd2910@nyu.edu', 'Ruoheng Du', 'a39e2f86067954d4d63a5d4fc9107347', '567', 'Yangsi West Road', 'Shanghai', 'Shanghai', 18635772, '18635772', '2024-05-19', 'China', '2002-06-15');


--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`airline_name`, `flight_num`, `departure_airport`, `departure_time`, `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`, `num_tickets_left`) VALUES
('China Eastern', 589, 'PVG', '2024-07-11 12:45:00', 'SFO', '2024-07-11 09:05:00', 9210, 'Upcoming', 747, 100),
('China Eastern', 587, 'PVG', '2024-08-18 11:30:00', 'JFK', '2024-08-18 14:25:00', 20870, 'Upcoming', 747, 100),
('China Eastern', 721, 'PVG', '2024-06-12 08:15:00', 'HKG', '2024-06-12 11:00:00', 913, 'Upcoming', 320, 150),
('China Eastern', 588, 'JFK', '2024-05-06 16:25:00', 'PVG', '2024-05-07 19:25:00', 13013, 'Delayed', 747, 50),
('Air China', 981, 'PEK', '2024-06-21 20:55:00', 'JFK', '2024-06-21 23:55:00', 9516, 'Upcoming', 380, 300);


--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
(1, 'China Eastern', 589),
(2, 'China Eastern', 588);


--
-- Dumping data for table `purchases`
--

INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
(1, 'rd2910@nyu.edu', NULL, '2024-05-01'),
(2, 'rd2910@nyu.edu', 20240123, '2024-05-01');