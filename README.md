

# Searching

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