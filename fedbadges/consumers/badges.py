# -*- coding; utf-8 -*-
# Author: Ross Delinger
# Description: Consumer for producing openbadges by listening for messages on fedmsg

from paste.deploy.converters import asbool
from fedmsg.consumers import FedmsgConsumer
from tahrir_api.dbapi import TahrirDatabase

import logging
log = logging.getLogger("moksha.hub")


class FedoraBadgesConsumer(FedmsgConsumer):
    """
    The Base class for creating fedmsg consumers that issue open badges
    Provides a base that does all of the heavy lifting related to issuing badges.
    All the subclass needs to do is have a topic and implement consume(self, msg)

    :type hub: Moksha Hub
    :param hub: the moksha hub we are getting our messages from
    """

    def __init__(self, hub):
        super(FedoraBadgesConsumer, self).__init__(hub)

        # If fedmsg doesn't think we should be enabled, then we should quit
        # before setting up all the extra special zmq machinery.
        # _initialized is set in moksha.api.hub.consumer
        if not getattr(self, "_initialized", False):
            return

        self.badges = {}

        global_settings = hub.config["badges_global"]
        database_uri = global_settings['database_uri']

        self.tahrir = TahrirDatabase(database_uri)
        self.DBSession = self.tahrir.session_maker

        issuer = global_settings.get('badge_issuer')
        self.issuer_id = self.tahrir.add_issuer(
                issuer.get('issuer_origin'),
                issuer.get('issuer_name'),
                issuer.get('issuer_org'),
                issuer.get('issuer_contact')
                )

        badges_settings = hub.config.get("{0}_badges".format(self.name))
        for badge in badges_settings:
            self.tahrir.add_badge(
                    badge.get('badge_name'),
                    badge.get('badge_image'),
                    badge.get('badge_desc'),
                    badge.get('badge_criteria'),
                    self.issuer_id
                    )


    def award_badge(self, email, badge_id, issued_on=None):
        """
        A high level way to issue a badge to a Person
        It adds the person if they don't exist, and creates an assertion for them

        :type email: str
        :param email: This person's email addr

        :type badge_id: str
        :param badge_id: the id of the badge being awarded

        :type issued_on: DateTime
        :param issued_on: A datetime object with the time this badge was issued
        """

        self.tahrir.add_person(email)
        self.tahrir.add_assertion(badge_id, email, issued_on)

    def consume(self, msg):
        """
        Consume a single message, we pass here because every subclass is going
        to want to parse this slightly differently

        :type msg: dict
        :param msg: The message to be parsed
        """
        pass
