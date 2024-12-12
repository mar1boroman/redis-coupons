import redis
import os
from dotenv import load_dotenv
import threading
load_dotenv()
r = redis.Redis(host=os.environ.get('host'), port=os.environ.get('port'), decode_responses=True)
p = r.pipeline()
r.flushdb()


def load_products():
    p.hset(name='product:1', mapping={
        'name' : 'Veg Burger',
        'price' : 15
    })
    p.hset(name='product:2', mapping={
        'name' : 'Fries',
        'price' : 5
    })
    p.execute()
    

# Lua script to dynamically change cart order
lua_script = """
    local cartKey = KEYS[1]
    local hasVegBurger = redis.call('HEXISTS', cartKey, 'Veg Burger') == 1
    local hasFries = redis.call('HEXISTS', cartKey, 'Fries') == 1

    if hasVegBurger and hasFries then
        redis.call('HSET', cartKey, 'Coffee (Free)', 0)
    else
        redis.call('HDEL', cartKey, 'Coffee (Free)')
    end

    return redis.call('HGETALL', cartKey)
    """
    
# Load the script into Redis
lua_script_sha = r.script_load(lua_script)



def update_cart_service(cart_key, event_stream):
    """
    Continuously listens to the Redis stream and processes events.
    """
    while True:
        # Listen for new events in the stream
        resp = r.xread(streams={event_stream: '$'}, block=0)
        ts, payload = resp[0][1][0]
        action = payload['action']
        product = payload['item']
        
        item_details = r.hgetall(name=product)
        name = item_details['name']
        price = item_details['price']
        
        if action == 'add':
            r.hset(
                name=cart_key,
                mapping={name:price}
            )
        else:
            r.hdel(cart_key, name)
            
        r.evalsha(lua_script_sha, 1, cart_key)
        print(f"Cart Updated!")


def capture_events(event_stream, event_type, key_name):
    """
    Captures user events and adds them to the Redis stream.
    """
    r.xadd(name=event_stream, fields={
        'action': event_type.lower(),
        'item': key_name
    })
    print(f"Capture Events: Event captured - action: {event_type.lower()}, item: {key_name}")
    

def main():
    """
    Main function to handle user input and start threads.
    """
    load_products()
    cart_key = 'cart'
    event_stream = 'event_stream'

    # Start the update_cart_service in a separate thread
    update_cart_thread = threading.Thread(target=update_cart_service, args=(cart_key, event_stream), daemon=True)
    update_cart_thread.start()

    print("Cart service is running...")

    while True:
        # Capture user input
        event_type = input("\nADD/DELETE? => \n").strip()
        key_name = input("\nPRODUCT KEY => \n").strip()

        # Call capture_events for each user input
        capture_events(event_stream, event_type, key_name)

if __name__ == '__main__':
    main()