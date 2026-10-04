import json
import time
import urllib.request
import urllib.error


def _try_parse_json(body_text):
    try:
        return json.loads(body_text)
    except (json.JSONDecodeError, ValueError, TypeError):
        return body_text


def fetch_with_retry(url, retries=3, backoff=0.5, timeout=5):
    last_status = None

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                status = resp.status
                text = body.decode("utf-8")
                return _try_parse_json(text), status

        except urllib.error.HTTPError as e:
            last_status = e.code
            if 400 <= e.code < 500:
                body = e.read()
                text = body.decode("utf-8")
                return _try_parse_json(text), e.code
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))

        except (urllib.error.URLError, ConnectionError, OSError):
            last_status = None
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))
            else:
                return None, None

    if last_status is not None:
        return None, last_status
    return None, None
