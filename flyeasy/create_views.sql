CREATE VIEW staff_flight AS
SELECT airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status
FROM flight NATURAL JOIN airline_staff;

CREATE VIEW public_search_flight AS
SELECT flight_num, airline_name, airplane_id, D.airport_city AS departure_city, departure_airport, departure_time, A.airport_city AS arrival_city, arrival_airport, arrival_time, price, status
FROM airport AS D, flight, airport AS A
WHERE D.airport_name = departure_airport AND A.airport_name = arrival_airport;

CREATE VIEW agent_commission AS 
SELECT email, purchases.ticket_id, customer_email, purchase_date, price AS ticket_price, ticket.airline_name
FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight;

CREATE VIEW agent_view_flight AS
SELECT booking_agent.email, purchases.booking_agent_id, purchases.customer_email, purchases.purchase_date, purchases.ticket_id, flight.airline_name, flight.flight_num, D.airport_city AS departure_city, departure_airport, departure_time, A.airport_city AS arrival_city, arrival_airport, arrival_time, price, status, airplane_id
FROM booking_agent NATURAL RIGHT OUTER JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight, airport AS D, airport AS A
WHERE D.airport_name = departure_airport AND A.airport_name = arrival_airport;

CREATE VIEW customer_spending AS
SELECT *
FROM purchases NATURAL JOIN ticket NATURAL JOIN flight;