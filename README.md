# requests_pro

## **requests_pro** is a robust, flexible HTTP client library built on top of Python's `requests` and custom TLS client implementations.

It's main focus is to provide flexibility in development processes and to improve code reusability. It simplifies making HTTP requests with advanced features like **automatic header generation**, **middleware for error handling**, **proxy management**, **advanced TLS configurations**, and **persistent sessions**. This package is ideal for projects that require realistic browser-like requests and fine-grained control over connection parameters, but without the overhead and memory usage of a browser.

## Features

- **Everything in [`requests`](https://github.com/psf/requests) and [`python-tls-client`](https://github.com/FlorianREGAZ/Python-Tls-Client)**
- **Multiple Client Support:** Choose between a standard `RequestsClient` or a custom `TLSClient` for TLS-encrypted requests.
- **Middleware Support:** Customize behavior with middleware that handles retries, redirects, and status code validation for each request and thus, deal with exception status in case something goes wrong.
- **Dynamic Header Generation:** Automatically generate and rotate realistic headers (including User-Agent, Accept-Language, etc.).
- **Proxy Handling:** Support for proxies via direct configuration or file-based random proxy selection.
- **Advanced TLS Configuration:** Configure custom JA3 strings, HTTP/2 settings, and more for enhanced TLS connections.
- **Session Management:** Maintain persistent sessions with cookie persistence and connection pooling.
- **Factory Pattern:** Use `SessionFactory` to instantiate and configure client sessions from JSON or direct parameters.

## Installation

Install the package via pip:

```bash
pip install requests_pro
```

Or, if you are developing locally:
```bash
git clone https://github.com/cirleamihai/requests_pro.git
cd requests_pro
pip install .
```
