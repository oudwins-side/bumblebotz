from bumblebot.session import Session
import time

def main():
    session = Session("C:\\Users\\pc\\AppData\\Local\\Google\\Chrome\\User Data\\Default")

    session.set_custom_location(latitude=40.411189, longitude=-3.708250)

    time.sleep(10)

    sleep = {
        "min": 4,
        "max": 12
    }
    session.like(amount=100, ratio="75%", sleep=sleep)



if __name__ == "__main__":
    main()