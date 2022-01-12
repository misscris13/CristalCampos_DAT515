import json
import math
import sys

# -------------------------------------------------------------------------- #
#                                                                            #
#   Lab 1 - DAT515 Advanced Programming in Python                            #
#                                                                            #
#   Cristal Campos Abad                                                      #
#                                                                            #
# -------------------------------------------------------------------------- #


# --------------------- DICTIONARY BUILDING FUNCTIONS ---------------------- #
 
# Building a stop dictionary, where keys are names of tram stops and
# values are dictionaries with the latitud and the longitude.
def build_tram_stops(jsonobject):

    # raw data from the json file
    raw_stops = {}  # format { town:n position:[ lat, lon ] }

    # reading the file
    with open(jsonobject) as file:
        raw_stops = json.load(file)

    # formatted dictionary
    fmtd_stops = {} # format { name: { lat:x lon:y } }

    # fill the dictionary
    for entry in raw_stops:
        position = raw_stops.get(entry).get('position')
        fmtd_stops[entry] = { 'lat': position[0], 'lon': position[1] }

    return fmtd_stops


# Building a line dictionary, where keys are names (numbers) and values
# are lists of stop names, in order.
def build_tram_lines(lines):

    # -------------------- BUILDING THE LINE DICTIONARY --------------------- #
    # line dictionary
    line_dict = {}  # format { num: [stops] }

    # reading the file
    with open(lines, "r", encoding='utf-8') as file:
        data = file.read()

    # separating by line numbers
    lines = data.split("\n\n")

    # building the line dictionary
    for line in lines:
        # get every stop
        stops = line.split("\n")

        # get only the line number
        num = stops[0].split(":")[0]

        # create every list of stops
        stop_list = []
        for stop in stops[1:]:
            # a way to separate the name from the time
            aux = stop.split("  ")
            # append the name
            stop_list.append(aux[0])

        # fill the dictionary
        line_dict[num] = stop_list
    
    # ---------------------------------------------------------------------- #
    # -------------------- BUILDING THE TIME DICTIONARY -------------------- #
    time_dict = {}  # format { stop: { stops: time } }

    for line in lines: # line = tram line
        # get every stop
        stops = line.split("\n")
        
        for stop in stops[1:]:
            # get info from current stop
            name = stop[:(stop.find("  "))]
            minutes = int(stop[-2:])
            
            aux_dict = {}

            # for every stop
            for aux in stops[1:]:
                # get info
                auxname = aux[:(aux.find("  "))]
                auxminutes = int(aux[-2:])

                # for those stops that are not the same as the one in question
                if name != auxname:
                    if minutes > auxminutes:
                        aux_dict[auxname] = minutes - auxminutes
                    else:
                        aux_dict[auxname] = auxminutes - minutes
            
            if name not in time_dict:
                    time_dict[name] = aux_dict
            else:
                for item in aux_dict:
                    if item not in time_dict.get(name):
                        time_dict.get(name)[item] = aux_dict.get(item)
                
            del aux_dict

    return [line_dict, time_dict]


# Puts everything together. Reads the two input files and writes a third one,
# 'tramnetwork.json'.
def build_tram_network(files):
    
    # get data
    stops = build_tram_stops(files[0])
    [lines, times] = build_tram_lines(files[1])

    # big dictionary
    dict = {}
    dict['stops'] = stops
    dict['lines'] = lines
    dict['times'] = times

    with open('./tramnetwork.json', 'w') as out:
        json.dump(dict, out, indent=4)


# ---------------------------- QUERY FUNCTIONS ----------------------------- #

# Lists the lines that go via the given stop.
def lines_via_stop(lines, stop):
    
    # result
    res = []

    for line in lines:
        for st in lines.get(line):
            if stop == st:
                res.append(line)

    return res


# Lists the lines that go from stop1 to stop2,
def lines_between_stops(lines, stop1, stop2):
    
    # result
    res = []

    for line in lines:
        one = False
        two = False
        for st in lines.get(line):
            if stop1 == st:
                one = True
            elif stop2 == st:
                two = True
        if one and two:
            res.append(line)
    return res


# Calculates the time from stop1 to stop2 along the given line
def time_between_stops(lines, times, line, stop1, stop2):
    valid_lines = lines_between_stops(lines, stop1, stop2)
    time = -1

    if (line not in valid_lines):
        print("Error, stops not in the same line.")
    else:   # stops are along the same line
        for stop in times.get(stop1):
            if (stop == stop2):
                time = times.get(stop1).get(stop)
    
    return time


# Calculates the geographic distance between any to stops
def distance_between_stops(stops, stop1, stop2):
    
    # variables
    lat1 = float(stops.get(stop1).get("lat"))
    lat2 = float(stops.get(stop2).get("lat"))
    lon1 = float(stops.get(stop1).get("lon"))
    lon2 = float(stops.get(stop2).get("lon"))

    # function to change to radians
    def rad(n):
        return (n * math.pi / 180)

    # deltas
    dlat = rad(lat2 - lat1)
    dlon = rad(lon2 - lon1)
    phi_m = rad( (lat1 + lat2) / 2 )

    # formula
    r = 6371
    distance =  r * math.sqrt( pow(dlat, 2) + 
                pow( ( math.cos(phi_m) * dlon ), 2) )

    return distance

    
# Dialogue function
def dialogue(jsonfile):
    
    # reading the file
    with open(jsonfile) as file:
        data = json.load(file)
    # creating dictionaries
    lines = data.get("lines")
    stops = data.get("stops")
    times = data.get("times")

    # dialogue
    inp = ""
    while (inp != "quit"):
        inp = input("> ")

        # get keyword separated from data
        kpos = inp.find(" ") # finds first space

        if kpos != -1: # space found
            keyword = inp[:kpos]
            inp = inp[kpos+1:]

            # via keyword
            if (keyword == "via"):
                stop = inp
                print(stop)
                res = lines_via_stop(lines, stop)
                if (len(res) == 0):
                    print("Error: Unknown arguments")
                else:
                    print(res)
            
            # between keyword
            elif (keyword == "between"):
                apos = inp.find("and")

                if apos == -1:
                    print("Error: Unknown syntax")
                else:
                    stop1 = inp[:apos-1]
                    stop2 = inp[apos+4:]
                    res = lines_between_stops(lines, stop1, stop2)
                    if(len(res) == 0):
                        print("Error: Unknown arguments")
                    else:
                        print(res)

            # time keyword
            elif (keyword == "time"):
                tpos = inp.find("to")
                wpos = inp.find("with")
                fpos = inp.find("from")

                if tpos == -1 or wpos == -1 or fpos == -1:
                    print("Error: Unknown syntax")
                else:
                    line = inp[wpos+5:fpos-1]
                    stop1 = inp[fpos+5:tpos-1]
                    print(stop1, "a")
                    stop2 = inp[tpos+3:]
                    print(stop2, "a")
                    res = time_between_stops(lines, times, line, stop1, stop2)
                    print(res)

            # distance keyword
            elif (keyword == "distance"):
                tpos = inp.find("to")
                fpos = inp.find("from")

                if tpos == -1 or fpos == -1:
                    print("Error: Unknown syntax")
                else:
                    stop1 = inp[fpos+5:tpos-1]
                    stop2 = inp[tpos+3:]
                    res = distance_between_stops(stops, stop1, stop2)
                    print(round(res, 2), "km")

        # quit keyword            
        elif inp == "quit":
            print("Quitting...")
        # error
        else:
            print("Sorry, try again")


if __name__ == '__main__':
    if sys.argv[1:] == ['init']:
        build_tram_network(["../data/tramstops.json", "../data/tramlines.txt"])
    else:
        dialogue("tramnetwork.json")