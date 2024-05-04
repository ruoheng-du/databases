from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import datetime
import json
import decimal

#####################################################################
#                             COMMON                                #
#                   all operations from all sides                   #
#####################################################################

# initialize the app from Flask
app = Flask(__name__)

# configure MySQL
conn = mysql.connector.connect(host='localhost',
					   user='root',
					   password='',
					   database='flyeasy')

#####################################################################
#                               HELPER                              #
#              malicious input such as (2 or '1' = '1')			    #
#####################################################################

def check_apostrophe(x):
	assert type(x) == str
	if "'" not in x:
		return x
	db_x = ''
	for i in x:
		if i == "'":
			db_x += "''"
		else:
			db_x += i
	return db_x

#####################################################################
#                               PUBLIC                              #
#                all operations from the public side                #
#####################################################################

@app.route('/')
def publicHome():
	return render_template('publicHome.html')

@app.route('/publicSearchFlight', methods=['GET', 'POST'])
def publicSearchFlight():
	departure_city = check_apostrophe(request.form['departure_city'])
	departure_airport = check_apostrophe(request.form['departure_airport'])
	arrival_city = check_apostrophe(request.form['arrival_city'])
	arrival_airport = check_apostrophe(request.form['arrival_airport'])
	departure_date = request.form['departure_date']
	arrival_date = request.form['arrival_date']

	cursor = conn.cursor()
	query = "SELECT airline_name, flight_num, departure_city, departure_airport, departure_time, arrival_city, arrival_airport, arrival_time, price, airplane_id \
        	FROM public_search_flight \
        	WHERE departure_airport = if (%s = '', departure_airport, %s) AND \
                arrival_airport = if (%s = '', arrival_airport, %s) AND \
                status = 'upcoming' AND \
                departure_city = if (%s = '', departure_city, %s) AND \
                arrival_city = if (%s = '', arrival_city, %s) AND \
                date(departure_time) = if (%s = '', date(departure_time), %s) AND \
                date(arrival_time) = if (%s = '', date(arrival_time), %s) \
        	ORDER BY airline_name, flight_num"
	cursor.execute(query, (departure_airport, departure_airport, arrival_airport, arrival_airport, departure_city, departure_city, arrival_city, arrival_city, departure_date, departure_date, arrival_date, arrival_date))
	data = cursor.fetchall() 
	cursor.close()
	
	if (data): # has data
		return render_template('publicHome.html', upcoming_flights=data)
	else: # does not have data
		error = 'Sorry, we can\'t find any flight!'
		return render_template('publicHome.html', error1=error)

@app.route('/publicSearchStatus', methods=['GET', 'POST'])
def publicSearchStatus():
	airline_name = check_apostrophe(request.form['airline_name'])
	flight_num = request.form['flight_num']
	arrival_date = request.form['arrival_date']
	departure_date = request.form['departure_date']

	cursor = conn.cursor()
	query = "SELECT * \
        	FROM public_search_flight \
        	WHERE flight_num = if (%s = '', flight_num, %s) AND \
                date(departure_time) = if (%s = '', date(departure_time), %s) AND \
                date(arrival_time) = if (%s = '', date(arrival_time), %s) AND \
                airline_name = if (%s = '', airline_name, %s) \
        	ORDER BY airline_name, flight_num"
	cursor.execute(query, (flight_num, flight_num, arrival_date, arrival_date, departure_date, departure_date, airline_name, airline_name))
	data = cursor.fetchall() 
	cursor.close()
	
	if (data): # has data
		# upcoming_flights = session['upcoming_flights']
		return render_template('publicHome.html', statuses=data)
	else: # does not have data
		error = 'Sorry, we can\'t find this flight!'
		return render_template('publicHome.html', error2=error)

#####################################################################
#                              CUSTOMER                             #
#               all operations from the customer side               #
#####################################################################

# define route for login
@app.route('/cuslogin')
def cuslogin():
	return render_template('cuslogin.html')

# define route for register
@app.route('/cusregister')
def cusregister():
	return render_template('cusregister.html')

# authenticate customer login
@app.route('/cusloginAuth', methods=['GET', 'POST'])
def cusloginAuth():
	if "email" in request.form and 'password' in request.form:
		email = request.form['email']
		db_email = check_apostrophe(email)
		password = request.form['password']

		cursor = conn.cursor()
		query = "SELECT * FROM customer WHERE email = %s AND password = md5(%s)"
		cursor.execute(query, (db_email, password))
		data = cursor.fetchone()
		cursor.close()

		if(data):
			session['email'] = email
			cursor = conn.cursor()
			query = "SELECT ticket_id, airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status \
					FROM flight NATURAL JOIN purchases NATURAL JOIN ticket, airport AS D, airport AS A \
					WHERE customer_email = %s AND status = 'upcoming' AND \
						D.airport_name = departure_airport AND A.airport_name = arrival_airport"
			cursor.execute(query, (db_email,))
			data1 = cursor.fetchall() 
			cursor.close()
			return render_template('cushome.html', email=email, emailName=email.split('@')[0], view_my_flights=data1)
		else:
			# return an error message to the html page
			error = 'Error: Invalid email or password!'
			return render_template('cuslogin.html', error=error)
	else:
		session.clear()
		return render_template('404.html')

# authenticate customer register
@app.route('/cusregisterAuth', methods=['GET', 'POST'])
def cusregisterAuth():
	if "email" in request.form and \
		'name' in request.form and \
		'password' in request.form and \
		'building_number' in request.form and \
		'street' in request.form and \
		'city' in request.form and \
		'state' in request.form and \
		'phone_number' in request.form and \
		'passport_number' in request.form and \
		'passport_expiration' in request.form and \
		'passport_country' in request.form and \
		'date_of_birth' in request.form:
		email = request.form['email']
		db_email = check_apostrophe(email)
		name = request.form['name']
		db_name = check_apostrophe(name)
		password = request.form['password']
		building_number = check_apostrophe(request.form['building_number'])
		street = check_apostrophe(request.form['street'])
		city = check_apostrophe(request.form['city'])
		state = check_apostrophe(request.form['state'])
		phone_number = request.form['phone_number']
		passport_number = check_apostrophe(request.form['passport_number'])
		passport_expiration = request.form['passport_expiration']
		passport_country = check_apostrophe(request.form['passport_country'])
		date_of_birth = request.form['date_of_birth']

		cursor = conn.cursor()
		query = "SELECT * FROM customer WHERE email = %s"
		cursor.execute(query, (db_email,))
		data = cursor.fetchone()

		if(data):
			cursor.close()
			error = "This user already exists!"
			return render_template('cusregister.html', error = error)
		else:
			new = "INSERT INTO customer VALUES (%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			cursor.execute(new, (db_email, db_name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
			conn.commit()
			query = "SELECT ticket_id, airline_name, airplane_id, flight_num, D.airport_city, \
							departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status \
					FROM flight NATURAL JOIN purchases NATURAL JOIN ticket, airport AS D, airport AS A\
					WHERE customer_email = %s AND status = 'upcoming' AND \
							D.airport_name = departure_airport AND A.airport_name = arrival_airport"
			cursor.execute(query, (db_email,))
			data1 = cursor.fetchall() 
			cursor.close()
			flash("Welcome to FlyEasy!")
			session['email'] = email
			return render_template('cushome.html', email=email, emailName=email.split('@')[0], view_my_flights=data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/cushome')
def cushome():
	if session.get('email'):
		email = session['email']
		db_email = check_apostrophe(email)

		cursor = conn.cursor()
		query = "SELECT ticket_id, airline_name, airplane_id, flight_num, D.airport_city, \
						departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status \
				FROM flight NATURAL JOIN purchases NATURAL JOIN ticket, airport AS D, airport AS A\
				WHERE customer_email = %s AND status = 'upcoming' AND \
						D.airport_name = departure_airport AND A.airport_name = arrival_airport"
		cursor.execute(query, (db_email,))
		data1 = cursor.fetchall() 
		cursor.close()
		return render_template('cushome.html', email=email, emailName=email.split('@')[0], view_my_flights=data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/cusSearchPurchase')
def cusSearchPurchase():
	if session.get('email'):
		email = session['email'] 
		return render_template('cusSearchPurchase.html', email=email, emailName=email.split('@')[0])
	else:
		session.clear()
		return render_template('404.html')

@app.route('/cusSpending', methods=['POST', 'GET'])
def cusSpending():
	if session.get('email'):
		email = session['email']
		db_email = check_apostrophe(email)

		# show total spending in the past period of time
		duration = request.form.get("duration")
		if duration is None:
			duration = "365"
		cursor = conn.cursor()
		query_total = "SELECT sum(price)\
					FROM customer_spending \
					WHERE customer_email = %s AND (purchase_date between DATE_ADD(NOW(), INTERVAL -%s DAY) and NOW())"
		cursor.execute(query_total, (db_email, duration))
		total_spending_data = cursor.fetchone()
		cursor.close()

		# show month-wise spending in the past 6 months
		period = request.form.get("period")
		if period is None:
			period = '6'
		today = datetime.date.today()
		past_day = today.day
		past_month = (today.month - int(period)) % 12
		if past_month == 0:
			past_month = 12
		past_year = today.year + ((today.month - int(period) - 1) // 12)
		past_date = datetime.date(past_year, past_month, past_day) # the day 6 months ago

		cursor = conn.cursor()
		query_month = "SELECT year(purchase_date) AS year, month(purchase_date) AS month, sum(price) AS monthly_spending \
					FROM customer_spending \
					WHERE customer_email = %s AND purchase_date >= %s \
					GROUP BY year(purchase_date), month(purchase_date)"
		cursor.execute(query_month, (db_email, past_date))
		monthly_spending_data = cursor.fetchall()
		cursor.close()

		months = []
		monthly_spendings = []
		for i in range(int(period)):
			month = (past_date.month + i + 1) % 12
			if month == 0:
				month = 12
			year = past_date.year + ((past_date.month + i) // 12)
			flag = False
			for one_month in monthly_spending_data:
				if one_month[0] == year and one_month[1] == month:
					flag = True
					break
			if flag:
				monthly_spendings.append(int(one_month[2]))
			else:
				monthly_spendings.append(0)
			months.append(str(year)+'-'+str(month))

		return render_template('cusSpending.html', email=email, emailName=email.split('@')[0], total_spending_data=total_spending_data[0], duration=duration, period=period, months=months, monthly_spendings=monthly_spendings)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/cusSearchFlight', methods=['GET', 'POST'])
def cusSearchFlight():
	if session.get('email'):
		email = session['email']
		db_email = check_apostrophe(email)
		departure_city = check_apostrophe(request.form['departure_city'])
		departure_airport = check_apostrophe(request.form['departure_airport'])
		arrival_city = check_apostrophe(request.form['arrival_city'])
		arrival_airport = check_apostrophe(request.form['arrival_airport'])
		departure_date = request.form['departure_date']
		arrival_date = request.form['arrival_date']

		cursor = conn.cursor()
		query = "SELECT airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, price, status, num_tickets_left \
         		FROM airport AS D, flight, airport AS A \
         		WHERE (%s = '' OR D.airport_city = %s) AND \
               		D.airport_name = departure_airport AND \
               		(%s = '' OR departure_airport = %s) AND \
               		(%s = '' OR A.airport_city = %s) AND \
               		A.airport_name = arrival_airport AND \
               		(%s = '' OR arrival_airport = %s) AND \
               		(%s = '' OR date(departure_time) = %s) AND \
               		(%s = '' OR date(arrival_time) = %s) \
         		ORDER BY airline_name, flight_num"
		cursor.execute(query, (departure_city, departure_city, departure_airport, departure_airport, arrival_city, arrival_city, arrival_airport, arrival_airport, departure_date, departure_date, arrival_date, arrival_date))
		data = cursor.fetchall()
		cursor.close()
		
		if (data):
			return render_template('cusSearchPurchase.html', email = email, emailName=email.split('@')[0], upcoming_flights=data)
		else:
			error = 'Sorry, we can\'t find any flight!'
			return render_template('cusSearchPurchase.html', email = email, emailName=email.split('@')[0], error1=error)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/cusBuyTickets', methods=['GET', 'POST'])
def cusBuyTickets():
	if session.get('email'):
		email = session['email']
		db_email = check_apostrophe(email)
		airline_name = check_apostrophe(request.form['airline_name'])
		flight_num = request.form['flight_num']

		cursor = conn.cursor()
		query = "SELECT * \
				FROM flight \
				WHERE airline_name = %s AND flight_num = %s AND num_tickets_left > 0"
		cursor.execute(query, (airline_name, flight_num))
		data = cursor.fetchall()
		cursor.close()

		if(data): # has ticket
			cursor = conn.cursor()
			# calculate the new ticket id
			cursor = conn.cursor()
			query_id = "SELECT ticket_id \
						FROM ticket \
						ORDER BY ticket_id DESC \
						LIMIT 1"
			cursor.execute(query_id)
			ticket_id_data = cursor.fetchone() #
			new_ticket_id = int(ticket_id_data[0]) + 1

			# first insert into ticket
			ins1 = "INSERT INTO ticket VALUES (%s, %s, %s)"
			cursor.execute(ins1, (new_ticket_id, airline_name, flight_num))

			# then insert into purchases
			ins2 = "INSERT INTO purchases VALUES (%s, %s, NULL, CURDATE())"
			cursor.execute(ins2, (new_ticket_id, db_email))
			conn.commit()
			cursor.close()
			message1 = 'Ticket bought successfully!'
			return render_template('cusSearchPurchase.html', email = email, message1 = message1)
		else:
			error = 'There\'re no ticket left...'
			return render_template('cusSearchPurchase.html', error2=error, email = email, emailName=email.split('@')[0])
	else:
		session.clear()
		return render_template('404.html')

#####################################################################
#                         BOOKING AGENT                             #
#            all operations from the booking_agent side             #
#####################################################################

@app.route('/agentlogin')
def agentlogin():
	return render_template('agentlogin.html')

@app.route('/agentregister')
def agentregister():
	return render_template('agentregister.html')

@app.route('/agentloginAuth', methods=['GET', 'POST'])
def agentloginAuth():
	if "email" in request.form and 'password' in request.form:
		email = request.form['email']
		db_email = check_apostrophe(email)
		password = request.form['password']
		airline_name = request.form['airline_name']
		airline = check_apostrophe(airline_name)

		cursor = conn.cursor()
		query = "SELECT * FROM booking_agent WHERE airline_name = %s AND email = %s AND password = md5(%s)"
		cursor.execute(query, (airline, db_email, password))
		data = cursor.fetchone()
		cursor.close()

		if(data):
			cursor = conn.cursor()
			query1 = "SELECT booking_agent_id FROM booking_agent WHERE airline_name = %s AND email = %s"
			cursor.execute(query1, (airline, db_email))
			data1 = cursor.fetchone()
			query2 = "SELECT * FROM agent_view_flight WHERE airline_name = %s AND email = %s"
			cursor.execute(query2, (airline, db_email))
			data2 = cursor.fetchall()
			cursor.close()
			session['BA_email'] = email
			session['BA_airline'] = airline
			session['BA_id'] = data1
			return render_template('agenthome.html', email=email, emailName=email.split('@')[0], view_my_flights=data2, booking_agent_id=data1)
		else:
			error = 'Error: Invalid email or password!'
			return render_template('agentlogin.html', error=error)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/agentregisterAuth', methods=['GET', 'POST'])
def agentregisterAuth():
	if "email" in request.form and 'password' in request.form and 'booking_agent_id' in request.form:
		email = request.form['email']
		db_email = check_apostrophe(email)
		password = request.form['password']
		booking_agent_id = request.form['booking_agent_id']
		airline_name = request.form['airline_name']
		airline = check_apostrophe(airline_name)

		cursor = conn.cursor()
		query = "SELECT * FROM booking_agent WHERE airline_name = %s AND email = %s"
		cursor.execute(query, (airline, db_email))
		data = cursor.fetchone()

		if(data):
			cursor.close()
			error = "This user already exists!"
			return render_template('agentregister.html', error = error)
		else:
			new = "INSERT INTO booking_agent VALUES(%s, md5(%s), %s, %s)"
			cursor.execute(new, (db_email, password, booking_agent_id, airline))
			conn.commit()
			query1 = "SELECT booking_agent_id FROM booking_agent WHERE airline_name = %s AND email = %s"
			cursor.execute(query1, (airline, db_email))
			data1 = cursor.fetchone()
			# get agent_view_flights info from db
			query = "SELECT * FROM agent_view_flight WHERE airline_name = %s AND email = %s"
			cursor.execute(query, (airline, db_email))
			data2 = cursor.fetchall()
			cursor.close()
			session['BA_email'] = email
			session['BA_airline'] = airline
			flash("Welcome to FlyEasy!")
			return render_template('agenthome.html', email=email, emailName=email.split('@')[0], view_my_flights=data2, booking_agent_id=data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/agentHome')
def agentHome():
	if session.get('BA_email'):
		email = session['BA_email']
		db_email = check_apostrophe(email)
		airline_name = session['BA_airline']
		airline = check_apostrophe(airline_name)
			
		cursor = conn.cursor()
		query1 = "SELECT booking_agent_id FROM booking_agent WHERE airline_name = %s AND email = %s"
		cursor.execute(query1, (airline, db_email))
		data1 = cursor.fetchone()
		query2 = "SELECT * FROM agent_view_flight WHERE airline_name = %s AND email = %s"
		cursor.execute(query2, (airline, db_email))
		data2 = cursor.fetchall()
		cursor.close()
		return render_template('agenthome.html', email=email, emailName=email.split('@')[0], view_my_flights=data2, booking_agent_id=data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/agentSearchPurchase')
def agentSearchPurchase():
	if session.get('BA_email'):
		email = session['BA_email'] 
		return render_template('agentSearchPurchase.html', email=email, emailName=email.split('@')[0], )
	else:
		session.clear()
		return render_template('404.html')

@app.route('/agentCommission', methods=['POST', 'GET'])
def agentCommission():
	if session.get('BA_email'):
		email = session['BA_email']
		db_email = check_apostrophe(email)
		airline_name = session['BA_airline']
		airline = check_apostrophe(airline_name)

		cursor = conn.cursor()
		duration = request.form.get("duration")
		if duration is None:
			duration = "30"
		query = 'SELECT SUM(ticket_price * 0.1), AVG(ticket_price * 0.1), COUNT(ticket_price * 0.1) \
			 	FROM agent_commission \
				WHERE airline_name = %s AND email = %s AND (purchase_date between DATE_ADD(NOW(), INTERVAL -%s DAY) and NOW())'
		cursor.execute(query, (airline, db_email, duration))
		commission_data = cursor.fetchone()
		total_com, avg_com, count_ticket = commission_data
		cursor.close()
		return render_template('agentCommission.html', email=email, emailName=email.split('@')[0], total_com=total_com, avg_com=avg_com, count_ticket=count_ticket, duration=duration)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/agentTopCustomers')
def agentTopCustomers():
	if session.get('BA_email'):
		email = session['BA_email']
		db_email = check_apostrophe(email)
		airline_name = session['BA_airline']
		airline = check_apostrophe(airline_name)

		cursor = conn.cursor()
		query = "SELECT customer_email, COUNT(ticket_id) \
				FROM agent_commission \
				WHERE airline_name = %s AND email = %s AND \
					DATEDIFF(CURDATE(), DATE(purchase_date)) < 183 \
				GROUP BY customer_email \
				ORDER BY count(ticket_id) DESC"
		cursor.execute(query, (airline, db_email))
		ticket_data = cursor.fetchall()
		cursor.close()

		l = len(ticket_data)
		if l >= 5:
			ppl1 = [ticket_data[i][0] for i in range(5)]
			tickets = [ticket_data[i][1] for i in range(5)]
		else:
			ppl1 = [ticket_data[i][0] for i in range(l)]
			tickets = [ticket_data[i][1] for i in range(l)]
			for i in range(5 - l):
				ppl1.append(' ')
				tickets.append(0)
		
		cursor = conn.cursor()
		query2 = "SELECT customer_email, SUM(ticket_price) * 0.1 \
				FROM agent_commission \
				WHERE airline_name = %s AND email = %s and \
				DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
				GROUP BY customer_email \
				ORDER BY sum(ticket_price) DESC"
		cursor.execute(query2, (airline, db_email))
		commission_data = cursor.fetchall()
		cursor.close()

		l2 = len(commission_data)
		if l2 >= 5:
			ppl2 = [commission_data[i][0] for i in range(5)]
			commissions = [commission_data[i][1] for i in range(5)]
		else:
			ppl2 = [commission_data[i][0] for i in range(l2)]
			commissions = [int(commission_data[i][1]) for i in range(l2)]
			for i in range(5 - l):
				ppl2.append(' ')
				commissions.append(0)
		return render_template('agentTopCustomers.html', email=email, emailName=email.split('@')[0], ppl1=ppl1, ppl2=ppl2, tickets=tickets, commissions=commissions)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/agentSearchFlight', methods=['GET', 'POST'])
def agentSearchFlight():
	if session.get('BA_email'):
		email = session['BA_email']
		db_email = check_apostrophe(email)
		airline_name = session['BA_airline']
		airline = check_apostrophe(airline_name)
		departure_city = check_apostrophe(request.form['departure_city'])
		departure_airport = check_apostrophe(request.form['departure_airport'])
		arrival_city = check_apostrophe(request.form['arrival_city'])
		arrival_airport = check_apostrophe(request.form['arrival_airport'])
		departure_date = request.form['departure_date']
		arrival_date = request.form['arrival_date']

		# validate booking agent email
		cursor = conn.cursor()
		query = "SELECT booking_agent_id FROM booking_agent WHERE airline_name = %s AND email = %s"
		cursor.execute(query, (airline, db_email))
		agent_data = cursor.fetchone()
		booking_agent_id = agent_data[0]
		cursor.close()

		if not (agent_data):
			agent_id_error = 'Sorry! You don\'t have the access.'
			return render_template('agentSearchPurchase.html', error1=agent_id_error)

		cursor = conn.cursor()
		query = "SELECT airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, \
						departure_time, arrival_time, status, price, airline_name, num_tickets_left \
				FROM airport AS D, flight, airport AS A \
				WHERE airline_name = %s AND D.airport_city = if (%s = '',D.airport_city, %s) AND \
					D.airport_name = departure_airport AND \
					departure_airport = if (%s = '', departure_airport, %s) AND \
					A.airport_city = if (%s = '', A.airport_city, %s) AND \
					A.airport_name = arrival_airport AND \
					arrival_airport =  if (%s = '', arrival_airport, %s) AND \
					date(departure_time) = if (%s = '', date(departure_time), %s) AND \
					date(arrival_time) =  if (%s = '', date(arrival_time), %s) \
				ORDER BY airline_name, flight_num"
		cursor.execute(query, (airline, departure_city, departure_city,departure_airport,departure_airport, arrival_city, arrival_city, arrival_airport, arrival_airport, departure_date, departure_date, arrival_date, arrival_date))
		data = cursor.fetchall()
		cursor.close()
		
		if (data): # has data
			return render_template('agentSearchPurchase.html', email=email, emailName=email.split('@')[0], upcoming_flights=data)
		else: # does not have data
			error = 'Sorry, we can\'t find any flight!'
			return render_template('agentSearchPurchase.html', email=email, emailName=email.split('@')[0], error1=error)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/agentBuyTickets', methods=['GET', 'POST'])
def agentBuyTickets():
	if session.get('BA_email'):
		email = session['BA_email']
		db_email = check_apostrophe(email)
		airline_name = session['BA_airline']
		airline = check_apostrophe(airline_name)
		flight_num = request.form.get("flight_num")
		customer_email = check_apostrophe(request.form['customer_email'])

		# validate booking agent email
		cursor = conn.cursor()
		query = "SELECT booking_agent_id FROM booking_agent WHERE airline_name = %s AND email = %s"
		cursor.execute(query, (airline, db_email))
		agent_data = cursor.fetchone()
		booking_agent_id = agent_data[0]
		cursor.close()

		if not (agent_data):
			agent_id_error = 'Sorry! You don\'t have the access.'
			return render_template('agentSearchPurchase.html', error1=agent_id_error)
		
		# validate customer email
		cursor = conn.cursor()
		query = "SELECT * FROM customer WHERE email = %s"
		cursor.execute(query, (customer_email,))
		cus_data = cursor.fetchone()
		cursor.close()

		if not (cus_data):
			email_error = 'Your customer is not registered.'
			return render_template('agentSearchPurchase.html', error2=email_error)
	
		cursor = conn.cursor()
		query = "SELECT * \
				FROM flight \
				WHERE airline_name = %s AND flight_num = %s AND num_tickets_left > 0"
		cursor.execute(query, (airline, flight_num))
		flight_data = cursor.fetchall()
		cursor.close()

		if (flight_data): # has ticket
			cursor = conn.cursor()
			# calculate the new ticket id
			cursor = conn.cursor()
			query_id = "SELECT ticket_id \
						FROM ticket \
						ORDER BY ticket_id DESC \
						LIMIT 1"
			cursor.execute(query_id)
			ticket_id_data = cursor.fetchone()
			new_ticket_id = int(ticket_id_data[0]) + 1

			# first insert into ticket
			ins1 = "INSERT INTO ticket VALUES (%s, %s, %s)"
			cursor.execute(ins1, (new_ticket_id, airline, flight_num))

			# then insert into purchases
			ins2 = "INSERT INTO purchases VALUES (%s, %s, %s, CURDATE())"
			cursor.execute(ins2, (new_ticket_id, customer_email, booking_agent_id))
			conn.commit()
			cursor.close()
			message = 'Ticket bought successfully!'
			return render_template('agentSearchPurchase.html', message=message, email=email, emailName=email.split('@')[0])
		else:
			error = 'There\'re no ticket left...'
			return render_template('agentSearchPurchase.html', error2=error, email=email, emailName=email.split('@')[0])	
	else:
		session.clear()
		return render_template('404.html')

#####################################################################
#                         AIRLINE STAFF                             #
#            all operations from the airline_staff side             #
#####################################################################

@app.route('/stafflogin')
def stafflogin():
	return render_template('stafflogin.html')

# define route for register
@app.route('/staffregister')
def staffregister():
	return render_template('staffregister.html')

# authenticate the login
@app.route('/staffloginAuth', methods=['GET', 'POST'])
def staffloginAuth():
	if "username" in request.form and 'password' in request.form:
		username = request.form['username']
		db_username = check_apostrophe(username)
		password = request.form['password']

		cursor = conn.cursor()
		query = "SELECT * FROM airline_staff WHERE username = %s and password = md5(%s)"
		cursor.execute(query, (db_username, password))
		data = cursor.fetchone()

		query1 = "SELECT username, airline_name, airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time FROM flight NATURAL JOIN airline_staff WHERE username = %s AND status = 'upcoming' AND DATEDIFF(CURDATE(), DATE(departure_time)) < 30 "
		cursor.execute(query1, (db_username,))
		data1 = cursor.fetchall()
		cursor.close()

		if (data):
			session['username'] = username
			return render_template('staffhome.html', username=username, posts=data1)
		else:
			error = 'Error: Invalid username or password!'
			return render_template('stafflogin.html', error=error)
	else:
		session.clear()
		return render_template('404.html')

# authenticate the register
@app.route('/staffregisterAuth', methods=['GET', 'POST'])
def staffregisterAuth():
	if "username" in request.form and \
		"password" in request.form and \
		"first_name" in request.form and \
		"last_name" in request.form and \
		"date_of_birth" in request.form and \
		"airline_name" in request.form and \
		"isAdmin" in request.form and \
		"isOperator" in request.form:
		username = request.form['username']
		db_username = check_apostrophe(username)
		password = request.form['password']
		first_name = request.form['first_name']
		db_first_name = check_apostrophe(first_name)
		last_name = request.form['last_name']
		db_last_name = check_apostrophe(last_name)
		date_of_birth = request.form['date_of_birth']
		airline_name = check_apostrophe(request.form['airline_name'])
		isAdmin = request.form['isAdmin']
		isOperator = request.form['isOperator']

		cursor = conn.cursor()
		query = "SELECT * FROM airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		data = cursor.fetchone()

		if(data):
			error = "This user already exists!"
			return render_template('staffregister.html', error = error)
		
		query = "SELECT airline_name FROM airline WHERE airline_name = %s"
		cursor.execute(query, (airline_name,))
		data = cursor.fetchone()
		error = None
		
		if (data): # airline exists
			ins = "INSERT INTO airline_staff VALUES(%s, md5(%s), %s, %s, %s, %s, %s, %s)"
			cursor.execute(ins, (db_username, password, db_first_name, db_last_name, date_of_birth, airline_name, isAdmin, isOperator))
			conn.commit()
			query1 = "SELECT username, airline_name, airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time FROM flight NATURAL JOIN airline_staff WHERE username = %s AND status = 'upcoming' AND DATEDIFF(DATE(departure_time), CURDATE()) < 30 "
			cursor.execute(query1, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			flash("Welcome to FlyEasy!")
			session['username'] = username
			return render_template('staffhome.html', username=username, posts = data1)
		else:
			error = "This airline doesn't exist!"
			cursor.close()
			return render_template('staffregister.html', error=error)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffhome')
def staffhome():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)

		cursor = conn.cursor()
		query = "SELECT username, airline_name, airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time \
				FROM flight NATURAL JOIN airline_staff \
				WHERE username = %s AND status = 'upcoming' AND DATEDIFF(CURDATE(), DATE(departure_time)) < 30 "
		cursor.execute(query, (db_username,))
		data1 = cursor.fetchall()
		cursor.close()
		return render_template('staffhome.html', username=username, posts=data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffflight')
def staffflight():
	if session.get('username'):
		username = session['username'] 
		return render_template('staffflight.html', username=username)
	else:
		session.clear()
		return render_template('404.html')

# only the operator can search and change the status of the flight
@app.route('/staffSearchFlight', methods=['GET', 'POST'])
def staffSearchFlight():
	if session.get('username'):
		departure_city = check_apostrophe(request.form['departure_city'])
		departure_airport = check_apostrophe(request.form['departure_airport'])
		arrival_city = check_apostrophe(request.form['arrival_city'])
		arrival_airport = check_apostrophe(request.form['arrival_airport'])
		departure_date = request.form['departure_date']
		arrival_date = request.form['arrival_date']
		username = session['username']
		db_username = check_apostrophe(username)

		cursor = conn.cursor()
		query = "SELECT airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status, price \
				FROM airport AS D, flight NATURAL JOIN airline_staff, airport AS A \
				WHERE D.airport_city = if (%s = '',D.airport_city, %s) AND \
						D.airport_name = departure_airport AND \
						departure_airport = if (%s = '', departure_airport, %s) AND \
						A.airport_city = if (%s = '', A.airport_city, %s) AND \
						A.airport_name = arrival_airport AND \
						arrival_airport =  if (%s = '', arrival_airport, %s) AND \
						date(departure_time) = if (%s = '', date(departure_time), %s) AND \
						date(arrival_time) =  if (%s = '', date(arrival_time), %s) AND \
						username = %s \
				ORDER BY airline_name, flight_num"
		cursor.execute(query, (departure_city, departure_city,departure_airport,departure_airport, arrival_city, arrival_city, arrival_airport, arrival_airport, departure_date, departure_date, arrival_date,arrival_date, db_username))
		data = cursor.fetchall()

		# validate staff permission
		query = "SELECT isOperator FROM airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		access = cursor.fetchone()
		cursor.close()
		if access[0] == '0':
			error = "Sorry! You don\'t have the access."
			return render_template('staffflight.html', username=username, error1=error)
		
		else:
			if (data): # has data
				return render_template('staffflight.html', username=username, upcoming_flights=data)
			else: 
				error = 'Sorry, we can\'t find any flight!'
				return render_template('staffflight.html', username=username, error1=error)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/edit_status', methods=['GET', 'POST'])
def edit_status():
	if session.get('username'):
		username = session['username'] 
		status = request.form['edit_status']
		flight_num = request.form['flight_num']
		
		cursor = conn.cursor()
		upd = "UPDATE flight SET status = %s WHERE flight_num = %s"
		cursor.execute(upd, (status, flight_num))
		conn.commit()
		cursor.close()

		message = 'Status changed successfully!'
		return render_template('staffflight.html', username=username, message = message)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffaddinfo')
def staffaddinfo():
	if session.get('username'):
		username = session['username'] 
		db_username = check_apostrophe(username)

		cursor = conn.cursor()
		query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		data = cursor.fetchall()
		cursor.close()

		return render_template('staffaddinfo.html', username=username, airplane = data)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		flight_num = request.form['flight_num']
		departure_airport = check_apostrophe(request.form['departure_airport'])
		departure_date = request.form['departure_date']
		departure_time = request.form['departure_time']
		arrival_airport = check_apostrophe(request.form['arrival_airport'])
		arrival_date = request.form['arrival_date']
		arrival_time = request.form['arrival_time']
		price = request.form['price']
		number = request.form['number']
		status = request.form['status']
		airplane_id = request.form['airplane_id']

		# validate staff permission
		cursor = conn.cursor()
		query = "SELECT isAdmin FROM airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		access = cursor.fetchone()
		cursor.close()
		if access[0] == '0':
			error = "Sorry! You don\'t have the access."
			return render_template('staffaddinfo.html', username=username, error1=error)
		
		cursor = conn.cursor()
		airline = "SELECT airline_name FROM airline_staff WHERE username = %s"
		cursor.execute(airline, (db_username,))
		airline_name = cursor.fetchone()
		airline_name = airline_name[0]

		# check departure airport
		query = "SELECT airport_name FROM airport WHERE airport_name = %s"
		cursor.execute(query, (departure_airport,))
		data = cursor.fetchall()
		error1 = None
		if not (data):
			error1 = "Departure airport doesn't exist."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			return render_template('staffaddinfo.html', error1 = error1, username=username, airplane = data1)

		# check arrival airport
		query = "SELECT airport_name FROM airport WHERE airport_name = %s"
		cursor.execute(query, (arrival_airport,))
		data = cursor.fetchall()
		error1 = None
		if not (data):
			error1 = "Arrival airport doesn't exist."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			return render_template('staffaddinfo.html', error1 = error1, username=username, airplane = data1)

		# check airplane type
		query = "SELECT airplane_id FROM airplane WHERE airline_name = %s AND airplane_id = %s"
		cursor.execute(query, (airline_name, airplane_id))
		data = cursor.fetchall()
		error1 = None
		if not (data):
			error1 = "Airplane doesn't exist."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			return render_template('staffaddinfo.html', error1 = error1, username=username, airplane = data1)

		# check number of seats
		num = "SELECT seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s AND airplane_id = %s"
		cursor.execute(num, (db_username, airplane_id))
		num = cursor.fetchone()
		numerror = None
		if int(number) > int(num[0]):
			numerror = "Not enough seats."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			return render_template('staffaddinfo.html', error1 = numerror, username=username, airplane = data1)

		# check flight number
		num = "SELECT airline_name, flight_num FROM flight WHERE airline_name = %s AND flight_num = %s"
		cursor.execute(num, (airline_name, flight_num))
		data = cursor.fetchone()
		error1 = None
		if (data):
			error1 = "Flight already exists."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			return render_template('staffaddinfo.html', error1 = error1, username=username, airplane = data1)		

		else:
			departure_datetime = f"{departure_date} {departure_time}"
			arrival_datetime = f"{arrival_date} {arrival_time}"
			ins = "INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			cursor.execute(ins, (airline_name, flight_num, departure_airport, departure_datetime, arrival_airport, arrival_datetime, price, status, airplane_id, number))
			conn.commit()

			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			message1 = "New flight added successfully!"
			return render_template('staffaddinfo.html', message1 = message1, username=username, airplane = data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		airplane_id = request.form['airplane_id']
		seats = request.form['seats']

		# validate staff permission
		cursor = conn.cursor()
		query = "SELECT isAdmin FROM airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		access = cursor.fetchone()
		cursor.close()
		if access[0] == '0':
			error = "Sorry! You don\'t have the access."
			return render_template('staffaddinfo.html', username=username, error2=error)

		cursor = conn.cursor()
		airline = "SELECT airline_name FROM airline_staff WHERE username = %s"
		cursor.execute(airline, (db_username,))
		airline_name = cursor.fetchone()
		airline_name = airline_name[0]

		# check airplane
		query = "SELECT airplane_id FROM airplane WHERE airline_name = %s AND airplane_id = %s"
		cursor.execute(query, (airline_name, airplane_id))
		data = cursor.fetchone()
		error2 = None
		if (data):
			error2 = "Airplane already exists."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			return render_template('staffaddinfo.html', error2 = error2, username=username, airplane = data1)
		
		else:		
			ins = "INSERT INTO airplane VALUES(%s, %s, %s)"
			cursor.execute(ins, (airline_name, airplane_id, seats))
			conn.commit()

			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			message2 = "New airplane added successfully!"
			return render_template('staffaddinfo.html', message2 = message2, username=username, airplane = data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		airport_name = check_apostrophe(request.form['airport_name'])
		airport_city = check_apostrophe(request.form['airport_city'])

		# validate staff permission
		cursor = conn.cursor()
		query = "SELECT isAdmin FROM airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		access = cursor.fetchone()
		cursor.close()
		if access[0] == '0':
			error = "Sorry! You don\'t have the access."
			return render_template('staffaddinfo.html', username=username, error3=error)

		cursor = conn.cursor()
		# check airport
		airport = "SELECT airport_name FROM airport WHERE airport_name = %s"
		cursor.execute(airport, (airport_name,))
		data = cursor.fetchone()
		error3 = None
		if (data):
			error3 = "Airport already exists."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			return render_template('staffaddinfo.html', error3 = error3, username=username, airplane = data1)

		else:
			ins = "INSERT INTO airport VALUES(%s, %s)"
			cursor.execute(ins, (airport_name, airport_city))
			conn.commit()

			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			message3 = "New airport added successfully!"
			return render_template('staffaddinfo.html', message3 = message3, username=username, airplane = data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/add_agent', methods=['GET', 'POST'])
def add_agent():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		email = check_apostrophe(request.form['email'])

		# validate staff permission
		cursor = conn.cursor()
		query = "SELECT isAdmin FROM airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		access = cursor.fetchone()
		cursor.close()
		if access[0] == '0':
			error = "Sorry! You don\'t have the access."
			return render_template('staffaddinfo.html', username=username, error4=error)

		cursor = conn.cursor()
		airline = "SELECT airline_name FROM airline_staff WHERE username = %s"
		cursor.execute(airline, (db_username,))
		airline_name = cursor.fetchone()
		airline_name = airline_name[0]

		# check agent
		agent = "SELECT * FROM booking_agent WHERE airline_name = %s AND email = %s"
		cursor.execute(agent, (airline_name, email))
		data = cursor.fetchone()
		error4 = None
		if (data):
			error4 = "Agent already exists."
			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			return render_template('staffaddinfo.html', error4 = error4, username=username, airplane = data1)

		else:
			booking_agent = "SELECT password, booking_agent_id FROM booking_agent WHERE email = %s"
			cursor.execute(booking_agent, (email,))
			agent_info = cursor.fetchone()
			password = agent_info[0]
			booking_agent_id = agent_info[1]
			ins = "INSERT INTO booking_agent VALUES(%s, %s, %s, %s)"
			cursor.execute(ins, (email, password, booking_agent_id, airline_name))
			conn.commit()

			query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = %s"
			cursor.execute(query, (db_username,))
			data1 = cursor.fetchall()
			cursor.close()
			message4 = "New agent added successfully!"
			return render_template('staffaddinfo.html', message4 = message4, username=username, airplane = data1)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffgrant')
def staffgrant():
	if session.get('username'):
		username = session['username'] 
		db_username = check_apostrophe(username)
		return render_template('staffgrant.html', username=username)
	else:
		session.clear()
		return render_template('404.html')

# only the admin can search and change the permission of the agent
@app.route('/staffSearchAgent', methods=['GET', 'POST'])
def staffSearchAgent():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		staff_name = check_apostrophe(request.form['staff_name'])

		cursor = conn.cursor()
		query = "SELECT * FROM airline_staff WHERE username = %s"
		cursor.execute(query, (staff_name,))
		data = cursor.fetchone()

		# validate staff permission
		query = "SELECT isAdmin FROM airline_staff WHERE username = %s"
		cursor.execute(query, (db_username,))
		access = cursor.fetchone()
		cursor.close()
		if access[0] == '0':
			error = "Sorry! You don\'t have the access."
			return render_template('staffgrant.html', username=username, error1=error)
		
		else:
			if (data): # has data
				return render_template('staffgrant.html', username=username, current_permit=data)
			else: 
				error = 'Sorry, we can\'t find the staff!'
				return render_template('staffgrant.html', username=username, error1=error)
	else:
		session.clear()
		return render_template('404.html')
	
@app.route('/edit_permit', methods=['GET', 'POST'])
def edit_permit():
	if session.get('username'):
		username = session['username']
		staff_name = request.form['staff_name']
		isAdmin_status = request.form['isAdmin_status']
		isOperator_status = request.form['isOperator_status']
		
		cursor = conn.cursor()
		grant = "UPDATE airline_staff SET isAdmin = %s, isOperator = %s WHERE username = %s"
		cursor.execute(grant, (isAdmin_status, isOperator_status, staff_name))
		conn.commit()
		cursor.close()

		message = 'Permission granted successfully!'
		return render_template('staffgrant.html', username=username, message = message)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffagent')
def staffagent():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)

		cursor = conn.cursor()

		# select agents based on commission
		query1 = "SELECT email, booking_agent_id, SUM(price) * 0.1 AS commission \
				FROM booking_agent NATURAL JOIN purchases NATURAL JOIN flight NATURAL JOIN ticket AS T, airline_staff \
				WHERE username = %s AND airline_staff.airline_name = T.airline_name AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365  \
				GROUP BY email, booking_agent_id ORDER BY commission DESC LIMIT 5 "
		cursor.execute(query1, (db_username,))
		data1 = cursor.fetchall()

		# select agents based on number of tickets (month)
		query2 = "SELECT booking_agent.email, booking_agent_id, COUNT(ticket_id) AS ticket \
				FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket AS T, airline_staff \
				WHERE username = %s AND airline_staff.airline_name = T.airline_name AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 30 \
				GROUP BY email, booking_agent_id ORDER BY ticket DESC LIMIT 5 "
		cursor.execute(query2, (db_username,))
		data2 = cursor.fetchall()

		# select agents based on number of tickets (year)
		query3 = "SELECT email, booking_agent_id, COUNT(ticket_id) AS ticket \
				FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket AS T, airline_staff \
				WHERE username = %s AND airline_staff.airline_name = T.airline_name AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
				GROUP BY email, booking_agent_id ORDER BY ticket DESC LIMIT 5 "
		cursor.execute(query3, (db_username,))
		data3 = cursor.fetchall()

		return render_template('staffagent.html', username=username, commission = data1, month = data2, year = data3)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffcus')
def staffcus():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)

		cursor = conn.cursor()
		query = "SELECT email, name, COUNT(ticket_id) AS ticket \
				FROM customer, purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
				WHERE email = customer_email AND username = %s and DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
				GROUP BY email, name ORDER BY ticket DESC LIMIT 1"
		cursor.execute(query, (db_username,))
		data = cursor.fetchall()
		cursor.close()
		return render_template('staffcus.html', frequent = data, username = username)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffcusflight', methods=['GET', 'POST'])
def staffcusflight():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		email = request.form['customer_email']
		db_email = check_apostrophe(email)

		cursor = conn.cursor()
		query = "SELECT email, name, COUNT(ticket_id) AS ticket \
					FROM customer, purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
					WHERE email = customer_email AND username = %s AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
					GROUP BY email, name ORDER BY ticket DESC LIMIT 1"
		cursor.execute(query, (db_username,))
		data = cursor.fetchall()
		
		# find the flights bought by the customer
		rec = "SELECT DISTINCT airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status \
			FROM customer, purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
			WHERE email = customer_email AND email = %s AND username = %s"
		cursor.execute(rec, (db_email, db_username))
		record = cursor.fetchall()
		cursor.close()
		error = None
		if (record): # if the customer has bought any flight
			return render_template('staffcus.html', cusflight = record, frequent = data, username = username)
		else: # no record
			cursor = conn.cursor()
			# check if the customer exists
			cus = "SELECT email FROM customer WHERE email = %s"
			cursor.execute(cus, (db_email,))
			cus = cursor.fetchone()
			cursor.close()
			if (cus): # customer exists
				error = "The customer did not purchase any flight!"
			else:
				error = "There is no such customer!"
			return render_template('staffcus.html', error = error, frequent = data, username = username)
	else:
		session.clear()
		return render_template('404.html')
	
@app.route('/staffDest')
def staffDest():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)

		cursor = conn.cursor()
		# select top destination (month)
		query1 = "SELECT airport_city, COUNT(ticket_id) AS ticket \
				FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport \
				WHERE airport_name = arrival_airport AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 90 \
				GROUP BY airport_city ORDER BY ticket DESC LIMIT 3"
		cursor.execute(query1)
		month = cursor.fetchall()

		query2 = "SELECT airport_city, COUNT(ticket_id) AS ticket \
				FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport \
				WHERE airport_name = arrival_airport AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
				GROUP BY airport_city ORDER BY ticket DESC LIMIT 3"
		cursor.execute(query2)
		year = cursor.fetchall()

		cursor.close()
		return render_template('staffDest.html', month = month, year = year, username = username)

	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffReve')
def staffReve():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)

		cursor = conn.cursor()
		# monthly direct revenue
		md = "SELECT SUM(price) \
			FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
			WHERE username = %s AND booking_agent_id is NULL AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 30 \
			GROUP BY airline_name"
		cursor.execute(md, (db_username,))
		mdirect = cursor.fetchall()
		if (mdirect):
			mdirect = [int(mdirect[0][0])]
		else:
			mdirect = [0]

		# monthly indirect revenue
		mid = "SELECT SUM(price) \
			FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
			WHERE username = %s AND booking_agent_id is NOT NULL AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 30 \
			GROUP BY airline_name"
		cursor.execute(mid, (db_username,))
		mindirect = cursor.fetchall()
		if (mindirect):
			mindirect = [int(mindirect[0][0])]
		else:
			mindirect = [0]

		# yearly direct revenue
		yd = "SELECT SUM(price) \
			FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
			WHERE username = %s AND booking_agent_id is NULL AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
			GROUP BY airline_name"
		cursor.execute(yd, (db_username,))
		ydirect = cursor.fetchall()
		if (ydirect):
			ydirect = [int(ydirect[0][0])]
		else:
			ydirect = [0]

		# yearly indirect revenue
		yid = "SELECT SUM(price) \
			FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
			WHERE username = %s AND booking_agent_id is NOT NULL AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
			GROUP BY airline_name"
		cursor.execute(yid, (db_username,))
		yindirect = cursor.fetchall()
		if (yindirect):
			yindirect = [int(yindirect[0][0])]
		else:
			yindirect = [0]
		
		cursor.close()

		return render_template('staffReve.html', username = username, mdirect = mdirect, mindirect = mindirect, ydirect = ydirect, yindirect = yindirect)
	else:
		session.clear()
		return render_template('404.html')

@app.route('/staffTickets')
def staffTickets():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)		
		return render_template('staffTickets.html', username = username)
	else:
		session.clear()
		return render_template('404.html')
	
@app.route('/staffticket_range', methods=['GET', 'POST'])
def staffticket_range():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		duration = request.form.get("duration")

		cursor = conn.cursor()
		if duration == 'tmonth': # total amount of tickets sold last month
			ticket = "SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, COUNT(ticket_id) \
					FROM purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket \
					WHERE username = %s AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 30 \
					GROUP BY year, month ORDER BY year, month"
			cursor.execute(ticket, (db_username,))
			fallticket = cursor.fetchall()
		elif duration == 'tyear': # total amount of tickets sold last year
			ticket = "SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, COUNT(ticket_id) \
					FROM purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket \
					WHERE username = %s AND DATEDIFF(CURDATE(), DATE(purchase_date)) < 365 \
					GROUP BY year, month ORDER BY year, month"
			cursor.execute(ticket, (db_username,))
			fallticket = cursor.fetchall()
		cursor.close()

		if (fallticket): # has data
			fs = str(fallticket[0][0]) + '-' + str(fallticket[0][1])
			fe = str(fallticket[len(fallticket) - 1][0]) + '-' + str(fallticket[len(fallticket) - 1][1])
			ftime = [str(fallticket[i][0]) + '-' + str(fallticket[i][1]) for i in range(len(fallticket))]
			fmonthticket = [fallticket[i][2] for i in range(len(fallticket))]
			ftotal = sum(fmonthticket)
			return render_template('staffTickets.html', fs = fs, fe = fe, ft = ftotal, ftime = ftime, fmonthticket = fmonthticket, fticket = fallticket, username = username)
		else:
			ferror = "No ticket sold!"
			return render_template('staffTickets.html', ferror = ferror, username = username)
	else:
		session.clear()
		return render_template('404.html')
	
@app.route('/staffticket_specify', methods=['GET', 'POST'])
def staffticket_specify():
	if session.get('username'):
		username = session['username']
		db_username = check_apostrophe(username)
		start = request.form['start']
		end = request.form['end']

		cursor = conn.cursor()
		# tickets sold within specified time range
		ticket = "SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, COUNT(ticket_id) \
				FROM purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket \
				WHERE purchase_date > %s AND purchase_date < %s AND username = %s \
				GROUP BY year, month ORDER BY year, month"
		cursor.execute(ticket, (start, end, db_username))
		allticket = cursor.fetchall()
		cursor.close()

		if (allticket):
			s = str(allticket[0][0]) + '-' + str(allticket[0][1])
			e = str(allticket[len(allticket) - 1][0]) + '-' + str(allticket[len(allticket) - 1][1])
			time = [str(allticket[i][0]) + '-' + str(allticket[i][1]) for i in range(len(allticket))]
			monthticket = [allticket[i][2] for i in range(len(allticket))]
			total = sum(monthticket)
			return render_template('staffTickets.html', s = s, e = e, t = total, time = time, monthticket = monthticket, ticket = allticket, username = username)
		else:
			error = "No ticket sold!"
			return render_template('staffTickets.html', error = error, username = username)
	else:
		session.clear()
		return render_template('404.html')

#####################################################################
#                             COMMON                                #
#                   all operations from all sides                   #
#####################################################################

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/cuslogin')

app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)