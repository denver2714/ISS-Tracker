import requests
from datetime import datetime
import smtplib
import time

class ISSNotifier:
    def __init__(self, email, password, latitude, longitude):
        self.email = email
        self.password = password
        self.latitude = latitude
        self.longitude = longitude

    def is_iss_overhead(self):
        response = requests.get(url="http://api.open-notify.org/iss-now.json")
        response.raise_for_status()
        data = response.json()

        iss_latitude = float(data["iss_position"]["latitude"])
        iss_longitude = float(data["iss_position"]["longitude"])

        if self.latitude-5 <= iss_latitude <= self.latitude+5 and self.longitude-5 <= iss_longitude <= self.longitude+5:
            return True
        return False

    def is_night(self):
        parameters = {
            "lat": self.latitude,
            "lng": self.longitude,
            "formatted": 0,
        }
        response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
        response.raise_for_status()
        data = response.json()
        sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
        sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

        time_now = datetime.now().hour

        if time_now >= sunset or time_now <= sunrise:
            return True
        return False

    def notify(self):
        if self.is_iss_overhead() and self.is_night():
            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(self.email, self.password)
                connection.sendmail(
                    from_addr=self.email,
                    to_addrs=self.email,
                    msg="Subject:Look Up👆\n\nThe ISS is above you in the sky."
                )

    def run(self):
        while True:
            time.sleep(60)
            self.notify()


# Usage
MY_EMAIL = "kurtdenverchavez2005@gmail.com"
MY_PASSWORD = "(*MY PASSWORD*)"
MY_LAT = 14.625483  # Your latitude
MY_LONG = 121.124481  # Your longitude

notifier = ISSNotifier(MY_EMAIL, MY_PASSWORD, MY_LAT, MY_LONG)
notifier.run()
