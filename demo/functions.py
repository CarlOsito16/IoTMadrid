import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

selected_air_station_index = [24,47,50]
selected_air_magnitude_index = [7,9,10,12]

selected_meteor_station_index = [24,102,107]
selected_meteorlogical_factors = [81,83,88,89]

D_list= ["D0"+str(i) for i in range(1, 10)]  + ["D1"+str(i) for i in range(0, 10)] + ["D2"+str(i) for i in range(0, 10)] +['D30', "D31"]
air_station_dict = {
    'name' : {24 : 'Casa de Campo',
               47: "Méndez Álvaro",
               50: "Plaza de Castilla"}
    ,
    'station_type': {24: "Suburban",
                     47: "Urban Background",
                     50: "Roadside Traffic"},
    'latitude': {24: 40.4193577,
                47: 40.3980991,
                50: 40.4655841},
    'longitude': {24: -3.7473445,
                47: -3.6868138,
                50: -3.6887449},
    'pollutant': {7: 'NO',
                 9: 'PM2.5',
                 10: 'PM10',
                 12: 'NOx'}
}

meteor_dict = {
    'station_name' : {24 : 'Casa de Campo',
               102: "J.M.D. Moratalaz",
               107: "J.M.D. Hortaleza"}
    ,

    'meteor_factor': {81: 'Wind Speed',
                 83: 'Temperature',
                 88: 'Solar Radiation',
                 89: 'Precipitation'
                 },
    'map_station_type': {"Casa de Campo": "Suburban",
                         "J.M.D. Moratalaz": "Urban Background",
                         "J.M.D. Hortaleza": "Roadside Traffic"
        
    }
}


closest_traffic_to_air_station_dict= { 24: [1002, 6936, 6794, 6780, 3545, 1001, 3546, 5009, 5031, 1006],
 47: [7023, 4129, 4127,4126, 7076,7004,7003,4153,7083],
 50: [5465, 5639, 5468 ,3453, 3421 ,4581, 3449, 7017,4620, 5525 ,5515 ,5526 ,5516 ,5527 ]
}

CORRECT_USED_TRAFFIC_STATION = [3545,
 1006,
 1001,
 1002,
 3546,
 4581,
 4620,
 3421,
 7017,
 5465,
 5468,
 3449,
 5515,
 5516,
 5525,
 5526,
 5527,
 3453,
 5639,
 5031,
 5009,
 4153,
 7003,
 7004,
 4129,
 4126,
 7076,
 7023,
 7083,
 4127,
 6780,
 6794,
 6936]

closest_traffic_to_air_station_list = []
for a, i in closest_traffic_to_air_station_dict.items():
    closest_traffic_to_air_station_list.extend(i)


def edit_month_to_two_digit(input):
    if len(str(input)) < 2:
        new_input = str(0) + str(input)
    else:
        new_input = input
    
    return new_input



def clean_air_data(filename):
    
    print('Cleaning AIR data...')
    df = pd.read_csv(filename, sep=';')
    df = df[(df['ESTACION'].isin(selected_air_station_index)) &
            (df['MAGNITUD'].isin(selected_air_magnitude_index))]

    V_list= ["V0"+str(i) for i in range(1, 10)]  + ["V1"+str(i) for i in range(0, 10)] + ["V2"+str(i) for i in range(0, 10)] +['V30', "V31"]
    v_df = pd.melt(df, id_vars=['ESTACION', 'ANO', 'MES', 'MAGNITUD'], value_vars=V_list, value_name= 'sensor_valid')
    
    df['sensor_valid'] = v_df['sensor_valid']
    invalid_sensor_index = df[df['sensor_valid'] != 'V'].index
    df = pd.melt(df, id_vars=['ESTACION', 'ANO', 'MES', 'MAGNITUD'], value_vars=D_list)
    date_constraint_df = df[ (df['MES'] == 2) & (df['variable'].isin(['D29','D30','D31'])) |
    ((df['MES'] == 4) & (df['variable'].isin(['D31'])) )  |
    ((df['MES'] == 6) & (df['variable'].isin(['D31'])) )  |
    ((df['MES'] == 9) & (df['variable'].isin(['D31'])) )  |
    ((df['MES'] == 11) & (df['variable'].isin(['D31'])) ) 
    ]  
    

    
    # assert date_constraint_df['value'].sum() == 0
    
    to_drop_index = invalid_sensor_index.union(date_constraint_df.index)
    df = df.drop(to_drop_index)
    print(f'Dropping: {len(invalid_sensor_index)} rows')
    df['meteor_station'] = df['MAGNITUD'].apply(lambda x : air_station_dict['pollutant'][x] )
    df['meteor_station'] = df['ESTACION'].apply(lambda x : air_station_dict['name'][x] )
    df['station_type'] = df['ESTACION'].apply(lambda x : air_station_dict['station_type'][x] )
    df['latitude'] = df['ESTACION'].apply(lambda x : air_station_dict['latitude'][x] )
    df['longitude'] = df['ESTACION'].apply(lambda x : air_station_dict['longitude'][x] )
    
    
    ## MANAGE TIMESTAMP
    
    df['MES'] = df.apply(lambda x: edit_month_to_two_digit(x['MES']), axis = 1)
    df['datestamp'] = pd.to_datetime(df.apply(lambda x  : x['variable'][1:] +"-" + str(x['MES']) + "-" + str(x['ANO']), axis = 1),
               format = '%d-%m-%Y')
    
    df['pollutant_name'] = df.MAGNITUD.apply(lambda x: air_station_dict['pollutant'][x] ) 
    
    
    g = sns.FacetGrid(df, col="pollutant_name", hue = 'station_type',
                  col_order = ["NO", "NOx", "PM2.5", "PM10"])
    g.map(sns.lineplot,  "datestamp",'value')
    [plt.setp(ax.get_xticklabels(), rotation=45) for ax in g.axes.flat]
    plt.legend()
    
    
    return df



def clean_meteor_data(filename):
     
    print('Cleaning METEOR data...')
    df = pd.read_csv(filename, sep=';')
    df = df[(df['ESTACION'].isin(selected_meteor_station_index)) &
            (df['MAGNITUD'].isin(selected_meteorlogical_factors))]

    D_list= ["D0"+str(i) for i in range(1, 10)]  + ["D1"+str(i) for i in range(0, 10)] + ["D2"+str(i) for i in range(0, 10)] +['D30', "D31"]
    V_list= ["V0"+str(i) for i in range(1, 10)]  + ["V1"+str(i) for i in range(0, 10)] + ["V2"+str(i) for i in range(0, 10)] +['V30', "V31"]


    v_df = pd.melt(df, id_vars=['ESTACION', 'ANO', 'MES', 'MAGNITUD'], value_vars=V_list, value_name= 'sensor_valid')
    df = pd.melt(df, id_vars=['ESTACION', 'ANO', 'MES', 'MAGNITUD'], value_vars=D_list)
    
    df['sensor_valid'] = v_df['sensor_valid']
    invalid_sensor_index = df[df['sensor_valid'] != 'V'].index
    
    date_constraint_df = df[ (df['MES'] == 2) & (df['variable'].isin(['D29','D30','D31'])) |
    ((df['MES'] == 4) & (df['variable'].isin(['D31'])) )  |
    ((df['MES'] == 6) & (df['variable'].isin(['D31'])) )  |
    ((df['MES'] == 9) & (df['variable'].isin(['D31'])) )  |
    ((df['MES'] == 11) & (df['variable'].isin(['D31'])) ) 
    ]  
    
    # # assert date_constraint_df['value'].sum() == 0
    
    to_drop_index = invalid_sensor_index.union(date_constraint_df.index)
    print(f'Dropping: {len(invalid_sensor_index)} rows')
    df = df.drop(to_drop_index)
    df['meteor_factor'] = df['MAGNITUD'].apply(lambda x : meteor_dict['meteor_factor'][x] )
    df['station_name'] = df['ESTACION'].apply(lambda x : meteor_dict['station_name'][x] )

    
    
    # MANAGE TIMESTAMP
    
    df['MES'] = df.apply(lambda x: edit_month_to_two_digit(x['MES']), axis = 1)
    df['datestamp'] = pd.to_datetime(df.apply(lambda x  : x['variable'][1:] +"-" + str(x['MES']) + "-" + str(x['ANO']), axis = 1),
               format = '%d-%m-%Y')
    
    df['station_type'] = df.station_name.apply(lambda x: meteor_dict['map_station_type'][x] ) 
    
    g = sns.FacetGrid(df, col="meteor_factor", hue = 'station_type', sharey=False)
    g.map(sns.lineplot,  "datestamp",'value')
    [plt.setp(ax.get_xticklabels(), rotation=45) for ax in g.axes.flat]
    plt.legend()
    
    return df

# for traffic
def convert_datetime(df, dateime_column):
    df[dateime_column] = pd.to_datetime(df[dateime_column]).dt.date
    return df

def linked_air_station(traffic_station_id):
    if traffic_station_id in closest_traffic_to_air_station_dict[24]:
        result_air_station = 24
    elif traffic_station_id in closest_traffic_to_air_station_dict[47]:
        result_air_station = 47
    elif traffic_station_id in closest_traffic_to_air_station_dict[50]:
        result_air_station = 50
    return result_air_station
           
    
def clean_monthly_traffic(FILEPATH):
    df = pd.read_csv(FILEPATH, sep= ";")
    df = convert_datetime(df,  dateime_column='fecha')
    
    columns_to_drop = ['tipo_elem', 'ocupacion', 'carga', 'vmed', 'periodo_integracion']
    df = df.drop(columns = columns_to_drop)
    
    sensor_valid_index_to_drop = df[df['error'] != 'N'].index
    closest_station_index_to_drop = df[~df['id'].isin(CORRECT_USED_TRAFFIC_STATION)].index
    
    all_to_trop_index = sensor_valid_index_to_drop.union(closest_station_index_to_drop)
    df = df.drop(all_to_trop_index)
    print(f'Dropping {len(all_to_trop_index)}')
    
    df['true_intensity'] = df['intensidad'] / 4 #must divide by 4 because it keeps data in 15 minute inteval but shown in an hour
    
    
    # # AGGREGATION OF MEANS FROM THE SAME STATION IN EACH DAY
    groupby_mean_df = df.groupby(['fecha', 'id']).aggregate({'true_intensity': ['mean']}).reset_index()
    groupby_mean_df.columns = groupby_mean_df.columns.droplevel(1)
    groupby_mean_df['linked_air_station'] = np.vectorize(linked_air_station)(groupby_mean_df['id'])
    
    # # AGGREGATION OF MEANS FROM THE DIFFERENT STATIONS UNDER SAME AIR STATION TYPE IN EACH DAY
    groupby_mean_df.groupby(['fecha', 'linked_air_station'])['true_intensity'].mean().reset_index()

    
    groupby_mean_df['fecha'] = pd.to_datetime(groupby_mean_df.fecha)
    groupby_mean_df['MES'] = groupby_mean_df.fecha.dt.month
    groupby_mean_df['ANO'] = groupby_mean_df.fecha.dt.year
    
    groupby_mean_df['air_station_name'] = groupby_mean_df['linked_air_station'].apply(lambda x : air_station_dict['name'][x] )
    groupby_mean_df['air_station_type'] = groupby_mean_df['linked_air_station'].apply(lambda x : air_station_dict['station_type'][x] )
    
    print(groupby_mean_df.MES.unique())
    print(groupby_mean_df.ANO.unique())
    print(groupby_mean_df.linked_air_station.unique())
    print()
    
    sns.lineplot(data= groupby_mean_df, x= 'fecha', y = 'true_intensity', hue = 'air_station_type')
    plt.xticks(rotation = 45)
    plt.plot()
    
    
    return groupby_mean_df


