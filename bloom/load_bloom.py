import redis
import os
from dotenv import load_dotenv
load_dotenv()

r = redis.Redis(host=os.environ.get('host'), port=os.environ.get('port'), decode_responses=True)
p = r.pipeline()

r.flushdb()
r.bf().reserve(key='users',errorRate=0.001, capacity=1000000)

def load_existing_users(no_of_users):
    user_ids = [f"user:{x}" for x in range(no_of_users)]
    for id in user_ids:
        p.bf().add("users", id)
        p.hset(name=id, mapping={'id' : id, 'coupon' : 'Expired', 'no_of_logins' : 1})
    p.execute()
    print(f"All users loaded successfully")

if __name__ == '__main__':
    load_existing_users(no_of_users=10000)
    


