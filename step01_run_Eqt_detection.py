#import warnings
#warnings.filterwarnings("ignore")
import os
import sys
sys.path.append('/home/sjh2019/Documents/Packages/EQ_Detection/EQTransformer')
import json
import yaml
import pandas as pd
from obspy import UTCDateTime
from EQTransformer.core.mseed_predictor import mseed_predictor
'''
Written by Junhao,SONG in Apr 2022
Use EQTransformer to detect earthquakes
And convert P and S picks into format for REAL input
'''


def save_picks_real_format(dataframe, dir4picks):
    '''
    input: EQtransformer X prediction results read by pandas.read_csv
    return: daily P and S picks text file under the directory for picks
    '''
    onedayseconds = 24*60*60
    ##################################################
    # Save P picks information into dict
    pha_dict = {}
    for irow in dataframe.index:
        # if no P pick, next loop
        pha_time = dataframe.loc[irow, 'p_arrival_time']
        if pd.isna(pha_time):
            continue
        # usually dataframe contains picks at one station
        # here considers more than one station situation
        # network = dataframe.loc[irow, 'network']
        network = dataframe.loc[irow, 'network']
        station = dataframe.loc[irow, 'station']
        stacode = network+'.'+station
        if stacode not in pha_dict.keys():
            pha_dict[stacode] = {}
        # for every station, their picks will be grouped
        # into daily picks for P and S picks, respectively
        # check if this day is in keys list of that station
        yyyymmdd = pha_time[:10].replace('-', '')
        if yyyymmdd not in pha_dict[stacode].keys():
            pha_dict[stacode][yyyymmdd] = []
        # then append results into certain station and day
        seconds = UTCDateTime(pha_time).timestamp % onedayseconds
        pha_prob = dataframe.loc[irow, 'p_probability']
        pha_dict[stacode][yyyymmdd].append([seconds, pha_prob])
        
    # Save P picks information from dict into files
    if not os.path.isdir(dir4picks):
        os.mkdir(dir4picks)
    for stacode in pha_dict.keys():
        for yyyymmdd in pha_dict[stacode].keys():
            onedaydir = os.path.join(dir4picks, yyyymmdd)
            if not os.path.exists(onedaydir):
                os.mkdir(onedaydir)
            w_pha = open(os.path.join(onedaydir, '%s.P.txt'%stacode), 'w')
            for pha_time, pha_prob in pha_dict[stacode][yyyymmdd]:
                w_pha.writelines('%.3f %.2f %.2f\n'%(pha_time, pha_prob, 0.0))
            w_pha.close()
            
    ##################################################
    
    ##################################################
    # Save S picks information into dict
    pha_dict = {}
    for irow in dataframe.index:
        # if no P pick, next loop
        pha_time = dataframe.loc[irow, 's_arrival_time']
        if pd.isna(pha_time):
            continue
        # usually dataframe contains picks at one station
        # here considers more than one station situation
        # network = dataframe.loc[irow, 'network']
        network = dataframe.loc[irow, 'network']
        station = dataframe.loc[irow, 'station']
        stacode = network+'.'+station
        if stacode not in pha_dict.keys():
            pha_dict[stacode] = {}
        # for every station, their picks will be grouped
        # into daily picks for P and S picks, respectively
        # check if this day is in keys list of that station
        yyyymmdd = pha_time[:10].replace('-', '')
        if yyyymmdd not in pha_dict[stacode].keys():
            pha_dict[stacode][yyyymmdd] = []
        # then append results into certain station and day
        seconds = UTCDateTime(pha_time).timestamp % onedayseconds
        pha_prob = dataframe.loc[irow, 's_probability']
        pha_dict[stacode][yyyymmdd].append([seconds, pha_prob])
        
    # Save S picks information from dict into files
    if not os.path.isdir(dir4picks):
        os.mkdir(dir4picks)
    for stacode in pha_dict.keys():
        for yyyymmdd in pha_dict[stacode].keys():
            onedaydir = os.path.join(dir4picks, yyyymmdd)
            if not os.path.exists(onedaydir):
                os.mkdir(onedaydir)
            w_pha = open(os.path.join(onedaydir, '%s.S.txt'%stacode), 'w')
            for pha_time, pha_prob in pha_dict[stacode][yyyymmdd]:
                w_pha.writelines('%.3f %.2f %.2f\n'%(pha_time, pha_prob, 0.0))
            w_pha.close()


# if __name__ == '__main__':
with open('./configuration.yaml', 'r') as f:
    cfgs = yaml.safe_load(f)

df = pd.read_csv(cfgs['Eqt']['stations_text'])
sta_dict = {}
for i in df.index:
    sta = df.loc[i, 'station']
    if sta not in sta_dict.keys():
        sta_dict[sta] = {}
        sta_dict[sta]['network'] = df.loc[i, 'network']
        sta_dict[sta]['channels'] = [df.loc[i, 'channel']]
        sta_dict[sta]['coords'] = [round(float(df.loc[i, 'latitude']), 6), 
                                   round(float(df.loc[i, 'longitude']), 6), 
                                   round(float(df.loc[i, 'elevation']), 1)]
    elif df.loc[i, 'network'] != sta_dict[sta]['network']:
        raise ValueError('duplicated station name: %s'%sta)
    else:
        sta_dict[sta]['channels'].append(df.loc[i, 'channel'])


with open(cfgs['Eqt']['stations_json'], 'w') as f:
    json.dump(sta_dict, f)

mseed_predictor(input_dir=cfgs['Eqt']['mseed_data_dir'],
                input_model=cfgs['Eqt']['eqt_model'],
                stations_json=cfgs['Eqt']['stations_json'],
                output_dir=cfgs['Eqt']['pks_result_dir'],
                detection_threshold=cfgs['Eqt']['eqt_eprob'],
                P_threshold=cfgs['Eqt']['eqt_pprob'],
                S_threshold=cfgs['Eqt']['eqt_sprob'],
                overlap=cfgs['Eqt']['overlap'], 
                batch_size=cfgs['Eqt']['batch_size'])
os.system('rm time_tracks.pkl')

for station in sta_dict.keys():
    eqt_prediction_file = os.path.join(cfgs['Eqt']['pks_result_dir'], station+'_outputs', 'X_prediction_results.csv')
    df = pd.read_csv(eqt_prediction_file)
    save_picks_real_format(df, cfgs['Eqt']['pks_4_REAL_dir'])

