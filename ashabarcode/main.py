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
import random
import StringIO
import base64
from google.appengine.ext import db
from google.appengine.api import mail

import barcode

class Ticket(db.Model):
    email = db.EmailProperty()
    used = db.BooleanProperty()
    time = db.DateTimeProperty()

class TicketCheckingHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")

        barcode = int(self.request.get('barcode'))
        ticket = Ticket.get_by_id(barcode)

        self.response.out.write('<html><body>')
        if not ticket:
            # empty query
            self.response.out.write('1')

        elif not ticket.used:
            ticket.used = True
            ticket.time = datetime.datetime.now()
            ticket.put()
            self.response.out.write('0')

        else:
            self.response.out.write(ticket.time) 
        self.response.out.write('</body></html>')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html><body>')
        tickets = db.GqlQuery("SELECT * FROM Ticket")

        if not tickets:
            return

        self.response.write('<table>')
        for ticket in tickets:
            self.response.write(
                    '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %
                    (ticket.email, ticket.key().id(), ticket.used, ticket.time))
        self.response.write('</table>')
        
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

class TicketHandler(webapp2.RequestHandler):
    def genTicketNum(self, eventNumber):
        #query database for event information based on event number
        return random.randint(0, 999999)

    def sendEmail(self, email, ticketNum): 
        if not mail.is_email_valid(email): 
            self.response.write("<html><body>hello</body></html>")
            #prompt user to enter a valid address
        else:
            message = mail.EmailMessage(sender="Ji Huang <jihuang92@gmail.com>",
                            subject="Your account has been approved")

            message.to = email

            message.body = """
            Dear Albert:

            Your example.com account has been approved.  You can now visit
            http://www.example.com/ and sign in using your Google Account to
            access new features.

            Please let us know if you have any questions.

            The example.com Team
            """

            # Generate image string
            x = barcode.generate(ticketNum, "asdf")
            output = StringIO.StringIO()
            x.save(output, "PNG")
            message.attachments = [('ticket.png', output.getvalue())]
            output.close()

            message.send()

    def get(self):
        eventNumber = cgi.escape(self.request.get('eventNum'))
        numTickets = int(cgi.escape(self.request.get('numTic')))
        email = cgi.escape(self.request.get('email'))

        #seat numbers not implemented
        for i in range (numTickets):
            ticketNum = self.genTicketNum(eventNumber)
            Ticket(id=ticketNum, email=email, used=False).put()
            self.sendEmail(email, str(ticketNum))

        self.response.write("<html><body>hello</body></html>")
        self.response.out.write("""
            <html><body>Your ticket request has been approved.<br>
            Please check your email for a printable ticket. <br>
            Thank you. 
            """)
        self.response.out.write("</body></html>")

app = webapp2.WSGIApplication([('/', MainHandler),
    ('/add', Add),
    ('/submitBarcode.html', TicketCheckingHandler),
    ('/sign', TicketHandler)], 
    debug=True)