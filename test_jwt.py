import jwt
import datetime
import time


key = "secret"
encoded = jwt.encode({"exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=30)}, key, algorithm="HS256")

print(encoded)


decoded = jwt.decode(encoded, key, algorithms="HS256")

print(decoded)





# jwt_payload = jwt.encode(
#     {"exp": datetime.datetime.utcnow() + }, "secret"
# )

# time.sleep(32)

# # JWT payload is now expired
# # But with some leeway, it will still validate
# jwt.decode(jwt_payload, "secret", leeway=10, algorithms=["HS256"])