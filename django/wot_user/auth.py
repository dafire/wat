"""OpenID 2.0 - Requesting Authentication
Ref: https://openid.net/specs/openid-authentication-2_0.html#requesting_authentication
"""
from datetime import datetime, timezone
from urllib.parse import urlencode, parse_qs, urlparse
from uuid import uuid4

from django.core.cache import cache
from requests import get, post


def nonce_saver(payload):
    cache.set("nonce_%s" % payload, 1, 3600 * 24 * 14)


def nonce_reader(nonce):
    return cache.get("nonce_%s" % nonce, False)


def check_nonce(nonce):
    if not nonce_reader(nonce):
        nonce_saver(nonce)
        return True
    return False


class BadOpenIDReturnTo(Exception):
    def __init__(self, message, url):
        self.message = message
        self.url = url


class OpenIDFailReturnURLVerification(Exception):
    pass


class OpenIDVerificationFailed(Exception):
    def __init__(self, message, validator):
        self.message = message
        self.validator = validator


class Authentication:

    def __init__(self, return_to, mode=None, ns=None, identity=None,
                 claimed_id=None, request_id=None):
        self.mode = 'checkid_setup' or mode
        self.ns = 'http://specs.openid.net/auth/2.0' or ns
        self.identity = 'http://specs.openid.net/auth/2.0/' \
                        'identifier_select' or identity
        self.claimed_id = 'http://specs.openid.net/auth/2.0/' \
                          'identifier_select' or claimed_id

        self.request_id = request_id or uuid4().hex
        self.return_to = return_to

    def authenticate(self, where, request_id=None):
        """Process to authenticate a request based on few data
        On this step, the most important information is the request_id.
        This parameter will allow us to recover this transaction on
        return url.
        """
        request = get(self.destination(where), allow_redirects=False)
        location = request.headers['Location']

        return location

    @property
    def payload(self):
        """Prepare the OpenID payload to authenticate this request"""
        return {
            'openid.mode': self.mode,
            'openid.ns': self.ns,
            'openid.identity': self.identity,
            'openid.claimed_id': self.claimed_id,
            'openid.return_to': self.return_to,
        }

    def convert(self, payload):
        """Convert the OpenID payload on QueryString format"""
        return urlencode(payload)

    def destination(self, base):
        """Full destination URL to send the payload"""
        return base + '?' + self.convert(self.payload)

    @property
    def evidence(self):
        """This function could be used to get an evidence about what requests
        were sent.
        Example:
        {
         'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
         'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
         'openid.mode': 'checkid_setup',
         'openid.ns': 'http://specs.openid.net/auth/2.0',
         'openid.return_to': 'https://requestb.in/1e7ing31?request_id=07c52d8bb36c4412a4f7e133be9b08ee',
         'request_id': '07c52d8bb36c4412a4f7e133be9b08ee',
         'timestamp': datetime.datetime(2017, 8, 9, 12, 12, 36, 735736, tzinfo=datetime.timezone.utc)
         }
        """
        evidence = {}
        evidence.update(self.payload)
        evidence.update({'request_id': self.request_id})
        evidence.update({'timestamp': datetime.now(timezone.utc)})
        return evidence


class Verification:
    """OpenID data verification.
        Receive a return OpenID URL
        Note:
            Based on OpenID specification
            https://openid.net/specs/openid-authentication-2_0.html
        Args:
            assertion_url
            evidence
        Attributes:
            assertion
    Args:
        assertion_url
        saver: function reference which accepts one argument (data/payload)
               and returns True if was saved.
        reader: function reference which accepts one argument
                (openid.response_nonce) and check if exists on reader
                backend. Returns True if exists.
    """

    def __init__(self, assertion_url, evidence=None, saver=None, reader=None):
        self.assertion = urlparse(assertion_url)
        self.saver = saver or nonce_saver
        self.reader = reader or nonce_reader

    @property
    def return_to(self):
        key = 'openid.return_to'
        query = parse_qs(self.assertion.query)
        if key in query:
            return urlparse(query[key][0])

        else:
            return None

    def is_positive_assertion(self):
        """Positive Assertions
        Reference: https://openid.net/specs/openid-authentication-2_0.html
        Section: 10.1
        Verify 'id_res' as positive assertion.
        Returns:
            reason - When negative assertion
        """
        key = 'openid.mode'
        query = parse_qs(self.assertion.query)

        if key in query:
            mode = query[key][0]
        else:
            raise BadOpenIDReturnTo("return_to url doesn't look to OpenID url",
                                    query)

        if mode == 'id_res':
            return True

        else:
            self.reason = mode
            return False

    def verify_return_url(self):
        """OpenID Verifying the Return URL
        Reference: https://openid.net/specs/openid-authentication-2_0.html#verification
        Section: 11.1
        To verify that the "openid.return_to" URL matches the URL that is
        processing this assertion:
            * The URL scheme, authority, and path MUST be the same between
            the two URLs.
            * Any query parameters that are present in the "openid.return_to"
            URL MUST also be present with the same values in the URL of the
            HTTP request the RP received.
        """

        if self.assertion.scheme != self.return_to.scheme or \
                self.assertion.netloc != self.return_to.netloc or \
                self.assertion.path != self.return_to.path:
            reason = 'scheme/authority/path are not the same'
            raise OpenIDFailReturnURLVerification(reason)

        query_parameters = parse_qs(self.return_to.query)
        assertion_parameters = parse_qs(self.assertion.query)

        for parameter, value in query_parameters.items():
            if parameter in assertion_parameters:
                if value[0] != assertion_parameters[parameter][0]:
                    reason = 'parameter %s has not the same value' % parameter
                    raise OpenIDFailReturnURLVerification(reason)

            else:
                reason = 'parameter %s is not present' % parameter
                raise OpenIDFailReturnURLVerification(reason)

        return True

    def verify_discovered_information(self):
        """OpenID Verifying Discovered Information **NOT IMPLEMENTED**
        Reference: https://openid.net/specs/openid-authentication-2_0.html#verification
        Section: 11.2
        """
        return True

    def check_nonce(self):
        """OpenID Checking the None.
        To prevent replay attacks, the agent checking the signature keeps
        track of the nonce values included in positive assertions and never
        accepts the same value more than once for the same OP Endpoint URL.
        Reference: https://openid.net/specs/openid-authentication-2_0.html#verification
        Section: 11.3
        """
        nonce = parse_qs(self.assertion.query)['openid.response_nonce'][0]

        if not self.reader(nonce):
            self.saver(nonce)
            return True
        else:
            return False

    def verify_signatures(self):
        """OpenID Verifying Signatures (Wargaming uses Direct Verification).
        To have the signature verification performed by the OP,
        the Relying Party sends a direct request to the OP.
        To verify the signature, the OP uses a private association that
         was generated when it issued the positive assertion.
        Reference: https://openid.net/specs/openid-authentication-2_0.html#verification
        Section: 11.4.2
        """
        # Note: This header is very important to allow this application works
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        query = parse_qs(self.assertion.query)

        # Change openid.mode to check the signature
        query['openid.mode'][0] = 'check_authentication'

        # Flatten query object. Remove list and get the [0] element
        query = {key: value[0] for key, value in query.items()}
        to_sign = urlencode(query)

        # Verification Request
        request = post(self.op_endopint, to_sign, allow_redirects=False,
                       headers=headers)

        # Verification parsing
        verification = self.parse_l2l(request.text)

        return verification.get('is_valid', False)

    def identify_the_end_user(self):
        """OpenID Identifying the end user.
        The Claimed Identifier in a successful authentication
        response SHOULD be used by the Relying Party as a key for local
        storage of information about the user. The Claimed Identifier MAY
        be used as a user-visible Identifier.
        When displaying URL Identifiers, the fragment MAY be omitted.
        Reference: https://openid.net/specs/openid-authentication-2_0.html#verification
        Section: 11.5
        Field: openid.identity and openid.claimed_id
        """
        query = parse_qs(self.assertion.query)
        return {
            'identity': query['openid.identity'][0],
            'claimed_id': query['openid.claimed_id'][0],
        }

    def parse_l2l(self, response):
        """Parse line by line OpenID response.
        Example:
        is_valid:false
        ns:http://specs.openid.net/auth/2.0
        """
        cleaned = response.strip().split('\n')
        return {fields.split(':')[0].strip():
                    self.convert_type(''.join(fields.split(':')[1:]).strip())
                for fields in cleaned}

    def convert_type(self, value):
        TYPES = {
            'false': False,
            'true': True
        }
        return TYPES.get(value, value)

    def verify(self):
        """Process to verify an OpenID assertion.
        This is the last step, you'll get a positive identification
        or a failure.
        Returns:
            Identification
        """
        validators = [self.is_positive_assertion,
                      self.verify_return_url,
                      self.verify_discovered_information,
                      self.check_nonce,
                      self.verify_signatures]

        for validator in validators:
            is_valid = validator()

            if not is_valid:
                name = validator.__name__
                reason = 'Validation fail on %s' % name
                raise OpenIDVerificationFailed(reason, name)

        return self.identify_the_end_user()

    @property
    def op_endopint(self):
        query = parse_qs(self.assertion.query)
        return query['openid.op_endpoint'][0]
