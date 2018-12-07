# -*- coding: utf-8 -*-
from pkg_resources import resource_string, resource_filename, resource_exists
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.utils.spider import iterate_spider_output
from urlparse import urlparse
from scrapy.conf import settings
import fnmatch
import time
import os
import re
import MySQLdb
from util.mail import MailSender


class BaseSpider(CrawlSpider):
    allowed_domains = []  # global allowed domains in rule
    deny_domains = []  # global deny domains in rule
    black_clients = ['proxypool', 'new_proxypool']
    valid_status = [200, 301, 302]
    invalid_httpstatus_deal = {
        403: 86400,
    }
    domain_delay = 0.0
    need_headers = False
    default_section = 60 * 60 * 24
    cootek_proxy = False
    crius_proxy = False
    phoebe_proxy = False

    def __init__(self, *a, **kw):
        CrawlSpider.__init__(self)
        self.init_host_regex()
        self.jobid = kw.get('_job')
        if self.jobid:
            self.resultdir = 'news/%s/%s' % (self.name, self.jobid)
            os.makedirs(self.resultdir)
        else:
            self.resultdir = '.'
        self.resultfile = os.path.join(self.resultdir, self.name)
        self.mailer = MailSender.from_settings(settings)
        self.error_mail_cnt = 0
        self.last_mail_ts = 0
        if self.need_headers:
            self.init_headers()

    def error_notify(self, failure, response):
        if not self.mailer:
            return
        self.error_mail_cnt += 1
        now_ts = time.time()
        if now_ts - self.last_mail_ts < 120:
            return
        self.last_mail_ts = now_ts
        subject = '{Spider Report}{CNFeeds}{Problem %s}' % self.name.upper()
        msg = 'Spider Name: %s\n' % self.name
        msg += 'Date Time: %s\n' % time.strftime(
            '%Y-%m-%d %X', time.localtime())
        msg += 'Spider error processing %s\n' % response.request
        msg += failure.getErrorMessage() + '\n' + failure.getTraceback()
        msg += 'Error Count: %d\n' % self.error_mail_cnt
        self.mailer.send(to=settings['MAIL_TO'], subject=subject, body=msg)

    def get_domain_delay(self, request):
        meta = request.meta
        try:
            domain_delay = meta['domain_delay']
            domain = domain_delay['domain']
            delay = domain_delay['delay']
        except:
            domain_delay = {}
            if not urlparse(request.url).hostname:
                self.logger.error('Url with no host: %s' % request.url)
            if isinstance(self.domain_delay, dict):
                flag = False
                for domain in self.domain_delay:
                    if not domain:
                        continue
                    if fnmatch.fnmatch(urlparse(request.url).hostname, domain):
                        domain_delay['domain'] = domain
                        domain_delay['delay'] = self.domain_delay[domain]
                        flag = True
                        break
                if not flag:
                    domain_delay['domain'] = urlparse(request.url).hostname
                    domain_delay['delay'] = float(0)
            else:
                domain_delay['domain'] = urlparse(request.url).hostname
                domain_delay['delay'] = float(self.domain_delay)
        return domain_delay

    def get_invalid_httpstatus_deal(self):
        return self.invalid_httpstatus_deal

    def init_headers(self):
        conf_file = '%s/headers' % self.dsname
        if not resource_exists('resources', conf_file):
            raise Exception('Failed to load configuration: %s' % conf_file)
        conf = {}
        execfile(resource_filename('resources', conf_file), conf)
        if not 'headers' in conf.keys():
            raise Exception('Failed to load headers: %s' % conf_file)
        self.conf_headers = conf['headers']
        self.conf_cookies = {}
        if 'Cookie' in self.conf_headers:
            cookie_str = self.conf_headers['Cookie']
            for item in cookie_str.split(';'):
                if not item:
                    continue
                key = item.split('=', 1)[0].strip()
                value = item.split('=', 1)[1]
                self.conf_cookies[key] = value
            self.conf_headers.pop('Cookie')

    def init_host_regex(self):
        self._domains_seen = set()
        allowed_domains = getattr(self, 'allowed_domains', None)
        if not allowed_domains:
            self.re_allow = None
        else:
            regex = r'^(.*\.)?(%s)$' % '|'.join(
                re.escape(d) for d in allowed_domains if d is not None)
            self.re_allow = re.compile(regex)
        deny_domains = getattr(self, 'deny_domains', None)
        if not deny_domains:
            self.re_deny = None
        else:
            regex = r'^(.*\.)?(%s)$' % '|'.join(
                re.escape(d) for d in deny_domains if d is not None)
            self.re_deny = re.compile(regex)

    def get_fit_file(self):
        if not hasattr(self, 'resultfile_part'):
            self.resultfile_part = '%s_0' % self.resultfile
        if not os.path.isfile(self.resultfile_part):
            return self.resultfile_part
        if os.path.getsize(self.resultfile_part) < 4294967296:
            return self.resultfile_part
        index = int(self.resultfile_part.rsplit('_', 1)[-1])
        prefix = self.resultfile_part.rsplit('_', 1)[0]
        newfile = '%s_%d' % (prefix, index + 1)
        self.logger.info('Write results into new file: %s' % newfile)
        return newfile

    def _parse_response(self, response, callback, cb_kwargs, follow=True):
        if callback:  # deal with response by callbackfunc defined in the rule
            cb_res = callback(response, **cb_kwargs) or ()
            cb_res = self.process_results(response, cb_res)
            for request in iterate_spider_output(cb_res):
                yield request
        if follow:  # if follow, response is run through all rules again
            for request in self._requests_to_follow(response):
                yield request

    def _requests_to_follow(self, response):
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [l for l in rule.link_extractor.extract_links(
                response) if l not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                if self.should_follow(link.url):
                    r = Request(
                        url=link.url, callback=self._response_downloaded)
                    r.meta.update(rule=n, link_text=link.text)
                    yield rule.process_request(r)
                else:
                    domain = urlparse(link.url).hostname
                    if domain and domain not in self._domains_seen:
                        self._domains_seen.add(domain)
                        self.logger.debug(
                            "Filtered offsite request to %r: %s" %
                            (domain, link.url))

    def should_follow(self, url):
        # hostname can be None for wrong urls (like javascript links)
        domain = urlparse(url).hostname
        if not domain:
            return False
        if self.re_deny and self.re_deny.search(domain):
            return False
        if not self.re_allow:  # allow all by default
            return True
        return bool(self.re_allow.search(domain))
