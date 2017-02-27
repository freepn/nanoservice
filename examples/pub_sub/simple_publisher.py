from nanoservice import Publisher
import time

p = Publisher('ipc:///tmp/pubsub-service.sock')

# Need to wait a bit to prevent lost messages
time.sleep(0.001)

p.publish('log_line', 'hello world')
p.publish('cap_line', 'this is uppercase')
