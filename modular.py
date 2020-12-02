
import time

while True:
    try:
        ipp = "test"
        res = req.get("https://ip-share.herokuapp.com/set-public-ip/{}".format(ipp))
        print(res.text)
    except Exception:
        print("Hit an exception, continuing")
    time.sleep(60)
