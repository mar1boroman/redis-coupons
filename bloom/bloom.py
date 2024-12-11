import redis
import random
import time
import os
from dotenv import load_dotenv
from multiprocessing import Process
load_dotenv()


r = redis.Redis(host=os.environ.get('host'), port=os.environ.get('port'), decode_responses=True)
p = r.pipeline()


def check_user(userid):
    is_present = r.bf().exists(key="users", item=userid)
    
    # If the user is not present, assign coupon & initialize profile
    if not is_present:
        print(f"New User : {userid}")
        p.hset(name=userid, mapping={'id' : userid, 'coupon' : 'first_time_user', 'no_of_logins' : 1 })
        
        # Add the new user to the Bloom filter
        p.bf().add("users", userid)

    # If the user is present, increment the number of logins
    else:
        print(f"Existing User : {userid}")
        p.hincrby(name=userid, key='no_of_logins', amount=1)

    p.execute()


def run_app(time_duration):
    start_time = time.time()
    while time.time() - start_time < time_duration:
        check_user(userid=f"user:{random.randint(0, 1000000)}")
    
    
def parallel_execution(time_duration):
    processes = []
    for _ in range(25):
        process = Process(target=run_app, args=[time_duration,])
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
    
if __name__ == "__main__":
    parallel_execution(time_duration=60)
