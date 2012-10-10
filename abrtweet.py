#!/usr/bin/env python
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import os
import twitter

CONSUMER_KEY = 'e4rijwXyDxN2y9Hmig8mA'
CONSUMER_SECRET = '0yBUkL9Ocd2xqPDTgKWQBztqeK7t0YG1EsS70pGqua4'.swapcase()
ACCESS_TOKEN_KEY = 'YOUR_KEY'
ACCESS_TOKEN_SECRET = 'YOUR_SECRET'

def handle_crash(package, dump, uid):
    # Ensure that bad packages can't hide by just being the most frequent to crash
    for f in ('core_backtrace', 'uuid'):
        try:
            os.rename(os.path.join(dump, f), os.path.join(dump, f + '.bak'))
        except OSError:
            pass

    # Construct a helpful tweet
    with open(os.path.join(dump, 'reason')) as f:
        reason = f.read()
    with open(os.path.join(dump, 'pkg_name')) as f:
        package = f.read()
    with open(os.path.join(dump, 'time')) as f:
        timestamp = f.read()
    tweet = "%s #%s #crash %s" % (reason, package, timestamp)

    # Share it with the world
    twitter_api.PostUpdate(tweet)

def main():
    # Connect to twitter
    global twitter_api
    twitter_api = twitter.Api(consumer_key = CONSUMER_KEY,
                              consumer_secret = CONSUMER_SECRET,
                              access_token_key = ACCESS_TOKEN_KEY,
                              access_token_secret = ACCESS_TOKEN_SECRET)

    # Set up DBus main loop
    DBusGMainLoop(set_as_default=True)

    # Connect to system DBus and listen for crash events
    bus = dbus.SystemBus()
    bus.add_signal_receiver(handle_crash, dbus_interface = 'com.redhat.abrt', signal_name = 'Crash')

    # Enter event loop
    loop = gobject.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
