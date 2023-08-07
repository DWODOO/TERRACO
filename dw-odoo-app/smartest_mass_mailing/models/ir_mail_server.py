# -*- coding: utf-8 -*-

# Import Python libs
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, make_msgid
import threading
import html2text

# Import from Odoo
from odoo import models, tools
from odoo.tools import ustr, pycompat
# from odoo.addons.base.models.ir_mail_server import encode_header_param, encode_header, encode_rfc2822_address_header

# Class
class SmartestMailServer(models.Model):
    _inherit = 'ir.mail_server'


    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
                    attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
                    body_alternative=None, subtype_alternative='plain'):
        """Constructs an RFC2822 email.message.Message object based on the keyword arguments passed, and returns it.

           :param string email_from: sender email address
           :param list email_to: list of recipient addresses (to be joined with commas)
           :param string subject: email subject (no pre-encoding/quoting necessary)
           :param string body: email body, of the type ``subtype`` (by default, plaintext).
                               If html subtype is used, the message will be automatically converted
                               to plaintext and wrapped in multipart/alternative, unless an explicit
                               ``body_alternative`` version is passed.
           :param string body_alternative: optional alternative body, of the type specified in ``subtype_alternative``
           :param string reply_to: optional value of Reply-To header
           :param string object_id: optional tracking identifier, to be included in the message-id for
                                    recognizing replies. Suggested format for object-id is "res_id-model",
                                    e.g. "12345-crm.lead".
           :param string subtype: optional mime subtype for the text body (usually 'plain' or 'html'),
                                  must match the format of the ``body`` parameter. Default is 'plain',
                                  making the content part of the mail "text/plain".
           :param string subtype_alternative: optional mime subtype of ``body_alternative`` (usually 'plain'
                                              or 'html'). Default is 'plain'.
           :param list attachments: list of (filename, filecontents) pairs, where filecontents is a string
                                    containing the bytes of the attachment
           :param list email_cc: optional list of string values for CC header (to be joined with commas)
           :param list email_bcc: optional list of string values for BCC header (to be joined with commas)
           :param dict headers: optional map of headers to set on the outgoing mail (may override the
                                other headers, including Subject, Reply-To, Message-Id, etc.)
           :rtype: email.message.Message (usually MIMEMultipart)
           :return: the new RFC2822 email message
        """
        email_from = email_from or self._get_default_from_address()
        assert email_from, "You must either provide a sender address explicitly or configure "\
                           "using the combintion of `mail.catchall.domain` and `mail.default.from` "\
                           "ICPs, in the server configuration file or with the "\
                           "--email-from startup parameter."

        # Note: we must force all strings to to 8-bit utf-8 when crafting message,
        #       or use encode_header() for headers, which does it automatically.

        headers = headers or {}         # need valid dict later
        email_cc = email_cc or []
        email_bcc = email_bcc or []
        body = body or u''

        email_body = ustr(body)
        email_text_part = MIMEText(email_body, _subtype=subtype, _charset='utf-8')
        msg = MIMEMultipart()

        if not message_id:
            if object_id:
                message_id = tools.generate_tracking_message_id(object_id)
            else:
                message_id = make_msgid()
        msg['Message-Id'] = encode_header(message_id)
        if references:
            msg['references'] = encode_header(references)
        msg['Subject'] = encode_header(subject)
        msg['From'] = encode_rfc2822_address_header(email_from)
        del msg['Reply-To']
        if reply_to:
            msg['Reply-To'] = encode_rfc2822_address_header(reply_to)
        else:
            msg['Reply-To'] = msg['From']
        msg['To'] = encode_rfc2822_address_header(COMMASPACE.join(email_to))
        if email_cc:
            msg['Cc'] = encode_rfc2822_address_header(COMMASPACE.join(email_cc))
        if email_bcc:
            msg['Bcc'] = encode_rfc2822_address_header(COMMASPACE.join(email_bcc))
        msg['Date'] = formatdate()
        # Custom headers may override normal headers or provide additional ones
        for key, value in headers.items():
            msg[pycompat.to_text(ustr(key))] = encode_header(value)

        if subtype == 'html' and not body_alternative:
            # Always provide alternative text body ourselves if possible.
            text = html2text.html2text(email_body)
            alternative_part = MIMEMultipart(_subtype="alternative")
            alternative_part.attach(MIMEText(text, _charset='utf-8', _subtype='plain'))
            alternative_part.attach(email_text_part)
            msg.attach(alternative_part)
        elif body_alternative:
            # Include both alternatives, as specified, within a multipart/alternative part
            alternative_part = MIMEMultipart(_subtype="alternative")
            body_alternative_ = ustr(body_alternative)
            alternative_body_part = MIMEText(body_alternative_, _subtype=subtype_alternative, _charset='utf-8')
            alternative_part.attach(alternative_body_part)
            alternative_part.attach(email_text_part)
            msg.attach(alternative_part)
        else:
            msg.attach(email_text_part)

        if attachments:
            for (fname, fcontent, mime, id) in attachments:
                filename_rfc2047 = encode_header_param(fname)
                if mime and '/' in mime:
                    maintype, subtype = mime.split('/', 1)
                    part = MIMEBase(maintype, subtype)
                else:
                    part = MIMEBase('application', "octet-stream")

                # The default RFC2231 encoding of Message.add_header() works in Thunderbird but not GMail
                # so we fix it by using RFC2047 encoding for the filename instead.
                part.set_param('name', filename_rfc2047)
                part.add_header('Content-ID', '<{}>'.format(str(id)))
                part.add_header('Content-Disposition', 'inline', filename=filename_rfc2047)

                part.set_payload(fcontent)
                encoders.encode_base64(part)
                msg.attach(part)

        return msg
