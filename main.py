#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import urllib
import datetime
from google.appengine.ext import db
from google.appengine.api import mail

class Ticket(db.Model):
    email = db.EmailProperty()
    ticket_number = db.StringProperty()
    used = db.BooleanProperty()
    time = db.DateTimeProperty()

class TicketCheckingHandler(webapp2.RequestHandler):
    def get(self):
        barcode = self.request.get('barcode')
        tickets = db.GqlQuery("SELECT * FROM Ticket WHERE ticket_number = %s" % barcode)

        self.response.out.write('<html><body>')
        tickets = [ticket for ticket in tickets]
        if not tickets:
            # empty query
            self.response.out.write('0')

        else:
            ticket = tickets[0]
            if not ticket.used:
                ticket.time = datetime.datetime.now()
                self.response.out.write('1')

            else:
                self.response.out.write(ticket.time) 
        self.response.out.write('</body></html>')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""<html><body>
        <form action="/add" method="post">
        Background picture: <input type="file" name="picture">
        <hr>
        Custom text blurb:
        <br>
        Top: <input name="blurb_top">
        <br>
        Mid: <input name="blurb_mid">
        <br>
        Bot: <input name="blurb_bot">
        <hr>
        Ticket category: <input name="ticket_category">
        <hr>
        Ticket number format: <input name="ticket_format">
        <hr>
        Number of tickets to be generated: <input name="num_tickets">
        <hr>
        Email address to which tickets should be sent: <input name="email">
        <input type="submit" value="Submit"></form>
        </body>
        </html>""")

class Add(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        ticket_number = self.request.get('ticket_number')
        Ticket(email=email, ticket_number=ticket_number).put()
        self.redirect('/')

class RUNSHIT(webapp2.RequestHandler):
	def genTicketNum(self, eventNumber): pass
		#query database for event information based on event number
		
	def storeTicket(self,ticketNumber): pass
		#push it into database under same event number
	def genBarcode(self, ticketNumber): pass
		#generate barcode.
		#query database for event information based on event number
	def sendEmail(self, ticketNum, email): 
		if not mail.is_email_valid(email): 
			self.response.write("<html><body>hello</body></html>")
			#prompt user to enter a valid address
		else:
			sender = "jihuang92@gmail.com" #query database?
			eventNum = 1024 #query
			#fileName = ticketNum + ".gif"
			#subject =  "Your registration for event #" + eventNum + " has been confirmed."
			subject = "hello"
			body = """
				bla bla bla
				
				"""
			#attachments = [(filename, fileInfo)]
			mail.send_mail(sender, email, subject, body)
			self.response.write("<html><body>hello</body></html>")
	
		#send the damned email
	def get(self):
		eventNumber = cgi.escape(self.request.get('eventNum'))
		numTickets = int(cgi.escape(self.request.get('numTic')))
		email = cgi.escape(self.request.get('email'))
		
		
		#seat numbers not implemented
		for i in range (numTickets):
			ticketNum = self.genTicketNum(eventNumber)
			self.genBarcode(ticketNum)
			self.storeTicket(ticketNum)
		self.response.write("<html><body>hello</body></html>")
		self.sendEmail(1045, email)
		self.response.out.write("""
			<html><body>Your ticket request has been approved.<br>
			Please check your email for a printable ticket. <br>
			Thank you. 
			""")
		self.response.out.write("</body></html>")

app = webapp2.WSGIApplication([('/', MainHandler),
    ('/add', Add),
    ('/submitBarcode.html', TicketCheckingHandler),
	('/sign', RUNSHIT)], 
    debug=True)
