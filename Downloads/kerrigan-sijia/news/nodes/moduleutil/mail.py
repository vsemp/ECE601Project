"""
Mail sending helpers

See documentation in docs/topics/email.rst
"""
import json
import logging
import urllib2


class MailSender(object):

    def __init__(self, messenger_host='localhost',
                 messenger_port=9100, timeout=30):
        self.api = 'http://%(host)s:%(port)s/sendmail' % \
            {'host': messenger_host,
             'port': messenger_port}
        self.timeout = timeout
        self.logger = logging.getLogger('mailsender')

    @classmethod
    def from_settings(cls, settings):
        return cls(settings['MAIL_HOST'], settings['MAIL_PORT'])

    def _format_to_list(self, value):
        if isinstance(value, list):
            return value
        return [i.strip() for i in value.split(',')]

    def send(self, to, subject, body, cc=None,
             bcc=None, attachs=None, _callback=None):
        """
        to: mail to email address, eg, ['a@cootek.cn', 'b@cootek.cn']
        subject: title of email, string
        body: content of email, string
        cc: chao-song email addresses, eg, ['c@cootek.cn', 'd@cootek.cn']
        bcc: anomynous chao-song email addresses, eg, ['e@cootek.cn', 'f@cootek.cn']
        attachs: list for attachments, eg, [('fujian.txt', 'fujian_content', 'text/plain'),...]
        _callback: do callback after sending mail, no matter whether succeeded or not
        """
        msg = {
            'subject': subject,
            'to': self._format_to_list(to),
            'message': body,
        }
        if cc:
            msg['cc'] = self._format_to_list(cc)
        if bcc:
            msg['bcc'] = self._format_to_list(bcc)
        if attachs:
            if isinstance(attachs, tuple):
                msg['attachments'] = [attachs]
            elif isinstance(attachs, list) and isinstance(attachs[0], tuple):
                msg['attachments'] = attachs
            else:
                self.logger.warning(
                    'Email attachs type supports only tuple or list of tuples')
        else:
            attachs = []
        data = json.dumps(
            msg, ensure_ascii=False, encoding='utf8').encode('utf8')
        try:
            urllib2.urlopen(
                self.api, data=data,
                timeout=self.timeout).read()
            self._sent_ok(to, cc, subject, len(attachs))
        except Exception, e:
            self._sent_failed(e, to, cc, subject, len(attachs))

        if _callback:
            _callback(
                to=to, subject=subject, body=body,
                cc=cc, attach=attachs, msg=msg)

    def _sent_ok(self, to, cc, subject, nattachs):
        self.logger.info('Mail sent OK: To=%(mailto)s Cc=%(mailcc)s '
                         'Subject="%(mailsubject)s" Attachs=%(mailattachs)d',
                         {'mailto': to, 'mailcc': cc, 'mailsubject': subject,
                          'mailattachs': nattachs})

    def _sent_failed(self, exception, to, cc, subject, nattachs):
        errstr = str(exception)
        self.logger.error('Unable to send mail: To=%(mailto)s Cc=%(mailcc)s '
                          'Subject="%(mailsubject)s" Attachs=%(mailattachs)d'
                          '- %(mailerr)s',
                          {'mailto': to, 'mailcc': cc, 'mailsubject': subject,
                           'mailattachs': nattachs, 'mailerr': errstr})
