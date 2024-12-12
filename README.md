
# Scenario 1:  Bloom Filters

#### Create the index

```
FT.CREATE idx:users
    ON HASH 
    PREFIX 1 user:
    SCHEMA
        id as id TEXT
        coupon as coupon TAG
        no_of_logins NUMERIC
```

#### Find the number of existing users

```
FT.AGGREGATE  idx:users @coupon:{Expired}
    APPLY "upper('Existing Users')" as existing
    GROUPBY 1 @existing
    REDUCE COUNT_DISTINCT 1 @id as Total
    DIALECT 4
```

#### Find all users who were the existing users

```
FT.SEARCH idx:users @coupon:{Expired}
```


#### Find all the NEW users who have logged in only once

```
FT.SEARCH idx:users "@coupon:{first_time_user} @no_of_logins:[1,1]"
```

```
FT.AGGREGATE idx:users "@no_of_logins:[1,1]"
    APPLY "upper('Only Once Login')" as only_once
        GROUPBY 1 @only_once
        REDUCE COUNT 0 AS COUNT
```

#### Find the top 5 most active users

```
FT.SEARCH idx:users "@coupon:{first_time_user}" SORTBY no_of_logins DESC LIMIT 0 5
```

# Scenario 2 : All applicable coupons

```
FLUSHDB
```

#### Set the coupon metadata

```
HSET coupon:1 name COUPON10 value 10 category Books
HSET coupon:2 name ELECTRO50 value 20 category Electronics
HSET coupon:3 name BANK50 value 50 category BANK1
```

#### Set the cart metadata

```
HSET cart Electronics 10 Books 5 Fashion 15 Payment BANK1
```

#### Create index based on coupons & Search for relevant coupons based on cart items

```
FT.CREATE idx:coupons
    ON HASH PREFIX 1 coupon:
    SCHEMA 
        name as name TAG
        value as value NUMERIC
        category as category TAG
```

```
FT.INFO idx:coupons
```

```
FT.SEARCH idx:coupons "@category:{Electronics}"
```
