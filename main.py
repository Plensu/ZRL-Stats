"""
Zealous Racing League Stats App
Check out ZRL on SimGrid: https://www.thesimgrid.com/hosts/zealousracing
Check out ZRL on Discord: https://discord.gg/e3wUySg
Check out ZRL on Youtube: https://www.youtube.com/@zealousracingleague4661
"""

import streamlit as st
import pandas as pd
import json
from pyjsonq import JsonQ
from os import listdir
from os.path import isfile, join
from datetime import datetime
import matplotlib.dates as md
import matplotlib.pyplot as plt
import statistics
import numpy as np
import altair as alt

season = 16
season_dir = "Data\\Season"

def convert_time(milliseconds):
    seconds = round((milliseconds/1000)%60, 3)
    minutes = int((milliseconds/(1000*60))%60)
    if minutes != 0:
        return f'{minutes}:{seconds:.3f}'
    else:
        return f'{seconds:.3f}'

def addColors(row, fastest_sector1, fastest_sector2, fastest_sector3, fastest_lap):
    sector1_color = 'color: purple' if row['Sector 1'] == convert_time(fastest_sector1) and row['flags'] == 0 else ''
    sector2_color = 'color: purple' if row['Sector 2'] == convert_time(fastest_sector2) and row['flags'] == 0 else ''
    sector3_color = 'color: purple' if row['Sector 3'] == convert_time(fastest_sector3) and row['flags'] == 0 else ''
    fastest_lap_color = 'color: purple' if row['Lap Time'] == convert_time(fastest_lap) and row['flags'] == 0 else ''
    if row['positionInClassDelta'] > 0:
        position_color = 'color: green'
    elif row['positionInClassDelta'] < 0:
        position_color = 'color: red'
    else:
        position_color = ''

    if row['lapType'] != 2 or row['flags'] != 0:
        lap_color = 'color: red'
    else:
        lap_color = ''

    return [f'{lap_color}', f'{position_color}', f'{sector1_color}', f'{sector2_color}', f'{sector3_color}', f'{fastest_lap_color}', '', '', '']

def groupedAddColors(row, group_fastest_lap, group_best_average, group_best_stddev, group_best_s1, group_best_s2, group_best_s3, group_best_opt):
    sector1_color = 'color: purple' if row['S1'] == convert_time(group_best_s1) else ''
    sector2_color = 'color: purple' if row['S2'] == convert_time(group_best_s2) else ''
    sector3_color = 'color: purple' if row['S3'] == convert_time(group_best_s3) else ''
    fastest_lap_color = 'color: purple' if row['Fastest'] == convert_time(group_fastest_lap) else ''
    average_color = 'color: purple' if row['Average'] == convert_time(group_best_average) else ''
    stddev_color = 'color: purple' if row['Std Dev'] == convert_time(group_best_stddev) else ''
    opt_color = 'color: purple' if row['Optimal'] == convert_time(group_best_opt) else ''
    return ['', '', '', '',f'{average_color}',f'{fastest_lap_color}',f'{sector1_color}',f'{sector2_color}',f'{sector3_color}',f'{opt_color}', '',f'{stddev_color}','','','']

def groupedAnalysis(session, driver_class, laps_by_drivers):
    grouped_dir = "grouped"
    current_season_dir = f"{season_dir} {season}"
    grouped_file = join(current_season_dir, grouped_dir, f"{session}.json")
    class_data = JsonQ(grouped_file).at(driver_class).get()
    my_dict = {}
    total_laps = []
    valid_laps = []
    valid_laps_percentage = []
    average_lap_time = []
    valid_average_lap_time = []
    fastest_lap = []
    fastest_sector1 =[]
    fastest_sector2 =[]
    fastest_sector3 =[]
    optimal_lap = []
    std_deviation = []
    valid_std_deviation = []
    for driver in class_data.keys():
        total_laps.append((driver,class_data[driver]['total_laps']))
        valid_laps.append((driver,class_data[driver]['valid_laps']))
        valid_laps_percentage.append((driver,class_data[driver]['valid_laps_percentage']))
        average_lap_time.append((driver,class_data[driver]['average_lap_time']))
        valid_average_lap_time.append((driver,class_data[driver]['valid_average_lap_time']))
        fastest_lap.append((driver,class_data[driver]['fastest_lap']))
        optimal_lap.append((driver,class_data[driver]['optimal_lap']))
        std_deviation.append((driver,class_data[driver]['std_deviation']))
        valid_std_deviation.append((driver,class_data[driver]['valid_std_deviation']))

    df = pd.DataFrame.from_dict(class_data)
    tdf = df.transpose()
    tdf.rename(columns={
        "fastest_lap": "Fastest",
        "valid_average_lap_time": "Average",
        "valid_std_deviation": "Std Dev",
        "fastest_s1": "S1",
        "fastest_s2": "S2",
        "fastest_s3": "S3",
        "optimal_lap": "Optimal"
    }, inplace=True)
    group_fastest_lap = tdf['Fastest'].min()
    tdf['Fastest'] = tdf['Fastest'].apply(convert_time)
    group_best_average = tdf['Average'].min()
    tdf['Average'] = tdf['Average'].apply(convert_time)
    group_best_stddev = tdf['Std Dev'].min()
    tdf['Std Dev'] = tdf['Std Dev'].apply(convert_time)
    group_best_s1 = tdf['S1'].min()
    tdf['S1'] = tdf['S1'].apply(convert_time)
    group_best_s2 = tdf['S2'].min()
    tdf['S2'] = tdf['S2'].apply(convert_time)
    group_best_s3 = tdf['S3'].min()
    tdf['S3'] = tdf['S3'].apply(convert_time)
    group_best_opt = tdf['Optimal'].min()
    tdf['Optimal'] = tdf['Optimal'].apply(convert_time)
    st.dataframe(tdf.style.apply(groupedAddColors, axis=1, group_fastest_lap=group_fastest_lap, group_best_average=group_best_average, group_best_stddev=group_best_stddev, group_best_s1=group_best_s1, group_best_s2=group_best_s2, group_best_s3=group_best_s3, group_best_opt=group_best_opt), column_config={
        "total_laps": None,
        "valid_laps": None,
        "valid_laps_percentage": None,
        "average_lap_time": None,
        "std_deviation": None,
        "last_lap_time_stamp": None,
        "last_lap_position": None,
        "driver_laps": st.column_config.LineChartColumn("Lap Times", pinned=True)
        })
    
    # my_dict['valid_laps'] = sorted(valid_laps, key=lambda tup: tup[1], reverse=True)
    # my_dict['total_laps'] = sorted(total_laps, key=lambda tup: tup[1], reverse=True)
    # my_dict['valid_laps_percentage'] = sorted(valid_laps_percentage, key=lambda tup: tup[1], reverse=True)
    # my_dict['average_lap_time'] = sorted(average_lap_time, key=lambda tup: tup[1])
    # my_dict['valid_average_lap_time'] = sorted(valid_average_lap_time, key=lambda tup: tup[1])
    # my_dict['fastest_lap'] = sorted(fastest_lap, key=lambda tup: tup[1])
    # my_dict['optimal_lap'] = sorted(optimal_lap, key=lambda tup: tup[1])
    # my_dict['std_deviation'] = sorted(std_deviation, key=lambda tup: tup[1])
    # my_dict['valid_std_deviation'] = sorted(valid_std_deviation, key=lambda tup: tup[1])

    # col1, col2, col3 = st.columns(3, gap='medium')
    # with col1:
    #     group_data_sub_table = "|    | Valid Laps |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['valid_laps']:
    #         group_data_sub_table += f"{i}|{item[0]} {item[1]}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    #     group_data_sub_table = "|    | Average Lap Time |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['average_lap_time']:
    #         group_data_sub_table += f"{i}|{item[0]} {convert_time(item[1])}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    #     group_data_sub_table = "|    | Optimal Lap Time |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['optimal_lap']:
    #         group_data_sub_table += f"{i}|{item[0]} {convert_time(item[1])}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    # with col2:
    #     group_data_sub_table = "|    | Total Laps |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['total_laps']:
    #         group_data_sub_table += f"{i}|{item[0]} {item[1]}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    #     group_data_sub_table = "|    | Valid Avg Lap Time |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['valid_average_lap_time']:
    #         group_data_sub_table += f"{i}|{item[0]} {convert_time(item[1])}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    #     group_data_sub_table = "|    | Standard Deviation |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['std_deviation']:
    #         group_data_sub_table += f"{i}|{item[0]} {convert_time(item[1])}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    # with col3:
    #     group_data_sub_table = "|    | Valid Laps Percentage |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['valid_laps_percentage']:
    #         group_data_sub_table += f"{i}|{item[0]} {item[1]}%\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    #     group_data_sub_table = "|    | Fastest Lap |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['fastest_lap']:
    #         group_data_sub_table += f"{i}|{item[0]} {convert_time(item[1])}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)
    #     group_data_sub_table = "|    | Valid Lap Std Dev |\n"
    #     group_data_sub_table += "|---:|:-----------|\n"
    #     i = 1
    #     for item in my_dict['valid_std_deviation']:
    #         group_data_sub_table += f"{i}|{item[0]} {convert_time(item[1])}\n"
    #         i += 1
    #     st.markdown(group_data_sub_table)

    

def driverAnalysis(driver_class, driver_lap_data):
    df = pd.DataFrame(
        driver_lap_data, columns=['lapNumber', 'PositionInClass', 'sector1', 'sector2', 'sector3', 'lapTime', 'positionInClassDelta', 'lapType', 'flags']
    )

    driver_lap_query_conn = JsonQ(data=driver_lap_data)
    
    qualified_position = driver_lap_query_conn.first()['positionInClassStartLap']
    finishing_position = driver_lap_query_conn.last()['PositionInClass']
    total_lap_count = driver_lap_query_conn.count()
    valid_lap_count = driver_lap_query_conn.where('flags', '=', 0).where("lapType", "=", 2).count()
    fastest_lap = driver_lap_query_conn.where('flags', '=', 0).min("lapTime")
    fastest_sector1 = driver_lap_query_conn.where('flags', '=', 0).min("sector1")
    fastest_sector2 = driver_lap_query_conn.where('flags', '=', 0).min("sector2")
    fastest_sector3 = driver_lap_query_conn.where('flags', '=', 0).min("sector3")
    average_lap = driver_lap_query_conn.where('flags', '=', 0).where("lapType", "=", 2).avg('lapTime')
    optimal_lap = fastest_sector1 + fastest_sector2 + fastest_sector3
    stddev_valid_laps = [lapTime['lapTime'] for lapTime in driver_lap_query_conn.where('flags', '=', 0).where("lapType", "=", 2).get()]
    stddev_all_laps = statistics.stdev([lapTime['lapTime'] for lapTime in driver_lap_data])

    
    df["lapTime"] = df["lapTime"].apply(convert_time)
    df["sector1"] = df["sector1"].apply(convert_time)
    df["sector2"] = df["sector2"].apply(convert_time)
    df["sector3"] = df["sector3"].apply(convert_time)
    df.rename(columns={
        "lapNumber":    "Lap",
        "positionInClass":     "Position",
        "lapTime":      "Lap Time",
        "sector1":      "Sector 1",
        "sector2":      "Sector 2",
        "sector3":      "Sector 3",
    }, inplace=True)

    col1, col2, col3 = st.columns(3, gap='medium')

    with col1:
        st.write(f'Qualified: P{qualified_position}')
        st.write(f'Best Lap: {convert_time(fastest_lap)}')
        st.write(f'Total Laps: {total_lap_count}')
    with col2:
        st.write(f'Finished: P{finishing_position}')
        st.write(f'Optimal Lap: {convert_time(optimal_lap)}')
        st.write(f'Valid Laps: {valid_lap_count}')
    with col3:
        st.write(f'Positions: {('-' if (qualified_position - finishing_position) < 0 else ('+' if (qualified_position - finishing_position) > 0 else ''))}{abs(qualified_position-finishing_position)}')
        st.write(f'Average Lap: {convert_time(average_lap)}')
        st.write(f'Valid Laps Percentage: {round((valid_lap_count/total_lap_count)*100, 2)}%')

    st.dataframe(df.style.apply(addColors, axis=1, fastest_lap=fastest_lap,fastest_sector1=fastest_sector1,fastest_sector2=fastest_sector2,fastest_sector3=fastest_sector3), use_container_width=True, hide_index=True, column_config={"positionInClassDelta": None, "lapType": None, "flags": None})
    lap_graph_data = pd.DataFrame(driver_lap_data, columns=['lapNumber','lapTime'])
    lap_graph_data['Average'] = average_lap/1000
    lap_graph_data['lapTime'] = lap_graph_data['lapTime'].apply(lambda x: x/1000)
    lap_graph_data.rename(columns={'lapNumber': 'Lap', 'lapTime': 'Lap Time'}, inplace=True)
    lap_line = (alt.Chart(lap_graph_data).mark_line(color='blue').encode(x="Lap", y=alt.Y('Lap Time', title='Lap Time',scale=alt.Scale(domain=[lap_graph_data['Lap Time'].min()-1, lap_graph_data['Lap Time'].max()+1]))))
    avg_line = (alt.Chart(lap_graph_data).mark_line(color='green').encode(x='Lap', y=alt.Y('Average', title='Lap Time',scale=alt.Scale(domain=[lap_graph_data['Lap Time'].min()-1, lap_graph_data['Lap Time'].max()+1]))))
    st.altair_chart(lap_line+avg_line, use_container_width=True)
    #st.line_chart(lap_graph_data, x='Lap', x_label='Lap', y_label='Seconds')



def current_season():
    current_season_dir = f"{season_dir} {season}"
    season_conf = json.load(open(f'{current_season_dir}/conf.json'))
    season_sessions = [f.split('.')[0] for f in listdir(f"{current_season_dir}") if isfile(join(current_season_dir, f)) and f != "conf.json"]
    select_session = st.selectbox("Select Race",season_sessions)
    select_class = st.selectbox("Select Class", season_conf["classes"].keys())
    
    json_data = JsonQ(f'{current_season_dir}\\{select_session}.json')
    laps_by_drivers = json_data.at('laps').group_by('driver').get()
    drivers = [d for d in laps_by_drivers.keys() if d in season_conf["classes"][select_class]]
    drivers_select_options = drivers
    drivers_select_options.append('Grouped Analysis')
    select_driver = st.selectbox("Select Driver", drivers_select_options)
    if select_driver == 'Grouped Analysis':
        groupedAnalysis(select_session, select_class, laps_by_drivers)
    else: 
        driver_lap_data = laps_by_drivers[select_driver]
        driverAnalysis(select_class, driver_lap_data)

def archived_seasons():
    print('ok')

pg = st.navigation([st.Page(current_season, title=f"Season {season}"), st.Page(archived_seasons, title="Archives")])
pg.run()
