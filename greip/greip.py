import requests
from urllib.parse import quote

BASE_URL = "https://v2.greipapi.com"

available_geoip_params = ['location', 'security', 'timezone', 'currency', 'device']
available_country_params = ['language', 'flag', 'currency', 'timezone']

class CustomResponse:
    def __init__(self, **kwargs):
        #? Initialize attributes from the JSON response
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        #? Create a string representation of all attributes
        properties = {key: value for key, value in self.__dict__.items()}
        return f"CustomResponse({properties})"

    def __repr__(self):
        return self.__str__()

class Greip:
    """Greip instance: it's used to interact with the Greip API.

    Attributes:
        token (str): Your Greip API token.
        test_mode (bool): Whether to use the test mode or not.

    Raises:
        ValueError: If the token is not provided.

    Methods
    -------
        lookup(ip, params=None, lang="EN")
            Get geolocation information about an IP address.
        threats(ip)
            Get information about threats related to an IP address.
        bulk_lookup(ips, params=None, lang="EN")
            Get geolocation information about multiple IP addresses.
        country(country_code, params=None, lang="EN")
            Get information about a country.
        profanity(text, params=None, lang="EN")
            Check if a text contains profanity.
        asn(asn)
            Get information about an ASN.
        email(email)
            Validate an email address.
        phone(phone, country_code)
            Validate/lookup a phone number.
        iban(iban)
            Validate/lookup an IBAN number.
        payment(data)
            Check if a payment transaction is fraudulent.
    """

    def __init__(self, token: str, test_mode=False):
        #? Check if the token is provided
        if not token:
            raise ValueError("Token is required")
        self.token = token
        self.test_mode = test_mode

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _apply_mode(self, payload: dict):
        if self.test_mode:
            payload["mode"] = "test"
        if "source" not in payload:
            payload["source"] = "Python-SDK"

    def _parse_response(self, response):
        if not response.ok:
            raise requests.exceptions.RequestException(response.text)

        json_response = response.json()
        if json_response.get("success") is False:
            raise requests.exceptions.RequestException(
                json_response.get("description", "API request failed")
            )

        data = json_response.get("data")
        if data is None:
            raise requests.exceptions.RequestException("invalid response format: missing data field")

        if isinstance(data, dict):
            return CustomResponse(**data)
        return data

    def _make_http_request(self, path: str, payload: dict):
        url = f"{BASE_URL}/{path.lstrip('/')}"
        self._apply_mode(payload)

        response = requests.get(url, headers=self._headers(), params=payload)
        return self._parse_response(response)

    def _make_http_post_request(self, path: str, payload: dict):
        url = f"{BASE_URL}/{path.lstrip('/')}"
        self._apply_mode(payload)

        response = requests.post(url, headers=self._headers(), json=payload)
        return self._parse_response(response)

    def lookup(self, ip: str, params=None, lang="EN"):
        """Get geolocation information about an IP address."""

        if not ip:
            raise ValueError("You should pass the `ip` parameter.")

        if not isinstance(params, list):
            params = []

        self._validate_params(params, available_geoip_params)
        self._validate_lang(lang)

        payload = {
            "params": ",".join(params),
            "lang": lang.upper(),
        }

        return self._make_http_request(f"lookup/ip/{quote(ip, safe='')}", payload)

    def threats(self, ip: str):
        """Get information about threats related to an IP address."""

        if not ip:
            raise ValueError("You should pass the `ip` parameter.")

        return self._make_http_request(f"score/ip/{quote(ip, safe='')}", {})

    def bulk_lookup(self, ips: list, params=None, lang="EN"):
        """Get geolocation information about multiple IP addresses."""

        if not ips or not isinstance(ips, list) or len(ips) == 0:
            raise ValueError("You should pass the `ips` parameter as a list of IPs.")

        self._validate_ips(ips)
        if not isinstance(params, list):
            params = []

        self._validate_params(params, available_geoip_params)
        self._validate_lang(lang)

        payload = {
            "ips": ",".join(ips),
            "params": ",".join(params),
            "lang": lang.upper(),
        }

        return self._make_http_request("geo/ip/bulk", payload)

    def country(self, country_code: str, params=None, lang="EN"):
        """Get information about a country."""

        if not country_code:
            raise ValueError("You should pass the `country_code` parameter.")
        if len(country_code) != 2:
            raise ValueError("The `country_code` parameter should be in ISO 3166-1 alpha-2 format.")

        if not isinstance(params, list):
            params = []

        self._validate_params(params, available_country_params)
        self._validate_lang(lang)

        payload = {
            "params": ",".join(params),
            "lang": lang.upper(),
        }

        code = country_code.upper()
        return self._make_http_request(f"lookup/countries/{quote(code, safe='')}", payload)

    def profanity(self, text: str):
        """Check if a text contains profanity."""

        if not text:
            raise ValueError("You should pass the `text` parameter.")

        payload = {"text": text}
        return self._make_http_post_request("score/text", payload)

    def asn(self, asn: str):
        """Get information about an ASN."""

        if not asn:
            raise ValueError("You should pass the `asn` parameter.")

        return self._make_http_request(f"lookup/asn/{quote(asn, safe='')}", {})

    def email(self, email: str):
        """Validate an email address."""

        if not email:
            raise ValueError("You should pass the `email` parameter.")

        return self._make_http_request(f"score/email/{quote(email, safe='')}", {})

    def phone(self, phone: str, country_code: str):
        """Validate/lookup a phone number."""

        if not phone:
            raise ValueError("You should pass the `phone` parameter.")

        if len(country_code) != 2:
            raise ValueError("The `country_code` parameter should be in ISO 3166-1 alpha-2 format.")

        payload = {"country_code": country_code.upper()}
        return self._make_http_request(f"score/phone/{quote(phone, safe='')}", payload)

    def iban(self, iban: str):
        """Validate/lookup an IBAN number."""

        if not iban:
            raise ValueError("You should pass the `iban` parameter.")

        return self._make_http_request(f"lookup/iban/{quote(iban, safe='')}", {})

    def payment(self, data: dict):
        """Check if a payment transaction is fraudulent."""

        if not data or not isinstance(data, dict):
            raise ValueError("You should pass the `data` parameter as a dictionary.")

        payload = {"data": data}
        return self._make_http_post_request("score/payments", payload)

    def _validate_params(self, params, valid_params):
        for param in params:
            if param not in valid_params:
                raise ValueError(f'The "{param}" module is unknown. Check available params in the documentation.')

    def _validate_lang(self, lang):
        available_languages = ["EN", "AR", "DE", "FR", "ES", "JA", "ZH", "RU"]
        if lang.upper() not in available_languages:
            raise ValueError(f'The language "{lang}" is invalid. Use one of: {available_languages}')

    def _validate_ips(self, ips):
        for ip in ips:
            if len(ip) < 7:
                raise ValueError("Invalid IP address in the `ips` list.")
