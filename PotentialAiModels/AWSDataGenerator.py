import subprocess
#import sys
#from datetime import date
#from time import sleep
import random

#today = date.today()
#print("Today's date:", today)

#subprocess.run(["python3"])
#subprocess.run(["ls"])
#subprocess.run([sys.executable, "-c", "print('Todays date:')"])
#subprocess.run(["quit()"])

#from datetime import datetime

# datetime object containing current date and time
#now = datetime.now()

#print("now =", now)


# dd/mm/YY H:M:S
#dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#hour = now.strftime("%S.%f")
#print(hour)
#print("date and time =", dt_string)
#sleep(0.05)


#for _ in range(3):
    #now = datetime.now()
    #seconds = int(now.strftime("%S")) + 0.000001 * int(now.strftime("%f"))
    #print(seconds)
    #sleep(60 - seconds)
    #print("do stuff", now)
for loop in range(2):
    for i in range(10):
        datalist = []

        for datanumber in range(60):
            datalist.append(random.randint(i, (i * 2) + 1))

        statistics = f"Sum={sum(datalist)},Minimum={min(datalist)},Maximum={max(datalist)},SampleCount={len(datalist)}"

        minutes = loop*10 + i
        if minutes < 10:
            minutes = str(0) + str(minutes)
        else:
            minutes = str(minutes)
        date = "2021-02-22T08:" + minutes + ":00.000Z"

        if False:
            print(["aws cloudwatch put-metric-data " +
                "--metric-name " + "PageViewCount " +
                "--namespace " + "MyService " +
                "--statistic-values " + str(statistics) +
                " --timestamp " + str(date)
            ])
        else:
            subprocess.run(["aws cloudwatch put-metric-data " +
                "--metric-name " + "PageViewCount " +
                "--namespace " + "MyService " +
                "--statistic-values " + str(statistics) +
                " --timestamp " + str(date)
            ])
