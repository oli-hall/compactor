import asyncio
from collections import defaultdict
import logging
import socket
import threading

from .httpd import HTTPD

from twitter.common.lang import Compatibility

log = logging.getLogger(__name__)


class Context(threading.Thread):
  _SINGLETON = None
  _LOCK = threading.Lock()

  @classmethod
  def make_socket(cls):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', 0))
    ip, port = sock.getsockname()
    if ip == '127.0.0.1':
      ip = socket.gethostbyname(socket.gethostname())
    return s, ip, port
  
  @classmethod
  def singleton(cls, delegate="", **kw):
    with cls._LOCK:
      if cls._SINGLETON:
        if cls._SINGLETON.delegate != delegate:
          raise RuntimeError('Attempting to construct different singleton context.')
      else:
        cls._SINGLETON = cls(delegate=delegate, **kw)
    return cls._SINGLETON

  def __init__(self, delegate="", http_server_impl=HTTPD, loop=None):
    self._processes = {}
    self._links = defaultdict(set)
    self.delegate = delegate
    self.loop = loop or asyncio.new_event_loop()
    self.ip, self.port, self.socket = cls.make_socket()
    self.http = http_server_impl(self.socket, self._handle_request, self.loop)
    super(Context, self).__init__()
    self.daemon = True

  def run(self):
    self.loop.run_forever()

  def stop(self):
    self.loop.stop()
    self.loop.close()

  def spawn(self, process):
    process.bind(self)
    self._processes[pid] = process
    return process.pid

  def send(self, to, method, body=None):
    pass

  def link(self, pid, to):
    self._links[pid].add(to)
  
  def terminate(self, pid):
    self._processes.pop(pid, None)
    for link in self._links.pop(pid, []):
      # TODO(wickman) Not sure why libprocess doesn't send termination events
      pass

  def _handle_request(self, request):
    # TODO(wickman) We should roll our own request object so that we're not
    # tied to tornado.httpserver.HTTPRequest.
    pass
