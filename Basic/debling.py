#!/bin/env python2

from collections import OrderedDict, defaultdict

import argparse
import base64
import functools
import itertools
import operator
import os
import pprint
import pyexcel
import getpass
import pyexcel.ext.xls
import re
import requests
import requests_cache
import string
import sys
import xlwt

import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('detailbilling')

###  argument parsing
def check_user(val):
    while not val:
        val = raw_input("Username: ")
        if not val:
            log.critical('ERROR: Username must not be blank')
            sys.exit(1)
    return val.strip()

def check_apikey(val):
    while not val:
        val = getpass.getpass("APIKey:")
        if not val:
            log.critical('ERROR: APIkey must not be blank')
            sys.exit(1)
    return val.strip()

def check_cache(val):
    if val:
        requests_cache.install_cache("detailbilling.cache", expire_after=3600)

def parse_args(argv=None):
    if not argv:
        argv=sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', action='store_true', help='enable cache of http requests- helpful for development')
    parser.add_argument('--username', type=check_user, default='', help='softlayer username')
    parser.add_argument('--apikey', type=check_apikey, default='', help='softlayer api key')
    opts =  parser.parse_args(argv)
    check_cache(opts.cache)
    return opts


### detail billing generators
def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = string.ascii_uppercase[rem]
    return ''.join(result) + str(row)

def softlayerRestUrl(path, encoding='.json'):
    if encoding is None:
        return "https://api.softlayer.com/rest/v3/" + path
    else:
        return "https://api.softlayer.com/rest/v3/" + path + encoding

def serviceUrl(service, method, *init, **kw):
    initparams = '/'.join(map(str,init))
    if len(initparams) > 0:
        initparams += "/"
    return softlayerRestUrl('SoftLayer_%s/%s%s' % (service, initparams, method), **kw)

def invoiceUrl(invoice):
    assert isinstance(invoice, int)
    return serviceUrl("Billing_Invoice", str(invoice))

def accountUrl(account=None):
    assert account is None or isinstance(account, basestring)
    return serviceUrl("Account", "getObject" if not account else account)

def excelUrl(invoice):
    assert isinstance(invoice, int)
    return serviceUrl("Billing_Invoice", "getExcel", invoice, encoding=None)

def xlsFilenameUrl(invoice):
    assert isinstance(invoice, int)
    return serviceUrl("Billing_Invoice", "getXlsFilename", invoice)

def tagUrl(tag):
    assert isinstance(tag, int)
    return serviceUrl("Tag", "getObject" if not tag else tag)

def virtualGuestUrl(guest=None):
    assert isinstance(guest, int)
    return serviceUrl("Virtual_Guest", guest)

class memoized_property(object):
    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        try:
            return inst._cache[self.__name__]
        except (AttributeError, KeyError):
            value = self.fget(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = value
        return value

class HorizontalInvoiceView(object):
    COST_CATEGORY_COLLAPSE_MAP = OrderedDict([
        # occur in top level items
        (r'^server$', 'Server'),
        (r'^guest_core$', 'Virtual Machine'),
        (r'^evault$', 'EVault'),
        (r'^nas$', 'NAS'),
        (r'^virtual_peak_usage$', 'VMware/ESX Peak Usage'),
        (r'^guest_storage$', 'Archive Storage Repository'),
        (r'^guest_storage_usage$', 'Archive Storage Repository Usage'),
        (r'^sov_sec_ip_addresses_priv$', 'IP Addresses'),

        # occur in second level items
        (r'^second_processor$', 'Processors'),
        (r'^ram$', 'RAM'),
        (r'^(guest_)?disk\d+$', 'Hard Disks'),
        (r'^disk_controller$', 'Disk Controller'),
        (r'^bandwidth$', 'Bandwidth'),
        (r'^pri_ip(v6)?_addresses$', 'IP Addresses'),
        (r'^port_speed|public_port$', 'Network Ports'),
        (r'^bandwidth$', 'Network Bandwidth'),
        (r'^firewall$', 'Firewall'),
        (r'^monitoring_package$', 'Monitoring'),
        (r'^av_spyware_protection$', 'Antivirus & Spyware Protection'),
        (r'^os(_addon)?$', 'Operating System'),
        (r'^power_supply$', 'Power Supply'),
        (r'^database$', 'Database'),
    ])

    def __init__(self, title, invoice, tags):
        self.title = title
        self.invoice = invoice
        self.tags = tags

    def mapped_tag_generator(self):
        for tag in self.tags:
            if not 'name' in tag:
                continue

            if not 'references' in tag:
                continue

            tagpairs = map(lambda t: tuple(map(str, t.split(':',1))), tag['name'].split())

            tagpairs = filter(lambda p: len(p) == 2 and p[0] and p[1], tagpairs)

            tagpairs = map(lambda t: (str.lower(t[0]), t[1],), tagpairs)

            refs = filter(None, [ r.get('resourceTableId', None) for r in tag['references'] ])

            for m in [(r, t,) for t in tagpairs for r in refs]:
                yield m

    @memoized_property()
    def mapped_tags(self):
        tags = defaultdict(defaultdict)
        for k,v in self.mapped_tag_generator():
            tags[k][v[0]] = v[1]
        return tags

    # cached properties should be called in DAG
    @memoized_property()
    def headers(self):
        return [ 'Hostname', 'Description', 'Business Unit', 'Object Account', 'Sub-Ledger Account', 'RFS/SOW/WO' ] \
               + self.ordered_cost_categories \
               + self.ordered_fee_categories \
               + [ 'Total' ]

    @memoized_property()
    def fee_translation_table(self):
        translation = OrderedDict()
        translation.update(itertools.izip_longest(self.RECURRING_FEES, [], fillvalue='Recurring Fee'))
        translation.update(itertools.izip_longest(self.RECURRING_TAX, [], fillvalue='Recurring Tax'))
        translation.update(itertools.izip_longest(self.ONE_TIME_FEES, [], fillvalue='OTC Fee'))
        translation.update(itertools.izip_longest(self.ONE_TIME_TAX, [], fillvalue='OTC Tax'))
        return translation

    ordered_fee_categories = ['Recurring Fee', 'Recurring Tax', 'OTC Fee', 'OTC Tax']

    @memoized_property()
    def fee_categories(self):
        return set(self.ordered_fee_categories)

    @memoized_property()
    def cost_translation_table(self):
        match_table = map(lambda i: (re.compile(i[0]), i[1]), self.COST_CATEGORY_COLLAPSE_MAP.items())

        translations = {}
        newcats = set()

        for cat in self.cost_categories:
            matched = [v for k,v in match_table if k.match(cat)]
            if len(matched) > 1:
                newcat = matched[0]
                log.warn('cost category "%s" matches multiple aggregation expressions- %s. expressions are not mutually exclusive. using the first match' % (cat, str(matched)))
            elif len(matched) == 0:
                newcat = string.capwords(cat.replace('_',' '))
                if newcat not in newcats:
                    log.warn('cost category "%s" matches no expressions. using new cost category name "%s"' % (cat, newcat))
            else:
                newcat = matched[0]
            newcats.add(newcat)
            translations.setdefault(cat, newcat)

        return translations

    RECURRING_FEES = ['recurringFee']
    RECURRING_TAX = ['recurringTaxAmount']
    ONE_TIME_FEES = ['oneTimeFee', 'setupFee', 'laborFee']
    ONE_TIME_TAX = ['oneTimeTaxAmount', 'setupTaxAmount', 'laborTaxAmount']

    ALL_FEES = RECURRING_FEES + RECURRING_TAX + ONE_TIME_FEES + ONE_TIME_TAX

    @memoized_property()
    def toplevel_billing_items(self):
        topitems = []

        for topitem in self.invoice['invoiceTopLevelItems']:
            i = {}
            topitems.append(i)

            if topitem.get('hostName') and topitem.get('domainName'):
                i['Hostname'] = "%s.%s" % (topitem['hostName'], topitem['domainName'])

            resourceid = topitem.get('resourceTableId', None)

            if resourceid:
                i['Business Unit'] = self.mapped_tags.get(resourceid, {}).get('bu', '')
                i['Object Account'] = self.mapped_tags.get(resourceid, {}).get('oa', '')
                i['Sub-Ledger Account'] = self.mapped_tags.get(resourceid, {}).get('sl', '')
                i['RFS/SOW/WO'] = self.mapped_tags.get(resourceid, {}).get('sw', '')

            i['Description'] = topitem.get('description','')

            costs = []

            for item in [topitem] + topitem['children']:
                costs += [(item['categoryCode'],fee,float(item.get(fee, 0.0))) for fee in self.ALL_FEES]

            for cat, fee, v in costs:
                i.setdefault(fee, 0.0)
                i[fee] += v
                i.setdefault(cat, 0.0)
                i[cat] += v

        return topitems

    @memoized_property()
    def device_rows(self):
        rownum = len(list(self.header_rows())) + 1

        rows = []

        numeric_column_map = dict(self.cost_translation_table.items() + self.fee_translation_table.items())
        reverse_numeric_column_map = defaultdict(list)

        for k,v in numeric_column_map.items():
            reverse_numeric_column_map[v].append(k)

        for item in self.toplevel_billing_items:
            row = []
            get_summer = lambda accum, k: item.get(k, 0.0) + accum
            for col in self.headers:
                if col in reverse_numeric_column_map:
                    col_total = reduce(get_summer, reverse_numeric_column_map[col], 0.0)
                    row.append(round(col_total,2))
                elif col == 'Total':
                    row.append(xlwt.Formula('SUM(%s:%s)' % (excel_style(rownum, len(row) + -len(self.fee_categories) + 1), excel_style(rownum, len(row)))))
                else:
                    row.append(item.get(col, ''))
            rows.append(row)
            rownum += 1

        return rows

    @memoized_property()
    def translated_cost_categories(self):
        return set(map(self.cost_translation_table.get, self.cost_categories))

    @memoized_property()
    def ordered_cost_categories(self):
        order_keys = { v: k for k,v in reversed(list(enumerate(self.COST_CATEGORY_COLLAPSE_MAP.values())))}

        def order_func(i):
            return order_keys.get(i, len(order_keys))

        return sorted(list(self.translated_cost_categories), key=order_func)

    @memoized_property()
    def cost_categories(self):
        return self.top_cost_categories | self.child_cost_categories

    @memoized_property()
    def top_cost_categories(self):
        cats = set()

        for topitem in self.invoice['invoiceTopLevelItems']:
            cats.add(topitem['categoryCode'])

        return cats

    @memoized_property()
    def child_cost_categories(self):
        cats = set()

        for topitem in self.invoice['invoiceTopLevelItems']:
            for item in topitem['children']:
                cats.add(item['categoryCode'])

        return cats

    def header_rows(self):
        yield [self.title,]
        yield self.headers

    def rows(self):
        for row in self.device_rows:
            yield row

    @memoized_property()
    def total_row(self):
        first_row = len(list(self.header_rows())) + 1
        rownum = len(list(self.header_rows())) + len(list(self.rows())) + 1
        numeric_columns = self.fee_categories | self.translated_cost_categories

        def total_val(colnum, col):
            if colnum == 1:
                return 'Total'
            elif col in numeric_columns or col == 'Total':
                formula = xlwt.Formula('SUM(%s:%s)' % (excel_style(first_row, colnum), excel_style(rownum - 1, colnum)))
                # print formula.text()
                # import time
                # time.sleep(0.5)
                return formula

        return [total_val(colnum+1, col) for colnum, col in enumerate(self.headers)]

    def footer_rows(self):
        yield self.total_row

    def rendered_gen(self):
        for row in itertools.chain(self.header_rows(), self.rows(), self.footer_rows()):
            yield row

    def rendered(self):
        return list(self.rendered_gen())

def HorizontalInvoiceViewRenderer(title, invoice, tags):
    return HorizontalInvoiceView(title, invoice, tags).rendered()

if __name__ == "__main__":
    # parse args, get softlayer credentials
    opts = parse_args()
    SL_USER = opts.username
    SL_APIKEY = opts.apikey

    # requests session and credentials
    s = requests.Session()
    s.auth = (SL_USER, SL_APIKEY,)

    # fetch potential invoices
    r = s.get(accountUrl(), params={"objectMask": "filteredMask[invoices[id,createDate,typeCode]]"})

    # filter out recurring invoices and sort by create date
    invoice_response = r.json()
    recurring_invoices = filter(lambda i: str(i['typeCode']) == 'RECURRING', invoice_response['invoices'])
    invoices = map(lambda i: (i['id'], i['createDate'],), sorted(recurring_invoices, key=lambda i: i['createDate'], reverse=True))

    for invoice_id, create_date in invoices:
        log.info('processing invoice created %s (%s)' % (create_date, invoice_id))

        # download and save unmodified spreadsheet
        r = s.get(xlsFilenameUrl(invoice_id))
        xlsFilename = r.json()

        xlsOrigFilename = "%s-unmodified.%s" % tuple(xlsFilename.rsplit('.', 1))

        if not os.path.exists(xlsOrigFilename):
            r = s.get(excelUrl(invoice_id))
            with open(xlsOrigFilename, 'w') as fh:
                fh.write(base64.b64decode(r.json()))
        else:
            log.info('unmodified invoice %s already exists' % xlsOrigFilename)

        if not os.path.exists(xlsFilename):
            # rewrite
            pyex = pyexcel.get_book(file_name=xlsOrigFilename)

            # fetch related billing items
            r = s.get(invoiceUrl(invoice_id), params={"objectMask": "filteredMask[invoiceTopLevelItems[product,children,totalOneTimeAmount,totalOneTimeTaxAmount,totalRecurringAmount,totalRecurringTaxAmount]]"})
            fullinvoice = r.json()

            # get tags from billing items
            r = s.get(serviceUrl('Account', 'getTags'), params={"objectMask": "filteredMask[name,references[resourceTableId]]"})
            alltags = r.json()

            # generate transposed invoice view
            view = HorizontalInvoiceView('Chargeback Details', fullinvoice, alltags)
            sheet_data = view.rendered()
            pyex += pyex.get_sheet(sheet_data, "Chargeback Details")

            ## for debugging
            # pprint.pprint(view.top_cost_categories)
            # pprint.pprint(view.child_cost_categories)
            # pprint.pprint(view.translated_cost_categories)
            # pprint.pprint(view.ordered_cost_categories)
            # pprint.pprint(view.headers)
            # pprint.pprint(view.toplevel_billing_items)
            # pprint.pprint(view.device_rows)
            # pprint.pprint(view.mapped_tags)

            ## for debugging- maybe open a nice interactive shell
            # IPython.embed()

            log.info('writing modified invoice to %s' % xlsFilename)
            pyex.save_as(filename=xlsFilename)

# vim: set ts=4 sw=4 expandtab:
