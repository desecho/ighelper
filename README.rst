InstagramHelper
==========================================================

|Build Status| |Requirements Status| |Codecov|

The web application on Django_ 2, Vue.js_ 2, Bootstrap_ 4. It allows you to manage your followers and medias. It also allows you to get statistics.

Features:

- See how many photos & videos your followers liked
- Manage your followers:
    - follow
    - unfollow
    - block
    - mark as approved
- Statistics:
    - Get total number of:
        - photos
        - videos
        - followers
        - likes
        - views
    - Get average number of:
        - likes
        - views

- Manage your medias:
    - see caption, location, date and number of likes
    - edit caption

- Identify issues with medias like:
    - no caption
    - no location
    - no tags


Installation instructions
----------------------------

1. Use ansible-playbook-server_ to deploy.
2. Do git clone.

Development
--------------

| Use ``clean.sh`` to automatically prettify your code.
| Use ``tox`` for testing and linting.

.. |Requirements Status| image:: https://requires.io/github/desecho/ighelper/requirements.svg?branch=master
   :target: https://requires.io/github/desecho/ighelper/requirements/?branch=master

.. |Codecov| image:: https://codecov.io/gh/desecho/ighelper/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/desecho/ighelper

.. |Build Status| image:: https://travis-ci.org/desecho/ighelper.svg?branch=master
   :target: https://travis-ci.org/desecho/ighelper

.. _ansible-playbook-server: https://github.com/desecho/ansible-playbook-server
.. _Vue.js: https://vuejs.org/
.. _Bootstrap: https://getbootstrap.com/
.. _Django: https://www.djangoproject.com/
