from cherrypy import wsgiserver
import server

_API_BASE = os.getenv('API_BASE')  # "the base URL for the game API"
_API_TOKEN = os.getenv('API_TOKEN') # "the individual API token given to your team"

server.API_BASE = _API_BASE
server.ARGS.API_token = _API_TOKEN

d = wsgiserver.WSGIPathInfoDispatcher({'/': server.APP})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), d)


if __name__ == '__main__':
   try:
      server.start()
   except KeyboardInterrupt:
      server.stop()