#-------------------------------------------------------------------------------
# Name:        Tracks zero cordinate removing module
# Purpose:
#
# Author:      Obira Daniel
#
# Created:     30/09/2014
# Copyright:   (c) GIS 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#the working directory path
import os,time,datetime,sys,logging #importing the system, operation system and logging modules
dirpath='Z:\Tracking data'
logfile='Tracking.log'
LTPcars=['White Rav 4 UAS 147Z','Blue Double Cabin']
Weconsultcars=['Green Prado-UAL 587V','Grey Double Cabin-UAU 844J','Hardbody-UAH 869V','White double cabin-UAF 368T']
formatstr=""
reqcords=(60*60*24)/60
reqlins=(reqcords*5)+10
trackfolders=['Z:\Tracking data\LTP','Z:\Tracking data\TGS','Z:\Tracking data\We Consult']#['F:\General\Tracking files\GIS data\LTP','F:\General\Tracking files\GIS data\TGS','F:\General\Tracking files\GIS data\We Consult']
copyfolders=['F:\General\Tracking files\GIS data\LTP','F:\General\Tracking files\GIS data\TGS','F:\General\Tracking files\GIS data\We Consult']
dailylogs=['C:\\Users\\GIS\\Documents\\Tracking logs','Z:\\Tracking data\\Logs','F:\\General\\Tracking files\\Logs']
checkedcars=0
uncheckedcars=[]

def isSameCordinate(c1,c2):
    return c1[0]==c2[0]    
def isZero(c1):
    if len(c1)> 1:
        return 'lat="0.000000"' in c1[0]
def getcordinates(c1):
    """Returns numeric values of co-ordinates in (lat,long) format."""
    cords=c1[0].split('"')
    return (float(cords[1]), float(cords[3]))
def isSametime(c1,c2):
    """Checks if two co-ordinates have the same time."""
    return c1[2]==c2[2]
def getimedate(c1):
    """Returns (date, time) tuple for c1 co-ordinate"""
    t=c1[2]
    return (t[6:10]+t[11:13]+t[14:16],t[17:25])
def getspeed(cod):
    """Returns the speed when given a co-ordinate."""
    s=cod[3].split('speed')[1]
    return float(s[1:-2])
def getelevation(c1):
    """Returns the elevation im metres when given a co-rodinate c"""
    el=c1[1].split('>')
    return float(el[1][:-5])
def timerectify(c1):
        t=c1[2]
        c1[2]=t[:16]+'T'+t[17:25]+'Z'+t[25:]
def ReadCordinates(filename):
    """Takes in a gpx file instance and returns a\
    (startime,cods,estcods,actualcods,repeatedcods,zerocods,endtime) tuple."""
    print os.getcwd()+"\\"+filename
    File=file(filename,'r')
    lines=File.readlines()
    estcods=(len(lines)-10)/5.0
    actualcods=0;repeatedcods=0; zerocods=0
    File.close()
    cods=[];i=6;maxno=len(lines)-9
    previous=(lines[i:i+5])
    timerectify(previous)
    if not isZero(previous):
        previous=[previous]
        #startime=getimedate(previous)
        cods+=previous
    else:
        zerocods+=1
    i+=5
    current=lines[i:i+5]
    while i<=maxno:
        current=lines[i:i+5]
        timerectify(current)
        if isZero(current):
            zerocods+=1
        else:
            if not isSameCordinate(current,previous):
                cods+=current
                actualcods+=1
            else:
                repeatedcods+=1
        previous=[current]
        i+=5
        #if (i>=maxno):
         #   endtime=getimedate(previous)
    if not isZero(current):
        cods+=[current]
    else:
        zerocods+=1
    if len(cods)>0:
        startime=getimedate(cods[0])
        endtime=getimedate(cods[-1])
    else:
        startime=endtime='00:00'
    return (startime,cods,estcods,actualcods,repeatedcods,zerocods,endtime)
def writegpx(cods,writefile):
#    if not os.path.exists(writefile):
#        os.makedirs(os.path.dirname(writefile))
    File=file(writefile,'w')
    start='<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n\
<gpx creator="Mobile Action http://www.mobileaction.com/" version="1.0"\
    xmlns="http://www.topografix.com/GPX/1/0" xmlns:xsi="http://www.w3.org/2001\
    /XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/0\
    http://www.topografix.com/GPX/1/0/gpx.xsd">\n<trk>\n<name>201410301\
    445294529</name>\n<desc>Color:004000ff</desc>\n<trkseg>\n'
    end='\n</trkseg>\n</trk>\n</gpx>\n'
    File.write(start)
    for cod in cods:
        File.write(''.join(cod))
    File.write(end)
    File.close()
def readwrite(filename, car):
    if '.gpx' not in filename:
        filename+='.gpx'
    (startime,cods,estcods,actualcods,repeatedcods,zerocods,endtime)=ReadCordinates(filename)
#    (maxspeed,maxspeedtime,avgspeed)=getstats(cods)
    path=os.getcwd()
    print "readwrite "+os.getcwd()
    writepath=(path+'\\'+car+'\GPX'+'\Analysed\\')
    #print writepath,filename+" :WP"
    if not os.path.exists(writepath):
        os.makedirs(os.path.dirname(writepath))
    writegpx(cods,writepath+filename)
    for path in dailylogs:
        os.chdir(path)
        logwrite=file(logfile,'a')
        logwrite.write('\nCAR: '+car+'\n')
        logwrite.write('Current time: '+ time.ctime()+'\n')
        #logwrite.write(path+'\n')
        logwrite.write('Starttime,          Estcods  Actualcods  Repeatedcods  Zerocods            Endtime\n')
        logstring=" ".join(startime)+"   "+str(estcods)+"      "+str(actualcods)+"         "+str(repeatedcods)+"            "+str(zerocods)+"            "+" ".join(endtime)+"\n"
        print startime, endtime
        print logstring +"LOGSTRING."
        logwrite.write(logstring)
        #logwrite.write("___________\n")
        #logwrite.write("Maxspeed: "+str(maxspeed)+", at"+ maxspeedtime+", Avg speed: "+str(avgspeed)+".\n" )
        logwrite.write("______________________\n")
        logwrite.close()
    print "Done, "+ filename+" "+"car"
    os.chdir(path)
        
def getstats(cods):
    """Takes in a co-ordinates list and returns (maxspeed,maxspeedtime,avgspeed)"""
    totalspeed=0.0;speedcounts=0;i=0
    maxno=len(cods)-1
    maxspeed=(None,0)
    while i<=maxno:
        speed=getspeed(cods[i])
        if speed>maxspeed[0]:
            maxspeed=(speed,getimedate(cods[i]))
        if speed>0:
            totalspeed+=speed
            speedcounts+=1
    return (maxspeed[0],maxspeed[1],(totalspeed/speedcounts))
    
def FileBrowse(filename):
    global checkedcars
    global uncheckedcars
    cars=os.listdir('.')
    cars=[i for i in cars if '.' not in i]
    print cars
    cd=os.getcwd()
    for car in cars:
        #os.chdir(car)
        print str(os.getcwd())+"\\"+car+" ,"#+str(filename in gpxfiles)
        gpxfiles=os.listdir(car+'\GPX')
        if filename in gpxfiles:
            #os.chdir(car)
            readwrite(car+'\GPX\\'+filename,car)
            checkedcars+=1
        else:
            uncheckedcars=[car]+uncheckedcars
        os.chdir(cd)
def TracksBrowse(Directory,filename):
    if '.gpx' not in filename:
        filename+='.gpx'
    os.chdir(Directory)
    dlist=os.listdir('.')
    dlist=[i for i in dlist if '.' not in i]
    print dlist
    global checkedcars
    global uncheckedcars
    uncheckedcars=[]
    checkedcars=0
    for path in dailylogs:
        os.chdir(path)
        logwrite=file(logfile,'a')
        logwrite.write('\n\nSTART: Current time:__________'+ time.ctime()+'________________________________________\n')
        logwrite.close()
    if (('LTP' in dlist) and ('TGS' in dlist) and ('We Consult' in dlist)):
        os.chdir(Directory)
        for d in dlist:
            if 'LTP' in d:
                print 'LTP'
                print d+" .."+'D'
                os.chdir(d)
                FileBrowse(filename)
                os.chdir(Directory)
            elif 'TGS' in d:
                print d+" .."+'D'
                os.chdir(d)
                FileBrowse(filename)
                os.chdir(Directory)
            elif 'We' in d:
                os.chdir(d)
                print d+" .."+'D'
                FileBrowse(filename)
                os.chdir(Directory)
            else:
                continue
    else:
        return "Directory lacks some tracking files."
    for path in dailylogs:
        os.chdir(path)
        logwrite=file(logfile,'a')
        logwrite.write("Checked cars: "+str(checkedcars)+"_____.\n")
        logwrite.write("Unchecked cars: "+str(len(uncheckedcars))+"___ "+': '.join(uncheckedcars)+".\n")
        logwrite.write('\n\nEND: Current time:__________'+ time.ctime()+'________________________________________\n')
        logwrite.close()
    print "Checked cars: "+str(checkedcars)+"."
    print "Unchecked cars: ",str(len(uncheckedcars)), uncheckedcars
    checkedcars=0
def avg(values)          :
    return sum(values)/len(values)
            
    
E=file('Z:\Tracking data\TGS Landcruiser1 UAR420E 20140930.gpx','r')
f=E.readlines()
E.close()
c1=f[6:11];c2=f[11:16];c3=f[16:21];c4=f[21:25];
def main():
    TracksBrowse(dirpath,"20150421.gpx")
#    logwrite=open(logfile,'a')
#    os.chdir(dirpath)
#    logfile.close()

if __name__ == '__main__':
    main()

