import os
import glob
import obspy
import pandas as pd

navidatadir = '../Data_navi'
stadatadirs = glob.glob('/home/sjh2019/Documents/Work_Junhao/Anninghe_Array/local_eqs_detection/workflows/LOC-FLOW/eqt-real-hypoinv/Data/*')
for stadatadir in stadatadirs:
    station = os.path.basename(stadatadir)
    navifile = os.path.join(navidatadir, '%s_summary_file.csv'%station)
    seisfiles = sorted(glob.glob(os.path.join(stadatadir, '*mseed')))
    starttimes = []
    endtimes = []
    for seisfile in seisfiles:
        st = obspy.read(seisfile)
        starttimes.append(st.sort(keys=['starttime'])[0].stats.starttime.timestamp)
        endtimes.append(st.sort(keys=['endtime'], reverse=True)[0].stats.endtime.timestamp)
    df = pd.DataFrame({'names':seisfiles, 'starttime':starttimes, 'endtime':endtimes})
    df.to_csv(navifile, sep=',', index=False)