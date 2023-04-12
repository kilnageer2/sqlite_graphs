#! /usr/bin/python3


import sqlite3
from sqlite3 import Error
import datetime
import time
import matplotlib.pyplot as plt
import sys

debug = True
debug2 = True
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


    passed_in_time = (y,m,d,  h,0,0,   0,0,0)

    # Always ue this as it takes care of DST !
    #now_struct_time = time.localtime()
    now_struct_time = passed_in_time
    if debug: print ("Current local time as struct_time: ");
    if debug: print (now_struct_time) 
    # time.struct_time(tm_year=2022, tm_mon=9, tm_mday=8, tm_hour=13, tm_min=9, tm_sec=14, tm_wday=3, tm_yday=251, tm_isdst=0)
    year  = now_struct_time[0]
    month = now_struct_time[1]
    day   = now_struct_time[2]
    hour  = now_struct_time[3]

    ticks_per_min  = 60 
    ticks_per_hour = 60 * ticks_per_min
    ticks_per_day  = 60 * ticks_per_hour

    if (p == "Day"):
      first = (year, month, day,  0, 0,0, 0,0,0)
      first_ticks = int(time.mktime(first))
      tick_step = ticks_per_hour
      tick_end  = first_ticks + tick_step
      steps_max = 23
      if debug: print ("First ticks: ", first_ticks)

      last = (year, month, day,  23, 59,59, 0,0,0)
      last_ticks = int(time.mktime(last))
      if debug:  print ("Last ticks:  ", last_ticks)

    elif (p == "Hour"):
      first = (year, month, day,  hour, 0,0, 0,0,0)
      first_ticks = int(time.mktime(first))
      tick_step = ticks_per_min
      tick_end  = first_ticks + tick_step
      steps_max = 59
      if debug: print ("First ticks: ", first_ticks)

      last = (year, month, day,  hour, 59,59, 0,0,0)
      last_ticks = int(time.mktime(last))
      if debug:  print ("Last ticks:  ", last_ticks)

    elif (p == "Month"):
      first = (year, month, 0,  0, 0,0, 0,0,0)
      first_ticks = int(time.mktime(first))
      tick_step = 24 * ticks_per_hour
      tick_end  = first_ticks + tick_step
      steps_max = 30
      if debug: print ("First ticks: ", first_ticks)

      last = (year, month, 31,  23, 59,59, 0,0,0)
      last_ticks = int(time.mktime(last))
      if debug:  print ("Last ticks:  ", last_ticks)

    else:
      print("To be finished...")
      exit(-2)

    # Read the entire table into list of tuples
    rows = cur.fetchall()

    #i = 0
    steps = 0
    graph_total = 0
    step_total = 0
    step_count = 0
    hour_total = 0
    for row in rows:
        #i = i + 1
        # ticks = 52707330000
        #d = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds = row//10)
        #   values( "+ timestamp +"," + battery +"," + Vbat + "," + Ibat + "," + capacity +")";
        row_ticks     = int( row[0] / 1000 )
        room          = row[1]
        battery       = row[2]
        temperature   = int( row[3] / 100 )
        if debug2: print( "Ticks="+str(row_ticks)+" room:"+str(room)+" batt="+str(battery)+" temperature="+str(temperature/100)+"C" )

        '''
        if ((row_ticks >= first_ticks) and (row_ticks <= last_ticks)):
          #print( ticks, usage )
          dt = datetime.datetime.fromtimestamp( row_ticks )
          print(row_ticks, dt, usage)
          #print(row)
          i = i + 1
          #if (i == 5): break
        '''
        if (row_ticks > tick_end):
          step_average = 0
          if (step_count > 0): step_average = int(step_total / step_count)
          #plot_tuples.append( (steps, step_average, graph_total) )
          if (p == "Hour"):
            #plot_tuples.append( (steps, step_average, graph_total) )
            #plot_tuples.append( (step_average, graph_total) )
            plot_tuples.append( step_average )
            # Four KWh we only calculate value at end of the hour :)
            hour_total = hour_total + step_average
          if (p == "Day"):
            #plot_tuples.append( (""+str(steps)+":00", step_average, graph_total) )
            #plot_tuples.append( (steps, step_average, graph_total) )
            #plot_tuples.append( ((steps), (step_average, graph_total)) )
            #plot_tuples.append( (step_average, graph_total) )
            plot_tuples.append( step_average )
            graph_total = graph_total + step_average
          if (p == "Month"):
            #plot_tuples.append( (steps+1, (24 * step_average), graph_total)  )
            #plot_tuples.append( ((24 * step_average), graph_total)  )
            plot_tuples.append( 24 * step_average )
            graph_total = graph_total + (24 *step_average)
          if debug: print(steps, step_total, step_count, step_average)
          if debug: print("end of step  #"+str(steps), "ave="+str(step_average), "total="+str(graph_total) )
          tick_end = tick_end + tick_step
          steps = steps + 1
          step_total = 0
          step_count = 0
          if (steps > steps_max): 
              break

        if ((row_ticks >= first_ticks) and (row_ticks <= tick_end)):
          #print( ticks, usage )
          #dt = datetime.datetime.fromtimestamp( row_ticks )
          #print(row_ticks, dt, usage)
          step_total = step_total + temperature
          step_count = step_count + 1
          #print(row)
          #if (i == 5): break

    if (p == "Hour"):
      # Four KWh we only calculate value at end of the hour :)
      #graph_total = graph_total + step_average
      if debug: print("end of step  #"+str(steps), "ave="+str(step_average), "total="+str(int(hour_total/60)) )
      #plot_tuples.append( (steps, step_average, int(hour_total/60)) )
      #plot_tuples.append( (step_average, int(hour_total/60)) )
      plot_tuples.append( step_average )


def main():

    n = len(sys.argv)
    if debug: print( "Number of arguments: " + str(n) + " arguments." )
    if debug: print( "Argument List: " + str(sys.argv) )

    # So how many ways will we use this?
    # 1) 2022 09 10 21 - gets that hour's charging/SOC
    # 2) 2022 09 10    - gets that day's charging/SOC
    # 3) 2022 09       - gets that month's charging/SOC
    # 4) 2022 08       - gets previous month's charging/SOC
    if ((n < 3) or (n > 5)): 
        print( "Usage:  specify a date/hour and type i.e. " + str(sys.argv[0]) + " 2022 07 {22} {10} " )
        print( "NOTE: day and hour are optional and used to generate the daly and hourly respectively" )
        exit( -1 )

    year  = int(sys.argv[1])
    month = int(sys.argv[2])
    day   = 0
    hour  = 0
    where = "Room_Temperatures"

    if (n == 3):
      #where = sys.argv[3]
      period = "Month"
      xLabelGraph = "Days 1 to 31"
      yLabelGraph =" Charge(+)/Discharge(-) in Watts (W)"
      titleGraph  = "Battery Charging/SOC for month "+str(month)+"/"+str(year)
    elif (n == 4):
      day   = int(sys.argv[3])
      #where = sys.argv[4]
      period = "Day"
      xLabelGraph = "Hours 00:00 to 23:00"
      yLabelGraph =" Temperature in Celcius (C)"
      titleGraph  = "Room temperatues for day "+str(day)+"/"+str(month)+"/"+str(year)
    elif (n == 5):
      day   = int(sys.argv[3])
      hour  = int(sys.argv[4])
      #where = sys.argv[5]
      period = "Hour"
      xLabelGraph = "Minutes 0 to 59"
      yLabelGraph =" Temperature in Celcius (C)"
      titleGraph  = "Room Temperatures for "+str(hour)+":00 hour on "+str(day)+"/"+str(month)+"/"+str(year)

    # Now lets check these values!
    if (year != 2023):
        print( "ERROR: Only 2022 allowed as year and not "+year )
        exit(-1)

    if (day > 31):
        print( "ERROR: Day must not be more than 31 and not "+day )
        exit(-1)

    if (hour > 23):
        print( "ERROR: Hour must be 0 to 23 and not "+day )
        exit(-1)

    # Below id from Node-Red code:
    # msg="(timestamp, room, battery, temperature) 
    #             values( "+ timestamp +"," + room +"," + battery + "," + temperature +")";
    # Battery is in mV and temperature stored is in C x100

    #database = r"C:\sqlite\db\pythonsqlite.db"
    database = r"/home/pi/node-red-sqlite.db"
    table = "zigbee_data"

    # create a database connection
    conn = create_connection(database)
    with conn:
        if debug: print("Query all table:"+table+" records in database")
        select_all_tasks(conn, year, month, day, hour, table, period)

        if debug: print( plot_tuples )

    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    #ax.plot([1, 2, 3, 4])
    ax.set(xlabel=xLabelGraph, ylabel=yLabelGraph, title=titleGraph)
    l1 =ax.plot( plot_tuples )
    #ax.legend((l1), ('instant', 'accumulated'), loc='best', shadow=True)
    ax.legend((l1), ('instant' ), loc='best', shadow=True)
    #plt.ylabel('Average and Accumulated Power (W) Used by the Extension')
    #plt.xlabel('Hours of the day 0 (00:00) to 23 (23:00)')

    #fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    #ax.plot([0,1,2], [10,20,3])
    #fig.savefig('path/to/save/image/to.png')   # save the figure to file
    #plt.close(fig)    # close the figure window

    #fig.savefig("/home/pi/graphs/"+where+period+".png")   # save the figure to file
    fig.savefig("/home/pi/graphs/"+where+period+".png")   # save the figure to file
    if graphDisplay: plt.show()

    plt.close(fig)    # close the figure window

    #plt.show()





plot_tuples = [ ]

if __name__ == '__main__':
    main()




