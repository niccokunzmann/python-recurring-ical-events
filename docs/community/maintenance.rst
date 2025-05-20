
Maintenance
===========

This sets you up for maintenance.

New Releases
------------

You can build the new release by running this command:

.. code-block:: shell

    tox -e build

To release new versions,

1. Edit the Changelog Section.
2. Create a commit and push it.
3. Wait for `GitHub Actions <https://github.com/niccokunzmann/python-recurring-ical-events/actions>`_ to finish the build.
4. Run

   .. code-block:: shell

       git tag v3.5.1
       git push origin v3.5.1

5. Notify the issues about their release.
