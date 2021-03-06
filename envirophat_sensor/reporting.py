import redis
import socket

class Reporter:
    def __init__(self, host, port, quiet):
       self.host = host
       self.port = port

       self.name = socket.getfqdn()
       self.live_expiry = 30
       self.quiet = quiet

    def get_name(self):
        return self.name

    def get_key(self, key):
        return self.client.get(key)

    def set_live(self):
        self.overset_expiring_key("live", "1", self.live_expiry)

    def delete_key(self, key):
        self.client.delete(key)

    def announce(self):
        self.client = redis.StrictRedis(host=self.host, port=self.port, db=0)
        self.set_live()
        self.client.hset("members", self.name, "1")
        self.client.publish("members.add", self.name)

    def set_key(self, key, value):
        if(self.quiet == False):
            print(key, value)

        self.client.set(self.name+"."+key, round(value, 2))

    def overset_expiring_key(self, key, value, timeout):

        self.client.set(self.name+"."+key, value)
        self.client.expire(self.name+"."+key, timeout)  

    def set_expiring_key(self, key, value, timeout):
        if(self.quiet == False):
            print(key, value, timeout)

        exists = self.client.get(self.name+"."+key)
        if(exists==None):
            if(self.quiet == False):
                print(key+ ", value=" + str(value))
            self.client.set(self.name+"."+key, value)
            self.client.expire(self.name+"."+key, timeout)

    def set(self, values):
        self.set_live()

        self.set_key("temp", values["temp"])
        self.set_expiring_key("temp.baseline", round(values["temp"], 2), 300)

        self.overset_expiring_key("motion", values["motion"], 5)


    def publish(self):
        self.client.publish("sensors.data", self.name)
