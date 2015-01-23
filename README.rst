The Laughing Robot
------------------


Or, how I learned not to rewrite bower in Python.

To answer the first, obvious question:

    *Why?*

    To allow Python developers/users access to bower components without 
    requiring a node.js / npm infrastructure.

Very basic usage is implemented:

  bower.py install <package> [version]

No dependencies are handled. Versions must be pinned.


INSTALLATION
------------

This will work, preferably installed into a virtualenv::

   pip install bower.py
   bower.py <command>

This is even more self-contained::

   pip install vex
   vex -m bower pip install bower.py
   vex bower bower.py <command>


Things I Learned About Bower
----------------------------

1. bower supports git, svn, http static files, but in reality it supports
   github.com
2. bower "packages" don't even need to supply a bower.json



------------

Copyright 2015, Richard Jones <richard@mechanicalcat.net>
and Rackspace, US, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
