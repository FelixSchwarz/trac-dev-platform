# -*- coding: utf-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from cStringIO import StringIO
import re

from trac.web.api import Request, RequestDone
from trac.web.chrome import Chrome

class MockResponse(object):
    
    def __init__(self):
        self.status_line = None
        self.headers = []
        self.body = StringIO()
    
    def code(self):
        string_code = self.status_line.split(' ', 1)[0]
        return int(string_code)
    
    def start_response(self, status, response_headers):
        self.status_line = status
        self.headers = response_headers
        return lambda data: self.body.write(data)
    
    def html(self):
        self.body.seek(0)
        body_content = self.body.read()
        self.body.seek(0)
        return body_content
    
    # --- require BeautifulSoup -----------------------------------------------
    
    def trac_messages(self, message_type):
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(self.html())
        message_container = soup.find(name='div', attrs=dict(id='warning'))
        if message_container is None:
            return []
        messages_with_tags = message_container.findAll('li')
        if len(messages_with_tags) > 0:
            strip_tags = lambda html: re.sub('^<li>(.*)</li>$', r'\1', unicode(html))
            return map(strip_tags, messages_with_tags)
        pattern = '<strong>%s:</strong>\s*(.*?)\s*</div>' % message_type
        match = re.search(pattern, unicode(message_container), re.DOTALL | re.IGNORECASE)
        if match is None:
            return []
        return [match.group(1)]
    
    def trac_warnings(self):
        return self.trac_messages('Warning')

    # -------------------------------------------------------------------------


def mock_request(path, request_attributes=None, **kwargs):
    request_attributes = request_attributes or {}
    wsgi_environment = {
        'SERVER_PORT': 4711,
        'SERVER_NAME': 'foo.bar',
        
        'REMOTE_ADDR': '127.0.0.1',
        'REQUEST_METHOD': request_attributes.pop('method', 'GET'),
        'PATH_INFO': path,
        
        'wsgi.url_scheme': 'http',
        'wsgi.input': StringIO(),
    }
    wsgi_environment.update(request_attributes)
    
    response = MockResponse()
    request = Request(wsgi_environment, response.start_response)
    request.captured_response = response
    request.args = kwargs
    
    
    def populate(env):
        from trac.perm import PermissionCache
        from trac.util.datefmt import localtz
        from trac.web.session import Session
        
        self = request
        self.tz = localtz
        self.authname = 'anonymous'
        self.session = Session(env, self)
        from trac.test import MockPerm
        self.perm = PermissionCache(env, 'anonymous')
        self.form_token = None
        self.chrome = dict(warnings=[], notices=[], scripts=[])
#        self.chrome = Chrome(env).prepare_request(self),
        #{'wiki': <function <lambda> at 0x7f33f0640b90>, 'search': <function <lambda> at 0x7f33f0640c80>, 'tags': <function <lambda> at 0x7f33f0640f50>, 'chrome': <function <lambda> at 0x7f33f05611b8>, 'timeline': <function <lambda> at 0x7f33f0640de8>, 'about': <function <lambda> at 0x7f33f0640e60>, 'admin': <function <lambda> at 0x7f33f0640d70>, 'logout': <function <lambda> at 0x7f33f0640cf8>, 'prefs': <function <lambda> at 0x7f33f0640ed8>}
    
    request.populate = populate
    return request


