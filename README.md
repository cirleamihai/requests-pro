# requests_pro

## **requests_pro** is a robust, flexible HTTP client library that defines an API similar to the popular `requests` module. Wraps up multiple client implementations such that one can change between them without changing the underlying code.

It's main focus is to provide flexibility in development processes and to improve code reusability. It simplifies making HTTP requests with advanced features like **automatic header generation**, **middleware for error handling**, **proxy management**, **advanced TLS configurations**, and **persistent sessions**. This package is ideal for projects that require realistic browser-like requests and fine-grained control over connection parameters, but without the overhead and memory usage of a browser.

### Design patterns such as:
- Proxy Pattern
- Adapter Pattern
- Decorator Pattern
- Factory pattern
- Strategy Pattern
### made possible the creation of this library, which comes in very handy when looking for simplicity as well as scalability.

## Features

- **Everything in [`requests`](https://github.com/psf/requests) and [`python-tls-client`](https://github.com/FlorianREGAZ/Python-Tls-Client)**
- **Multiple Client Support:** Choose between a standard `RequestsClient` or a custom `TLSClient` for TLS-encrypted requests.
- **Easy new clients integration which facilitates fast scalability**
- **Middleware Support:** Customize behavior with middleware that handles retries, redirects, and status code validation for each request and thus, deal with exception status in case something goes wrong.
- **Dynamic Header Generation:** Automatically generate and rotate realistic headers (including User-Agent, Accept-Language, etc.) that persist throughout the entire life of a session.
- **Proxy Handling:** Support for proxies via direct configuration or file-based random proxy selection.
- **Advanced TLS Configuration:** Configure custom JA3 strings, HTTP/2 settings, and more for enhanced TLS connections.
- **Session Management:** Maintain persistent sessions with cookie persistence and connection pooling.
- **Factory Pattern:** Use `SessionFactory` to instantiate and configure client sessions from JSON or direct parameters.

## Basic Usage
```py
from requests_pro import RequestsClient

client = RequestsClient()
print(client.headers)  # Already contains more than 6 preset headers, with a randomized user_agent

resp = client.get("https://httpbin.org/get")  # Will automatically retry if the request fails, logging the error
print(resp.status_code)
```
### Broad examples on how to use the library can be found in the [`examples.py`](https://github.com/cirleamihai/requests-pro/blob/main/src/requests_pro/examples.py) file

## Implementing your own Client
```py
# If there is need for a separate implementation, one can do it very easy without forking the package
from requests_pro import MiddlewareClient

class MyOwnClient(MiddlewareClient):
  pass  #  <- make sure to implement every abstract method of it
```

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

## Design Highlights

`requests_pro` was designed with **developer ergonomics**, **realistic web behavior**, and **clean software design** in mind. Key architectural decisions include:

- **Encapsulation of real-world client behaviors** using Proxy + Adapter patterns.
- **Extension without modification**, via base abstract classes like `MiddlewareClient`.
- **Swappable logic units** such as header generators, proxy managers, and middleware controllers.
- **Middleware hooks per request** for granular error handling and recovery logic.
- **Scalable architecture** using Factory + Strategy patterns.

## Contributing

Pull requests are welcome! If you're interested in contributing a new client type or adding utility functions (e.g. a HAR parser or TLS fingerprinting utilities), feel free to open an issue or submit a PR.

Before submitting, please:

- Format with `ruff` or `black`
- Sort imports with `isort`
- Follow existing file organization
- Include minimal working examples in `/examples`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
Made with ❤️ by [cirleamihai](https://github.com/cirleamihai)
