# SPDX-FileCopyrightText: 2022-2024 Michael E. Weiblen http://mew.cx/
#
# SPDX-License-Identifier: MIT

'''
rfc5424.py
This library implements the syslog message formatting specified by RFC5424.
We do not actually transmit the results by any transport; transmission is
left to the caller, to send the results by whatever means.
The formatting specifications are primarily under Section 6 of the RFC.
https://datatracker.ietf.org/doc/html/rfc5424 : "The Syslog Protocol"
'''

import time

__version__ = "1.0.0.1"
__repo__ = "https://github.com/mew-cx/CircuitPython_rfc5424"

#############################################################################
# Enumerations

class Facility:
    "Syslog facilities, Sect 6.2.1"
    KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, LPR, NEWS, UUCP, CRON, \
        AUTHPRIV, FTP = range(0,12)
    LOCAL0, LOCAL1, LOCAL2, LOCAL3, LOCAL4, LOCAL5, LOCAL6, \
        LOCAL7 = range(16, 24)

class Severity:
    "Syslog severities, Sect 6.2.1"
    EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG = range(0,8)

#############################################################################

def FormatTimestamp(ts = None):
    "Sect 6.2.3 specifies a subset of RFC3339 date formatting."
    if not ts:
        ts = time.localtime()
    result = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(
        ts.tm_year, ts.tm_mon, ts.tm_mday,
        ts.tm_hour, ts.tm_min, ts.tm_sec)
    return result

#############################################################################

def FormatSyslog(facility = Facility.USER,
                 severity = Severity.NOTICE,
                 timestamp = None,
                 hostname = None,
                 app_name = None,
                 procid = None,
                 msgid = None,
                 structured_data = None,
                 msg = None) :
    "RFC5424 Section 6.x"
    # Sect 6.2: HEADER MUST be ASCII
    # Sect 9.1: RFC5424's VERSION is "1"
    header = "<{}>1 {} {} {} {} {} ".format(
        (facility << 3) + severity,
        timestamp or "-",
        hostname or "-",
        app_name or "-",
        procid or "-",
        msgid or "-")
    result = header.encode("ascii")

    # Sect 6.3: STRUCTURED-DATA has complicated encoding requirements,
    # so we require it to already be properly encoded.
    if not structured_data:
        structured_data = b"-"
    result += structured_data

    # Sect 6.4: MSG SHOULD be UTF-8, but MAY be other encoding.
    # If using UTF-8, MSG MUST start with Unicode BOM.
    # Sect 6 ABNF: MSG is optional.
    #enc = "utf-8-sig"
    enc = "ascii"       # we're using ASCII
    if msg:
        result += b" " + msg.encode(enc)

    #print(repr(result))    # uncomment for debugging output
    return result

# vim: set sw=4 ts=8 et ic ai:
