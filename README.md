# Nuffle Blood Bowl Web Manager

## Summary

The Nuffle Blood Bowl Web Manager is a web based system for tracking
teams or running a league for the Blood Bowl game created by Games
Workshop.

The Blood Bowl web manager is a self contained web server. It's
implemented in Python using CherryPy and SQLObject. To use the Blood
Bowl web manager you launch the web server, and then any number of
people can connect to the Blood Bowl manager using a standard web
browser. It's just like accessing any other website on the Internet.

## What You Need

Python >=2.4: The web manager is implemented in Python. You want
at least version 2.4. Earlier versions most definitely will not work
without some amount of hackery, as function decorators (see PEP 318)
were used in the implementation.

MySQL and MySQLdb --OR-- Postgres and psycopg

Both MySQL and Postgres have active installations at large. It might be
possible to run atop other databases, but I haven't tried others. MySQL
is configured out-of-the-box. If you go with Postgres you'll need to
change the db.uri configuration variable within nuffle.cfg (Step 4 below).

MySQLdb and psycopg are Python modules that implement the Python
DBI. This is used for communication between your Nuffle server and the
database. Most installations of Python or your database will install
this for you, so you likely don't need to install this yourself.


## Installation (Linux, Mac OSX, *nix)

1: Download the Nuffle Blood Bowl Web Manager from here:

  http://sourceforge.net/project/showfiles.php?group_id=53815


2: Extract the downloaded file:

    tar xzf nuffle*.tar.gz


3: Create a database for Nuffle. If you're using MySQL, you
want to do something like this:

    shell> mysql -u root -p mysql
    mysql> create user nuffle identified by 'nuffle';

    shell> mysql -u nuffle -p
    mysql> create database nuffle;

--OR--

    createuser nuffle
    createdb -U nuffle nuffle


4: Create your configuration files. Sample configuration files
are provided for you and are located in the root directory for
Nuffle.  Nuffle expects your configuration files to be located in
the root directory for nuffle, so start by copying the samples:

    cp nuffle.cfg.sample nuffle.cfg
    cp cherrypy.cfg.sample cherrypy.cfg

Then, open both of these files and poke around. At the very least you'll
need to replace all references to the "/home/nuffle" directory and replace
it with the location of your personal installation. You also probably want
to ensure that the database configuration options coincide with the Nuffle
database/account that you just created. If you're using Postgres and not
MySQL you'll definitely need to modify the db uri configuration variable.


5: Create the Nuffle schema in your Nuffle database. Assuming
you've managed to configure yourself correctly, just do this:

    python ./src/data.py

The Python "data" module when executed directly will recreate all
of the necessary tables in your database, and install a base set
of starting data (races, skills, etc).

Now create your database indexes:

    mysql -u nuffle -p nuffle < ./bin/createIndexes.sql

--OR--

    psql -U nuffle nuffle < ./bin/createIndexes.sql


6: Launch the web manager:

    python ./src/server.py


7: Open your favorite web browser and navigate to http://localhost:8042/

8: Whew, all done. You should be staring at the frontpage of
your very own Nuffle installation. You'll want to login as user
"nuffle" password "nuffle". Then click on "[Admin]" to begin creating
coaches and teams.

## Installation (Windows)

I don't personally own any Windows computers, so I haven't been able to
try installing the web manager on a Windows machine. There's nothing
platform-specific in the implementation that I know of, so if you do
attempt (and better yet, succeed) at installing on a Windows machine,
please drop me a note about any hiccups along the way.  I'll update this
document with your experience.

Contact Information

Website: http://nuffle.sourceforge.net/
Email: nuffle-developers@lists.sourceforge.net

That's it! Good luck. May all your injuries be Badly Hurt. Don't
hesitate to send me/us an email if you run in to trouble.

Eric Bieschke
oberon7@users.sourceforge.net
