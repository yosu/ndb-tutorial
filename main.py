# Copyright 2015 Google Inc. All rights reserved.
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

"""Cloud Datastore NDB API guestbook sample.

This sample is used on this page:
    https://cloud.google.com/appengine/docs/python/ndb/

For more information, see README.md
"""

# [START all]
import os

from google.appengine.ext import ndb

import webapp2
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'views', 'books')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class Book(ndb.Model):
    name = ndb.StringProperty()

    def greetings(self):
        return Greeting.query(ancestor=self.key).fetch()

    @classmethod
    def list(cls, limit=20):
        return cls.query().order(cls.name).fetch(limit)


class Greeting(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)


class SubmitForm(webapp2.RequestHandler):
    def post(self, book_id_str):
        book_id = int(book_id_str)
        book = Book.get_by_id(book_id)

        if not book:
            self.response.clear()
            self.response.set_status(404)
            self.response.write('Not Found')
            return

        greeting = Greeting(parent=book.key,
                            content=self.request.get('content'))
        greeting.put()

        self.redirect('/books/{}'.format(book_id))


class BooksHandler(webapp2.RequestHandler):
    def get(self):
        books = Book.list()

        template_args = {
            'books': books
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')

        self.response.write(template.render(template_args))

    def post(self):
        book_name = self.request.get('book_name')
        book = Book(name=book_name)
        book.put()

        self.redirect('/')


class BookHandler(webapp2.RequestHandler):
    def get(self, book_id_str):
        book_id = int(book_id_str)
        book = Book.get_by_id(book_id)

        if not book:
            self.response.clear()
            self.response.set_status(404)
            self.response.write('Not Found')
            return

        greetings = Greeting.query_book(book.key).fetch(20)

        template_args = {
            'book': book,
            'greetings': greetings
        }
        template = JINJA_ENVIRONMENT.get_template('show.html')

        self.response.write(template.render(template_args))


app = webapp2.WSGIApplication([
    ('/', BooksHandler),
    (r'/books/(\d+)', BookHandler),
    (r'/books/(\d+)/sign', SubmitForm)
])
# [END all]
