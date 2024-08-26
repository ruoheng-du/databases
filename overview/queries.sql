-------------------------
--------- Views ---------
-------------------------

-- create views for future use
CREATE VIEW staff_flight AS
SELECT airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status
FROM flight NATURAL JOIN airline_staff;

CREATE VIEW public_search_flight AS
SELECT flight_num, airline_name, airplane_id, D.airport_city AS departure_city, departure_airport, departure_time, A.airport_city AS arrival_city, arrival_airport, arrival_time, price, status
FROM airport AS D, flight, airport AS A
WHERE D.airport_name = departure_airport AND A.airport_name = arrival_airport;

CREATE VIEW agent_commission AS 
SELECT email, purchases.ticket_id, customer_email, purchase_date, price AS ticket_price
FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight;

CREATE VIEW agent_view_flight AS
SELECT booking_agent.email, purchases.booking_agent_id, purchases.customer_email, purchases.purchase_date, purchases.ticket_id, flight.airline_name, flight.flight_num, D.airport_city AS departure_city, departure_airport, departure_time, A.airport_city AS arrival_city, arrival_airport, arrival_time, price, status, airplane_id
FROM booking_agent NATURAL RIGHT OUTER JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight, airport AS D, airport AS A
WHERE D.airport_name = departure_airport AND A.airport_name = arrival_airport;

CREATE VIEW customer_spending AS
SELECT *
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight;

----------------------------
------- PUBLIC SIDE --------
----------------------------

-- select flight result
-- each input box can be empty, but if all boxes are empty, return all results
SELECT airline_name, flight_num, departure_city, departure_airport, departure_time, arrival_city, arrival_airport, arrival_time, price, airplane_id
FROM public_search_flight
WHERE departure_airport = if (%s = '', departure_airport, %s) AND 
    arrival_airport = if (%s = '', arrival_airport, %s) AND
    status = 'upcoming' AND
    departure_city = if (%s = '', departure_city, %s) AND
    arrival_city = if (%s = '', arrival_city, %s) AND
    date(departure_time) = if (%s = '', date(departure_time), %s) AND
    date(arrival_time) = if (%s = '', date(arrival_time), %s)
ORDER BY airline_name, flight_num;

-- select status result
-- each user input box can be empty. If all empty, then return all results​
SELECT *
FROM public_search_flight
WHERE flight_num = if (%s = '', flight_num, %s) AND date(departure_time) = if (%s = '', date(departure_time), %s) AND date(arrival_time) = if (%s = '', date(arrival_time), %s) AND airline_name = if (%s = '', airline_name, %s)
ORDER BY airline_name, flight_num;

----------------------------
------ CUSTOMER SIDE -------
----------------------------

-- check if there is such a customer given the email and password
SELECT *
FROM customer
WHERE email = %s AND password = md5(%s);

-- select the customer's upcoming flights
SELECT ticket_id, airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status
FROM flight NATURAL JOIN purchases NATURAL JOIN ticket, airport AS D, airport AS A
WHERE customer_email = %s AND status = 'upcoming' AND D.airport_name = departure_airport AND A.airport_name = arrival_airport;

-- check if this customer has registered before
SELECT * 
FROM customer 
WHERE email = %s;

-- insert new customer
INSERT INTO customer 
VALUES (%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- track the total spending
SELECT sum(price)
FROM customer_spending
WHERE customer_email = %s AND (purchase_date between DATE_ADD(NOW(), INTERVAL -%s DAY) and NOW());

-- track the month wise spending
SELECT year(purchase_date) AS year, month(purchase_date) AS month, sum(price) AS monthly_spending
FROM customer_spending 
WHERE customer_email = %s AND purchase_date >= %s 
GROUP BY year(purchase_date), month(purchase_date);

-- select search result for potential future purchase
SELECT airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, price, status, num_tickets_left
FROM airport AS D, flight, airport AS A
WHERE (%s = '' OR D.airport_city = %s) AND D.airport_name = departure_airport AND (%s = '' OR departure_airport = %s) AND (%s = '' OR A.airport_city = %s) AND A.airport_name = arrival_airport AND (%s = '' OR arrival_airport = %s) AND (%s = '' OR date(departure_time) = %s) AND (%s = '' OR date(arrival_time) = %s)
ORDER BY airline_name, flight_num;

-- check if there are still tickets left
SELECT *
FROM flight
WHERE airline_name = %s AND flight_num = %s AND num_tickets_left > 0;

-- calculate the new ticket id
SELECT ticket_id 
FROM ticket
ORDER BY ticket_id DESC
LIMIT 1;

-- insert new ticket
INSERT INTO ticket 
VALUES (%s, %s, %s);

-- insert new purchase record
INSERT INTO purchases 
VALUES (%s, %s, NULL, CURDATE());

----------------------------
-------- AGENT SIDE --------
----------------------------

-- check if there is such a booking agent given the email and password
SELECT * 
FROM booking_agent 
WHERE airline_name = %s AND email = %s AND password = md5(%s);

-- select the booking_agent_id of the booking agent
SELECT booking_agent_id 
FROM booking_agent 
WHERE airline_name = %s AND email = %s;

-- select the booking agent’s flights
SELECT *
FROM agent_view_flight
WHERE airline_name = %s AND email = %s;

-- check if this booking agent has registered before
SELECT * 
FROM booking_agent 
WHERE airline_name = %s AND email = %s;

-- insert new booking agent
INSERT INTO booking_agent 
VALUES(%s, md5(%s), %s, %s);

-- view commission
SELECT SUM(ticket_price * 0.1), AVG(ticket_price * 0.1), COUNT(ticket_price * 0.1)
FROM agent_commission
WHERE airline_name = %s AND email = %s AND (purchase_date between DATE_ADD(NOW(), INTERVAL -%s DAY) and NOW());

-- select the number of tickets bought for each customer in the past six months
SELECT customer_email, COUNT(ticket_id) 
FROM agent_commission 
WHERE airline_name = %s AND email = %s AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 183
GROUP BY customer_email
ORDER BY count(ticket_id)
DESC;

-- select the amount of commission received from each customer in the last year
SELECT customer_email, SUM(ticket_price) * 0.1
FROM agent_commission 
WHERE airline_name = %s AND email = %s and DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 
GROUP BY customer_email
ORDER BY sum(ticket_price)
DESC;

-- select search result for potential future purchase
SELECT airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status, price, airline_name, num_tickets_left
FROM airport AS D, flight, airport AS A
WHERE airline_name = %s AND D.airport_city = if (%s = '',D.airport_city, %s) AND D.airport_name = departure_airport AND departure_airport = if (%s = '', departure_airport, %s) AND A.airport_city = if (%s = '', A.airport_city, %s) AND A.airport_name = arrival_airport AND arrival_airport =  if (%s = '', arrival_airport, %s) AND date(departure_time) = if (%s = '', date(departure_time), %s) AND date(arrival_time) =  if (%s = '', date(arrival_time), %s)
ORDER BY airline_name, flight_num;

-- check if there are still tickets left
SELECT * 
FROM flight 
WHERE airline_name = %s AND flight_num = %s AND num_tickets_left > 0;

-- calculate the new ticket id
SELECT ticket_id 
FROM ticket
ORDER BY ticket_id DESC
LIMIT 1;

-- insert new ticket
INSERT INTO ticket 
VALUES (%s, %s, %s);

-- insert new purchase record
INSERT INTO purchases 
VALUES (%s, %s, %s, CURDATE());

----------------------------
-------- STAFF SIDE --------
----------------------------

-- check if there is such a staff agent given the username and password
SELECT * 
FROM airline_staff 
WHERE username = %s and password = md5(%s);

-- select the airline’s flights
SELECT username, airline_name, airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time
FROM flight NATURAL JOIN airline_staff 
WHERE username = %s AND status = 'upcoming' AND DATEFIFF(CURDATE(), DATE(departure_time)) < 30;

-- check if this airline staff has registered before
SELECT * 
FROM airline_staff 
WHERE username = %s;

-- check if this airline exists
SELECT airline_name 
FROM airline 
WHERE airline_name = %s;

-- insert new airline staff
INSERT INTO airline_staff 
VALUES(%s, md5(%s), %s, %s, %s, %s, %s, %s);

-- validate staff operator permission
SELECT isOperator
FROM airline_staff 
WHERE username = %s;

-- select search result (for change status)
SELECT airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status, price
FROM airport AS D, flight NATURAL JOIN airline_staff, airport AS A
WHERE D.airport_city = if (%s = '',D.airport_city, %s) AND D.airport_name = departure_airport AND departure_airport = if (%s = '', departure_airport, %s) AND A.airport_city = if (%s = '', A.airport_city, %s) AND A.airport_name = arrival_airport AND arrival_airport =  if (%s = '', arrival_airport, %s) AND date(departure_time) = if (%s = '', date(departure_time), %s) AND date(arrival_time) =  if (%s = '', date(arrival_time), %s) AND username = %s
ORDER BY airline_name, flight_num;

-- change flight status (operator only)
UPDATE flight 
SET status = %s 
WHERE flight_num = %s;

-- select airplane info
SELECT airplane_id, seats 
FROM airplane NATURAL JOIN airline_staff 
WHERE username = %s;

-- validate staff admin permission
SELECT isAdmin 
FROM airline_staff 
WHERE username = %s;

-- select the airline that the staff works for
SELECT airline_name 
FROM airline_staff
WHERE username = %s;

-- check if departure and arrival airport exist
SELECT airport_name 
FROM airport 
WHERE airport_name = %s;

-- check if airplane exists
SELECT airplane_id 
FROM airplane 
WHERE airline_name = %s AND airplane_id = %s;

-- check if enough number of seats
SELECT seats 
FROM airplane NATURAL JOIN airline_staff 
WHERE username = %s AND airplane_id = %s;

-- check if the flight has already existed
SELECT airline_name, flight_num 
FROM flight 
WHERE airline_name = %s AND flight_num = %s;

-- insert new flight
INSERT INTO flight 
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- insert new airplane
INSERT INTO airplane 
VALUES(%s, %s, %s);

-- insert new airport
INSERT INTO airport
VALUES(%s, %s);

-- select booking agent info for adding
SELECT password, booking_agent_id
FROM booking_agent
WHERE email = %s;

-- add booking agent (staff side)
INSERT INTO booking_agent 
VALUES(%s, %s, %s, %s);

-- select agents based on commission
SELECT email, booking_agent_id, SUM(price) * 0.1 AS commission
FROM booking_agent NATURAL JOIN purchases NATURAL JOIN flight NATURAL JOIN ticket AS T, airline_staff
WHERE username = %s AND airline_staff.airline_name = T.airline_name AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365
GROUP BY email, booking_agent_id 
ORDER BY commission DESC 
LIMIT 5;

-- select agents based on number of tickets (month)
SELECT booking_agent.email, booking_agent_id, COUNT(ticket_id) AS ticket 
FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket AS T, airline_staff 
WHERE username = %s AND airline_staff.airline_name = T.airline_name AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 30
GROUP BY email, booking_agent_id 
ORDER BY ticket DESC 
LIMIT 5;

-- select agents based on number of tickets (year)
SELECT booking_agent.email, booking_agent_id, COUNT(ticket_id) AS ticket 
FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket AS T, airline_staff 
WHERE username = %s AND airline_staff.airline_name = T.airline_name AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365
GROUP BY email, booking_agent_id 
ORDER BY ticket DESC 
LIMIT 5;

-- select top customers
SELECT email, name, COUNT(ticket_id) AS ticket
FROM customer, purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff 
WHERE email = customer_email AND username = %s and DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 
GROUP BY email, name 
ORDER BY ticket DESC 
LIMIT 1;

-- select the flights bought by the customer
SELECT DISTINCT airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status
FROM customer, purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff
WHERE email = customer_email AND email = %s AND username = %s;

-- check if the customer exists
SELECT email 
FROM customer 
WHERE email = %s;

-- update permission
UPDATE airline_staff
SET isAdmin = %s, isOperator = %s 
WHERE username = %s;

-- select top destination (month)
SELECT airport_city, COUNT(ticket_id) AS ticket
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport
WHERE airport_name = arrival_airport AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 90
GROUP BY airport_city 
ORDER BY ticket DESC 
LIMIT 3;

-- select top destination (year)
SELECT airport_city, COUNT(ticket_id) AS ticket
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport
WHERE airport_name = arrival_airport AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365
GROUP BY airport_city 
ORDER BY ticket DESC 
LIMIT 3;

-- select monthly direct revenue
SELECT SUM(price)
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff 
WHERE username = %s AND booking_agent_id is NULL AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 30 
GROUP BY airline_name;

-- select monthly indirect revenue
SELECT SUM(price) 
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff 
WHERE username = %s AND booking_agent_id is NOT NULL AND datediff(CURDATE(), DATE(purchase_date)) < 30 
GROUP BY airline_name;

-- select yearly direct revenue
SELECT SUM(price)
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff
WHERE username = %s AND booking_agent_id is NULL AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365
GROUP BY airline_name;

-- select yearly indirect revenue
SELECT SUM(price)
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff
WHERE username = %s AND booking_agent_id is NOT NULL AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365
GROUP BY airline_name;

-- select total amount of tickets sold (month)
SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, COUNT(ticket_id) 
FROM purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket 
WHERE username = %s AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 30 
GROUP BY year, month 
ORDER BY year, month;

-- select total amount of tickets sold (year)
SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, COUNT(ticket_id) 
FROM purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket 
WHERE username = %s AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365
GROUP BY year, month 
ORDER BY year, month;

-- select total amount of tickets sold (specified time range)
SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, COUNT(ticket_id)
FROM purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket 
WHERE purchase_date > %s AND purchase_date < %s AND username = %s 
GROUP BY year, month 
ORDER BY year, month;



