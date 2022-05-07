import os
import glob
import obspy
import pandas as pd
import numpy as np


stalst_df = pd.read_csv('../Locations/staloc/stations.txt')
stations = stalst_df['station'].to_numpy()
stations = np.unique(stations)

for station in stations:
    df_pick = pd.read_csv('../Pick/Eqt/results/%s_outputs/X_prediction_results.csv'%station)
    df_navi = pd.read_csv('../Data_navi/%s_summary_file.csv'%station)
    outputdir = '../Pick/Eqt/results/%s_outputs'%station
    all_files = df_navi['names'].to_numpy()
    all_starttimes = df_navi['starttime'].to_numpy()
    all_endtimes = df_navi['endtime'].to_numpy()


    for ipick in df_pick.index:
        eq_t1 = obspy.UTCDateTime(df_pick.loc[ipick, 'event_start_time']).timestamp
        eq_t2 = obspy.UTCDateTime(df_pick.loc[ipick, 'event_end_time']).timestamp
        # eq_t1 in data time window
        indx1 = np.where((eq_t1>=all_starttimes) & (eq_t1<all_endtimes))[0]
        # eq_t2 in data time window
        indx2 = np.where((eq_t2>all_starttimes) & (eq_t2<=all_endtimes))[0]
        # eq_t1 and eq_t2 enclose data time window
        indx3 = np.where((eq_t1<all_starttimes) & (eq_t2>all_endtimes))[0]

        indx = np.concatenate((indx1, indx2, indx3))
        indx = np.unique(indx)

        files = all_files[indx]

        if len(files) == 0: continue

        st = obspy.Stream()
        for file in files:
            st += obspy.read(file)

        st = st.slice(starttime=obspy.UTCDateTime(eq_t1-10), endtime=obspy.UTCDateTime(eq_t2+10))
        st.merge(method=1)

        for tr in st:
            try:
                tr.stats.sac
            except:
                tr.stats.sac = {}
            tr.stats.sac.nzyear = tr.stats.starttime.year
            tr.stats.sac.nzjday = tr.stats.starttime.julday
            tr.stats.sac.nzhour = tr.stats.starttime.hour
            tr.stats.sac.nzmin = tr.stats.starttime.minute
            tr.stats.sac.nzsec = tr.stats.starttime.second
            tr.stats.sac.nzmsec = tr.stats.starttime.microsecond / 1000
            tr.stats.sac.b = 0
            tr.stats.sac.e = tr.stats.endtime - tr.stats.starttime
            tr.stats.sac.o = 0

        if not np.isnan(df_pick.loc[ipick, 'p_probability']):
            for tr in st:
                try:
                    tr.stats.sac
                except:
                    tr.stats.sac = {}
                tr.stats.sac.a = obspy.UTCDateTime(df_pick.loc[ipick, 'p_arrival_time']) - tr.stats.starttime
                tr.stats.sac.user0 = df_pick.loc[ipick, 'p_probability']

        if not np.isnan(df_pick.loc[ipick, 's_probability']):
            for tr in st:
                try:
                    tr.stats.sac
                except:
                    tr.stats.sac = {}
                tr.stats.sac.t0 = obspy.UTCDateTime(df_pick.loc[ipick, 's_arrival_time']) - tr.stats.starttime
                tr.stats.sac.user1 = df_pick.loc[ipick, 's_probability']

        for tr in st:
            tr_stt = tr.stats.starttime.strftime('%Y%m%dT%H%M%S')
            tr_edt = tr.stats.endtime.strftime('%Y%m%dT%H%M%S')
            seisfile = "%s.%s.%s__%s__%s.SAC"%(tr.stats.network, tr.stats.station, tr.stats.channel, tr_stt, tr_edt)
            seisfile = os.path.join(outputdir, seisfile)
            tr.write(seisfile, format='SAC')