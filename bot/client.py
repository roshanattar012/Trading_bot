import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"
TIMEOUT = 10  # seconds


class BinanceAPIError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceNetworkError(Exception):
    pass


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.info("BinanceFuturesClient initialised (base_url=%s)", self.base_url)

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        if signed:
            params = self._sign(params)

        safe_params = {k: v for k, v in params.items() if k != "signature"}
        logger.info("REQUEST  %s %s  params=%s", method.upper(), endpoint, safe_params)

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(url, data=params, timeout=TIMEOUT)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.info(
                "RESPONSE %s %s  status=%s  body=%s",
                method.upper(),
                endpoint,
                response.status_code,
                response.text[:500],
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error("Network timeout for %s %s", method.upper(), url)
            raise BinanceNetworkError(f"Request timed out after {TIMEOUT}s: {url}")
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error for %s %s: %s", method.upper(), url, exc)
            raise BinanceNetworkError(f"Connection error: {exc}")
        except requests.exceptions.HTTPError:
            data = {}
            try:
                data = response.json()
            except Exception:
                pass
            code = data.get("code", response.status_code)
            msg = data.get("msg", response.text)
            logger.error("API error code=%s msg=%s", code, msg)
            raise BinanceAPIError(code, msg)

        return response.json()

    def new_order(self, **params) -> Dict[str, Any]:
        return self._request("POST", "/fapi/v1/order", params=params)

    def get_account(self) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v2/account")

    def get_exchange_info(self) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)
