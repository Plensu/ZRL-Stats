import json
import os
from pyjsonq import JsonQ
from os.path import isfile, join
import statistics
from collections import OrderedDict

season = 18
season_dir = "Data\\Season"

# PositionInClass
# PositionInClassStartLap
# Need to add PositionInClassDelta

def getGroupedAnalysisData(sessionName):
    groupedData = {}
    current_season_dir = f"{season_dir} {season}"
    grouped_file = join(current_season_dir, "grouped", f"{sessionName}.json")
    season_conf = json.load(open(f'{current_season_dir}\\conf.json'))
    season_session = join(current_season_dir, f"{sessionName}.json")
    for driver_class in season_conf['classes'].keys():
        groupedData[driver_class] = {}
        for driver in season_conf['classes'][driver_class]:
            driver_lap_data = JsonQ(season_session).at('laps').group_by('driver').get()
            try:
                driver_lap_query_conn = JsonQ(data=driver_lap_data[driver])
            except:
                continue

            total_lap_count = driver_lap_query_conn.count()
            valid_lap_count = driver_lap_query_conn.where('flags', '=', 0).where("lapType", "=", 2).count()
            try:
                fastest_lap = driver_lap_query_conn.where('flags', '=', 0).min("lapTime")
            except:
                fastest_lap = 999999
            try:
                fastest_sector1 = driver_lap_query_conn.where('flags', '=', 0).min("sector1")
            except:
                fastest_sector1 = 99999
            try:
                fastest_sector2 = driver_lap_query_conn.where('flags', '=', 0).min("sector2")
            except:
                fastest_sector2 = 99999
            try:
                fastest_sector3 = driver_lap_query_conn.where('flags', '=', 0).min("sector3")
            except:
                fastest_sector3 = 99999
            try:
                average_lap = driver_lap_query_conn.where('flags', '=', 0).where("lapType", "=", 2).avg('lapTime')
            except:
                average_lap = 999999
            optimal_lap = fastest_sector1 + fastest_sector2 + fastest_sector3
            try:
                stddev_valid_laps = statistics.stdev([lapTime['lapTime'] for lapTime in driver_lap_query_conn.where('flags', '=', 0).where("lapType", "=", 2).get()])
            except:
                stddev_valid_laps = 999999
            try:
                stddev_all_laps = statistics.stdev([lapTime['lapTime'] for lapTime in driver_lap_data[driver]])
            except:
                stddev_all_laps = 999999
            last_lap_time_stamp = driver_lap_query_conn.sum('lapTime')
            try:
                last_lap_position = driver_lap_query_conn.last()['position']
            except:
                last_lap_position = driver_lap_data[driver][-1]['position']
            try:
                valid_average_lap_time = driver_lap_query_conn.avg('lapTime')
            except:
                valid_average_lap_time = 999999


            groupedData[driver_class][driver] = {
                'total_laps': total_lap_count,
                'valid_laps': valid_lap_count,
                'valid_laps_percentage': round((valid_lap_count/total_lap_count)*100, 2),
                'average_lap_time': average_lap,
                'valid_average_lap_time': valid_average_lap_time,
                'fastest_lap': fastest_lap,
                'fastest_s1': fastest_sector1,
                'fastest_s2': fastest_sector2,
                'fastest_s3': fastest_sector3,
                'optimal_lap': optimal_lap,
                'std_deviation': stddev_all_laps,
                'valid_std_deviation': stddev_valid_laps,
                'last_lap_time_stamp': last_lap_time_stamp,
                'last_lap_position': last_lap_position,
                'driver_laps': [l['lapTime'] for l in driver_lap_data[driver]]
                }

        class_sorted = sorted(groupedData[driver_class].items(), key=lambda x: (-x[1]['total_laps'], x[1]['last_lap_position']))
        class_fixed = {}
        for driver in class_sorted:
            class_fixed[driver[0]] = driver[1]
        groupedData[driver_class] = class_fixed

    json.dump(groupedData, open(grouped_file, 'w'))


def getQualData(sessionName, driver):
    current_season_dir = f"{season_dir} {season}"
    session_quali = join(current_season_dir, "quals", f"{sessionName}.json")
    if not isfile(session_quali):
        return "File not found."
    try:
        return JsonQ(session_quali).at('laps').where('driver', '=', driver).where("flags", '=', 0).min("lapTime")
    except:
        return 0


def addClassPositionData(sessionName):
    new_laps = []
    current_season_dir = f"{season_dir} {season}"
    season_conf = json.load(open(f'{current_season_dir}\\conf.json'))
    season_session = join(current_season_dir, f"{sessionName}.json")
    if not isfile(season_session):
        return "File not found."
    jsonData = JsonQ(season_session).get()
    lap_count = jsonData['lapCount']
    all_laps = jsonData["laps"]
    
    

    for driver_class in season_conf["classes"].keys():
        drivers = season_conf["classes"][driver_class]
        lap_data = JsonQ(data=jsonData).at("laps")
        i = 1
        while i <= lap_count:
            laps = lap_data.where_in("driver", drivers).where("lapNumber", '=', i).get()
            for positionInClass, lap in enumerate(laps):
                lap['PositionInClass'] = positionInClass+1
                new_laps.append(lap)
            i += 1
            lap_data = JsonQ(data=jsonData).at("laps")
    new_new_laps = []
    for driver_class in season_conf["classes"].keys():
        quali_data = {}
        drivers = season_conf["classes"][driver_class]
        for driver in drivers:
            quali_data[driver] = getQualData(sessionName,driver)
        for key in [key for key in quali_data.keys()]:
            if quali_data[key] == 0:
                quali_data.pop(key)
        quali_order = sorted(quali_data.items(), key=lambda item: item[1])
        for driver in drivers:
            driver_laps = JsonQ(data=new_laps).where('driver', '=', driver).get()
            for lapNumber, lap in enumerate(driver_laps):
                if lapNumber == 0:
                    for quali_position, quali_driver in enumerate(quali_order):
                        if driver == quali_driver[0]:
                            lap['positionInClassStartLap'] = quali_position+1
                        lap['positionInClassDelta'] = lap['positionInClassStartLap'] - lap['PositionInClass']
                else:
                    lap['positionInClassStartLap'] = driver_laps[lapNumber - 1]['PositionInClass']
                    lap['positionInClassDelta'] = lap['positionInClassStartLap'] - lap['PositionInClass']
                new_new_laps.append(lap)
    race_json = json.load(open(join(current_season_dir, f"{sessionName}.json")))
    race_json['laps'] = new_new_laps
    json.dump(race_json, open(join(current_season_dir, f"{sessionName}.json"), 'w'))

addClassPositionData("Kyalami")
getGroupedAnalysisData('Kyalami')