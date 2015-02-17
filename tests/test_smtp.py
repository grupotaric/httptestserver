# -*- coding: utf-8 -*-

import time
import smtplib
import email.message

from hamcrest import (assert_that, is_, instance_of, greater_than,
                      has_entries, contains, contains_string)

from httptestserver import SmtpServer, SmtpTestServer, smtp_server
from httptestserver.smtp_server import DEFAULT_HOST, DEFAULT_PORT


SENDER = 'me@host.com'
RECIPIENTS = ['one@host.com', 'two@host.com']
MESSAGE = 'testing message'


class TestSmtp(SmtpTestServer):
    def test_it_should_start(self):
        assert_that(self.server, is_(instance_of(SmtpServer)))

    def test_it_should_have_current_host(self):
        assert_that(self.server.host, is_(DEFAULT_HOST))

    def test_it_should_have_current_port(self):
        assert_that(self.server.port, is_(greater_than(DEFAULT_PORT)))

    def test_it_should_receive_messages(self):
        self.send_email()

    def test_it_should_have_history(self):
        assert_that(self.server.history, is_([]))

    def test_it_should_have_data(self):
        assert_that(self.server.data, is_({}))

    def test_it_should_store_server_state_in_data(self):
        self.send_email()

        assert_that(self.server.data, self.is_message())

    def test_it_should_store_server_state_in_order(self):
        self.send_email(message='message 1')
        self.send_email(message='message 2')

        assert_that(self.server.history, contains(
            self.is_message(message='message 1'),
            self.is_message(message='message 2')
        ))

    def test_it_should_store_messages_in_inbox(self):
        self.send_email(message='message 1')

        assert_that(self.server.inbox,
                    contains(instance_of(email.message.Message)))

    def test_it_should_store_in_inbox_in_order(self):
        self.send_email(message='message 1')
        self.send_email(message='message 2')

        assert_that(self.server.inbox[0].as_string(),
                    contains_string('message 1'))
        assert_that(self.server.inbox[1].as_string(),
                    contains_string('message 2'))


    def is_message(self, sender=SENDER, recipients=RECIPIENTS, message=MESSAGE):
        return has_entries({
            'mailfrom': sender,
            'message_data': message,
            'recipients': recipients,
            'message': instance_of(email.message.Message),
            'peer': contains('127.0.0.1', instance_of(int))
        })

    def send_email(self, sender=SENDER, recipients=RECIPIENTS, message=MESSAGE):
        smtp = smtplib.SMTP()
        smtp.connect(self.server.host, self.server.port)
        smtp.sendmail(sender, recipients, message)


class TestServerContext(object):
    def test_it_should_give_a_server(self):
        with smtp_server() as server:
            assert_that(server, is_(instance_of(SmtpServer)))

    def test_it_should_start_server(self):
        with smtp_server() as server:
            assert_that(server.accepting, is_(True))

    def test_it_should_stop_server(self):
        with smtp_server() as server:
            pass

        time.sleep(0.02)  # wait for the server to finish
        assert_that(server.is_alive(), is_(False))
