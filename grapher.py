#! /usr/bin/python3

import datetime
import time
import sys
import subprocess

debug = True



def main():

  while True:
    # Always ue this as it takes care of DST !
    now_struct_time = time.localtime()
    #now_struct_time = passed_in_time
    print ("Current local time as struct_time: ");
    print (now_struct_time) 
    # time.struct_time(tm_year=2022, tm_mon=9, tm_mday=8, tm_hour=13, tm_min=9, tm_sec=14, tm_wday=3, tm_yday=251, tm_isdst=0)
    year  = now_struct_time[0]
    month = now_struct_time[1]
    day   = now_struct_time[2]
    hour  = now_struct_time[3]

    # So how many ways will we use this?
    # 1) 2022 09 10 21 house    - gets that hour's usage
    # 2) 2022 09 10 extension   - gets that day's usage
    # 3) 2022 09 extension      - gets that month's usage
    # 4) 2022 08 extension      - gets previous month's usage

    if (month >1):
      lastMonth = month - 1
      lastYear = year
    else:
      lastMonth = 12
      lastYear = year - 1

    for where in ( "house", "extension" ):
      subprocess.run("/home/pi/graphs/createElectrictyGraph.py "+str(lastYear)+" "+str(lastMonth)+" "+where, shell=True)
      subprocess.run("mv /home/pi/graphs/"+where+"Month.png /home/pi/graphs/"+where+"LastMonth.png", shell=True )
      subprocess.run(["/home/pi/graphs/createElectrictyGraph.py", str(year), str(month), str(day), str(hour), where ])
      subprocess.run(["/home/pi/graphs/createElectrictyGraph.py", str(year), str(month), str(day), where ])
      subprocess.run(["/home/pi/graphs/createElectrictyGraph.py", str(year), str(month), where ])

    subprocess.run("ls -al /home/pi/graphs/*.png", shell=True )

    subprocess.run("cp /home/pi/graphs/*.png /var/www/html", shell=True)
    subprocess.run("scp /var/www/html/* pi@192.168.1.108:/var/www/html", shell=True)
    time.sleep( 10*60 ) # 10 mins

if __name__ == '__main__':
    main()




