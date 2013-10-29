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

import shutil
import tempfile

from trac import __version__ as trac_version


if not trac_version.startswith('0.11'):
    from trac.test import EnvironmentStub
    
    class EnvironmentStub10(EnvironmentStub):
        # Trac 1.0 has a @lazy decorator which replaces the decorated method
        # with a plain dict after first access. For testing purposes I'll just
        # include the actual code from Trac but without any caching.
        @property
        def _component_rules(self):
            _rules = {}
            for name, value in self.components_section.options():
                if name.endswith('.*'):
                    name = name[:-2]
                _rules[name.lower()] = value.lower() in ('enabled', 'on')
            return _rules
    EnvironmentStub = EnvironmentStub10
else:
    from trac.env import Environment
    from trac.test import EnvironmentStub

    class FixedEnvironmentStub(EnvironmentStub):
        """Since the release of trac 0.11 a lot of bugs were fixed in the 
        EnvironmentStub. This class provides backports of these fixes so plugins
        can support older trac versions as well."""
        
        # See http://trac.edgewall.org/ticket/8591
        # 'Can not disable components with EnvironmentStub'
        # fixed in 0.12
        def __init__(self, default_data=False, enable=None):
            super(FixedEnvironmentStub, self).__init__(default_data=default_data, enable=enable)
            if enable is not None:
                self.config.set('components', 'trac.*', 'disabled')
            for name_or_class in enable or ():
                config_key = self.normalize_configuration_key(name_or_class)
                self.config.set('components', config_key, 'enabled')
            self._did_create_temp_directory = False
        
        def normalize_configuration_key(self, name_or_class):
            name = name_or_class
            if not isinstance(name_or_class, basestring):
                name = name_or_class.__module__ + '.' + name_or_class.__name__
            return name.lower()
        
        def is_component_enabled(self, cls):
            return Environment.is_component_enabled(self, cls)
        
        # TODO: Better naming
        def use_temp_directory(self):
            if self._did_create_temp_directory:
                return
            self.path = tempfile.mkdtemp()
            self._did_create_temp_directory = True
        
        def destroy_temp_directory(self):
            if not self._did_create_temp_directory:
                return
            shutil.rmtree(self.path)
        
        # See http://trac.edgewall.org/ticket/7619
        # 'EnvironmentStub wrong implementation of get_known_users()'
        # fixed in 0.11.2
        def get_known_users(self, db=None):
            return self.known_users
    EnvironmentStub = FixedEnvironmentStub


