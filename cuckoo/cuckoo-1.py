import redis
import random
import time
import os
from dotenv import load_dotenv
from multiprocessing import Process
load_dotenv()


r = redis.Redis(host=os.environ.get('host'), port=os.environ.get('port'), decode_responses=True)
p = r.pipeline()


def check_coupon(couponid):
    is_present = r.cf().exists(key="unused_coupons", item=couponid)
    
    # If the coupon is not present, mark this as fraud alert
    if not is_present:
        print(f'Attempted reuse / fraud for coupon : {couponid}')
    else:
        print(f"Maybe a valid usage, checking the db..")
        print(f"Coupon validated, deleting the coupon from the cuckoo filter")
        p.cf().delete(key="unused_coupons", item=couponid)

    p.execute()


def main():
    
    coupon_name = input('Enter your coupon code: ')
    check_coupon(coupon_name)
    
    
if __name__ == "__main__":
    main()
