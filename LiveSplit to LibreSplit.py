import time

file = str(input("File name of Live Split file (.lss): ")) #Can import any file. expects to end in .lss

LSS=open(file,'r').readlines()
output = open(file[0:-4]+".json",'w',encoding='utf-8') #gets file name without extension. Removes last few characters
segmentMap = [] #+15 for the full data
counter = 0
attemptMap = []
completedCount = 0

comparison = "<RealTime>"

def hms_to_s(time_str):
    time = time_str.split(":")
    hours = int(time[0])*3600
    minutes = int(time[1])*60
    seconds = float(time[2])

    total_time = round(hours+minutes+seconds,6)
    return total_time


def s_to_hms(full_seconds):
    seconds,ms = str(full_seconds).split(".")
    return(time.strftime('%H:%M:%S', time.gmtime(int(seconds)))+"."+ms[0:6])

for line in LSS:
    if "<GameName>" in line:
        gameName = line[12:len(line)-12]
    if "<CategoryName>" in line:
        categoryName = line[16:len(line)-16]
    if "<AttemptCount>" in line:
        attemptCount = line[16:len(line)-16]
    if "<Segment>" in line:
        segmentMap.append(counter)
    if "AttemptHistory>" in line:
        attemptMap.append(counter)
    if "<GameTime>" in line and comparison == "<RealTime>":
        comparison = "<GameTime>" #makes splits based on game time instead of real time (default)
    counter += 1


for line in LSS[attemptMap[0]:attemptMap[1]]: #finds completed runs by finding run end times in the "Attemps" segment of LSS file
    if "<RealTime>" in line:
        completedCount += 1


output.write('{\n\t"title": '+'"'+gameName+' - '+categoryName+'",\n')
output.write('\t"attempt_count": '+attemptCount+',\n')
output.write('\t"finished_count": '+str(completedCount)+',\n')
output.write('\t"splits": [\n')


sum_of_best = 0


for i in segmentMap: #prints the entire Segment of a lss file (the next 15 lines after <Segment>). Ignores segment history
    segment = LSS[i:i+15]

    PB = 0
    Gold = 0
    for y in segment:
        if "<Name>" in y:
            output.write('\t\t{\n')
            output.write('\t\t\t"title": '+'"'+y[12:len(y)-8]+'",\n')


        #since GameTime/RealTime shows up in both best segments and PB splits, the two need to be differentiated

        if '<SplitTime name="Personal Best">' in y:
            PB = 1
        if '<BestSegmentTime>' in y:
            Gold = 1
            PB = 0

        if comparison in y: #looks for split time (game or real time)

            if PB == 1:
                output.write('\t\t\t"time": '+'"'+y[20:len(y)-13]+'",\n')
                PB = 0

            if Gold == 1:
                sum_of_best += hms_to_s(y[18:len(y)-13])
                output.write('\t\t\t"best_time": '+'"'+s_to_hms(sum_of_best)+'",\n') #calculates sum of best, unsure if that's what best_time is supposed to be
                output.write('\t\t\t"best_segment": '+'"'+y[18:len(y)-13]+'"\n')
                if y == segment[-1]:
                    output.write('\t\t}\n') #won't put the comma on the last iteration of the loop
                else:
                    output.write('\t\t},\n')

output.write('\t],\n')
output.write('\t"width": 400,\n')
output.write('\t"height": 800\n}\n')

print("Successfully converted ",file," > ",file[0:-4]+".json")
