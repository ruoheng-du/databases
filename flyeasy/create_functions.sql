-- define trigger to update the number of tickets left

DROP TRIGGER IF EXISTS delete_tickets;
CREATE TRIGGER delete_tickets AFTER INSERT ON purchases
FOR each ROW 
	UPDATE flight NATURAL JOIN ticket NATURAL JOIN purchases
    SET num_tickets_left = num_tickets_left - 1
    WHERE NEW.ticket_id = ticket.ticket_id;

show triggers;