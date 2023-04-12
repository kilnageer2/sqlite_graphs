#! /usr/bin/python3


import sqlite3
from sqlite3 import Error
import datetime
import time
import matplotlib.pyplot as plt
import sys

debug = False
graphDisplay = True

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_all_tasks(conn, y, m, d, h, t, p):
    """
    Query all rows in the extension_powerNow table
    :param conn: the Connection object
    :return:
    """
    if debug: print ("y=",y, " m=",m, " d=",d, " h=",h, " t=",t, " p=",p)
    cur = conn.cursor()
    #cur.execute("SELECT * FROM extension_powerNow")
    cur.execute("SELECT * FROM "+t)

    ms=str(m)
    if (m<10): ms= "0"+ms
    ds=str(d)
    if (d<10): ds= "0"+ds
    hs=str(h)
    if (h<10): hs= "0"+hs

    if (p == "Day"):
      match=str(y)+"-"+ms+"-"+ds
      #print("match="+match+" y="+str(y)+" d="+ds+" m="+ms)
    elif (p == "Hour"):
      match=str(y)+"-"+ms+"-"+ds+" "+hs
    elif (p == "Month"):
      # We only want to remember last entry per day for "Month" charts
      d = 1
      match=str(y)+"-"+ms+"-"
      print( "Month d=",d," and match="+match)
    else:
      print("Only Day and Hour supported")
      exit(-2)
    print("Searching all database entries for \""+match+"\"")


    # Read the entire table into list of tuples
    rows = cur.fetchall()

    count=0

    last_usage = 0                     # Should never be used
    last_ts2   = '2023-01-23 23:00:30' # Should never be used

    for row in rows:
        #i = i + 1
        # ticks = 52707330000
        #d = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds = row//10)
        row_ticks = int( row[0] / 1000 )
        usage = row[1]
        ts1 = str(datetime.datetime.fromtimestamp(row_ticks, tz=None))
        if (match in ts1):
          count=count+1
          if (p == "Hour"):
              #print("match="+ts1)
              y_l.append( usage )
              ts2 = str(datetime.datetime.fromtimestamp(row_ticks, tz=None))
              x.append( ts2 )
              #print( "( "+ts2+", "+str(usage)+" ),")
          if (p == "Day"):
              #print("match="+ts1)
              y_l.append( usage )
              ts2 = str(datetime.datetime.fromtimestamp(row_ticks, tz=None))
              x.append( ts2 )
              #print( "( "+ts2+", "+str(usage)+" ),")
          if (p == "Month"):
              ts2 = str(datetime.datetime.fromtimestamp(row_ticks, tz=None))
              same_month = (match in ts2)  # e.g "2023-01" in "2023-01-23 23:01:30"
              # We want to process every day in this month
              if (same_month) :
                  #print( "Same month d=",d," and match="+match)
                  ds=str(d)
                  if (d<10): ds= "0"+ds
                  match2 = match+ds
                  same_day = (match2 in ts2) # e.g "2023-01-02" in "2023-01-02 23:01:30"
                  if (same_day) :
                      #print( "Same day d=",d," and match2="+match2)
                      last_usage = usage
                      last_ts2   = ts2  
                      #print( "current time and usage values for day ",d," are ", last_ts2, " and ", last_usage )
                      #continue # skip this fella
                  else:
                      #print( "Different day d=",d," and match2="+match2)
                      # Let's move on to the next day
                      d = d + 1

                      # But save to array the last values from the current day
                      y_l.append( last_usage )
                      x.append( last_ts2 )
                      #print( "last time and usage values for day ",d," are ", last_ts2, " and ", last_usage )
                      if (d > 31): break
              else:
                  # All done so don't process any more values
                  break


    print( count, "matches found")


def main():

    n = len(sys.argv)
    if debug: print( "Number of arguments: " + str(n) + " arguments." )
    if debug: print( "Argument List: " + str(sys.argv) )

    # So how many ways will we use this?
    # 1) 2022 09 10 21 house    - gets that hour's usage
    # 2) 2022 09 10 extension   - gets that day's usage
    # 3) 2022 09 extension      - gets that month's usage
    # 4) 2022 08 extension      - gets previous month's usage
    if ((n < 4) or (n > 6)): 
        print( "Usage:  specify a date/hour and type i.e. " + str(sys.argv[0]) + " 2022 07 {22} {10} [house | extension]" )
        print( "NOTE: day and hour are optional and used to generate the daly and hourly respectively" )
        exit( -1 )

    year  = int(sys.argv[1])
    month = int(sys.argv[2])
    day   = 0
    hour  = 0
    if (n == 4):
      where = sys.argv[3]
      period = "Month"
      xLabelGraph = "Days 1 to 31"
      yLabelGraph =" Units in Watts (W)"
      titleGraph  = "Electricity Usage by "+where+" for month "+str(month)+"/"+str(year)
    elif (n == 5):
      day   = int(sys.argv[3])
      where = sys.argv[4]
      period = "Day"
      xLabelGraph = "Hours 00:00 to 23:00"
      yLabelGraph =" Units in Watts (W)"
      titleGraph  = "Electricity Usage by "+where+" for day "+str(day)+"/"+str(month)+"/"+str(year)
    elif (n == 6):
      day   = int(sys.argv[3])
      hour  = int(sys.argv[4])
      where = sys.argv[5]
      period = "Hour"
      xLabelGraph = "Minutes 0 to 59"
      yLabelGraph =" Units in Watts (W)"
      titleGraph  = "Electricity Usage by "+where+" for "+str(hour)+":00 hour on "+str(day)+"/"+str(month)+"/"+str(year)

    # Now lets check these values!
    if (year < 2020):
        print( "ERROR: Only greater than 2020 allowed as year and not "+year )
        exit(-1)

    if (day > 31):
        print( "ERROR: Day must not be more than 31 and not "+day )
        exit(-1)

    if (hour > 23):
        print( "ERROR: Hour must be 0 to 23 and not "+day )
        exit(-1)

    if (where == "house"):
        if (period == "Month"):
            table = "house_powerToday"
        else:
            table = "house_powerNow"
            #table = "house_powerToday"

    elif (where == "extension"):
        if (period == "Month"):
            table = "extension_powerToday"
        else:
            table = "extension_powerNow"
            #table = "extension_powerToday"
    else:
        print( "ERROR: Where must be house or extension and not "+where )
        exit(-1)


    #database = r"C:\sqlite\db\pythonsqlite.db"
    database = r"/home/pi/node-red-sqlite.db"

    print( "Using table: "+table+" from SQlite database: "+database )

    # create a database connection
    conn = create_connection(database)
    with conn:
        if debug: print("Query all records in database")
        select_all_tasks(conn, year, month, day, hour, table, period)

        if debug: print( y_l )

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    #ax.plot([1, 2, 3, 4])
    #ax.set(xlabel=xLabelGraph, ylabel=yLabelGraph, title=titleGraph)
    ax.set(xlabel=xLabelGraph, title=titleGraph)
    ax.set_ylabel("W (Discrete)",color="blue",fontsize=14)
    #l1 =ax.plot( plot_tuples )
    #l1 =ax.plot( acc )

    #ax.plot( x, plot_tuples, color="blue", marker="o" )
    x2 = [datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in x]
    ax.plot( x2, y_l, color="blue", marker="o" )

    #ax.legend((l1), ('instant', 'accumulated'), loc='best', shadow=True)
    #ax.legend((l1), ('accumulated'), loc='best', shadow=True)
    #plt.ylabel('Average and Accumulated Power (W) Used by the Extension')
    #plt.xlabel('Hours of the day 0 (00:00) to 23 (23:00)')

    #fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    #ax.plot([0,1,2], [10,20,3])
    #fig.savefig('path/to/save/image/to.png')   # save the figure to file
    #plt.close(fig)    # close the figure window

    # twin object for two different y-axis on the sample plot
    #ax2=ax.twinx()
    #ax2.set_ylabel("Wh (Discrete)",color="orange",fontsize=14)
    #ax2.plot( now, color="orange", marker="o" )
    #ax2.legend((l2), ('instant'), loc='best', shadow=True)

    #https://stackoverflow.com/questions/1574088/plotting-time-in-python-with-matplotlib
    plt.gcf().autofmt_xdate()

    fig.savefig("/home/pi/graphs/"+where+period+"_detailed.png")   # save the figure to file
    if graphDisplay: plt.show()

    plt.close(fig)    # close the figure window

    #plt.show()





y_l = []  # discrete values
x   = []  # timestamps

if __name__ == '__main__':
    main()




