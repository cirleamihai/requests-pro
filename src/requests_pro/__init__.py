# Disclaimer:
# This package defines first of all, API for any kind of HTTP requests
# clients that you'd like to wrap around with this. The biggest advantage is that
# you can easily switch between the two clients without changing the code later on.
# By forcing the concrete clients to implement the same methods, it can give your
# project a lot of flexibility and scalability in the future. Moreover, by combining
# multiple design patterns such as Proxy Design Pattern, Factory Method i managed to
# refurbish a lot of code and make it more readable and maintainable.
#
# The main reason why i started this was to deal with the ever growing issue of checking
# the status codes after making a request. By using this wrapper, you can easily
# rely on the library's internal method of checking the status codes and either catch
# the exceptions in a broader context or just let the program crash.
#
#
# Another reason why i made this was because people were always trying to match
# the headers and proxies when it came to session persistence. Doing this once the
# client is created is much better than doing it every time you make a request.
# Having this, you minimize the risk that comes with making small typos in one request.
#
#
# Big shoutout to Florian for wrapping up bogdanfinn's tls-client in Python.
# As it contained some errors, I've made my own wrap-around it.
#
#
# I highly suggest and recommend that people fork this and integrate
# it into their own projects rather than using this package as a dependency.
# The two clients can be used out of the box, but they are lacking some features
# such as antibot support and other 3rd party api integrations optionality.
#
#
# In order to add anti-bot support, you would need to rely on the AntiBotBlockError
# that is being raised in the Middleware class. This is a good starting point.

# florian-tls: https://github.com/FlorianREGAZ/Python-Tls-Client
# tls-client: https://github.com/bogdanfinn/tls-client
# requests: https://github.com/psf/requests

from middlewareClient import MiddlewareClient
from requestsClient import RequestsClient
from response import Response
from sessionFactory import SessionFactory
from tlsClient import TLSClient
