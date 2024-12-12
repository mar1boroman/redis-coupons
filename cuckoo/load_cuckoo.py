import redis
import os
from dotenv import load_dotenv
load_dotenv()

r = redis.Redis(host=os.environ.get('host'), port=os.environ.get('port'), decode_responses=True)
p = r.pipeline()

r.flushdb()
r.cf().reserve(key='unused_coupons', capacity=1000000)

def load_unused_coupons(no_of_coupons):
    coupon_ids = [f"coupon:{x}" for x in range(no_of_coupons)]
    for id in coupon_ids:
        p.cf().add('unused_coupons', id)
    p.execute()
    print(f"All coupons loaded successfully")
    

if __name__ == '__main__':
    load_unused_coupons(no_of_coupons=100)
    