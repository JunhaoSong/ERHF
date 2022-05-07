import os
import glob
import shutil
import pandas as pd
from obspy import read
from obspy import Stream
from obspy import UTCDateTime
from obspy.geodetics import gps2dist_azimuth

def ykx(x, k): return k*x
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.transforms import blended_transform_factory

# the selected region/area
minlon = 104.3
maxlon = 104.7
minlat = 29.2
maxlat = 29.6
# waveform parameters
beforeo = 5
aftero  = 20
freqmin = 0.5
freqmax = 20
channel = 'BHZ'
# input and output data
stalist = '../Locations/staloc/stations.txt'
stadf = pd.read_csv(stalist)
catalog  = '../Locations/evtloc/hypoOut.arc'
mseeddir = '../Data'
eventsdir = './Hypoinv_events'
if not os.path.isdir(eventsdir):
    os.mkdir(eventsdir)
# use associated picks or not
usepicks = True
nstations = 10 # should be given if usepicks is False, waveforms at the closest n stations would be extracted

# no change expected below
if not os.path.exists(eventsdir):
    os.mkdir(eventsdir)
else:
    shutil.rmtree(eventsdir)
    os.mkdir(eventsdir)
f = open(catalog, 'r')
lines = f.readlines()
f.close()

# part one: cut data
for line in lines:
    if len(line) == 180:
        iok = 0
        if line[18] == ' ': #N
            lat = (float(line[16:18]) + float(line[19:23]) / 6000)
        else:
            lat = float(line[16:18]) + float(line[19:23])/6000 * (-1)

        if line[26] == 'E':
            lon = (float(line[23:26]) + float(line[27:31]) / 6000)
        else:
            lon = (float(line[23:26]) + float(line[27:31]) / 6000) * (-1)
        if lat > minlat and lat < maxlat and lon > minlon and lon < maxlon:
            year = int(line[0:4])
            mon  = int(line[4:6])
            day  = int(line[6:8])
            hh = int(line[8:10])
            mm = int(line[10:12])
            sec  = int(line[12:16])/100
            dep = float(line[31:36])/100
            rms = float(line[48:52])/100
            mag = float(line[123:126])/100
            otime = UTCDateTime(year=year, month=mon, day=day, hour=hh, minute=mm)+sec
            eventid = UTCDateTime(otime, precision=0).isoformat().replace('-', '').replace('T', '').replace(':', '')
            t1, t2 = otime-beforeo, otime+aftero
            lat, lon, dep = float(lat), float(lon), float(dep)
            eventdir = os.path.join(eventsdir, eventid)
            if os.path.isdir(eventdir):
                shutil.rmtree(eventdir)
            os.mkdir(eventdir)
            iok = 1
            print('processing %s'%eventid)
            if not usepicks:
                for ista in stadf.index:
                    stadf.loc[ista, 'distance'] = 0.001 *gps2dist_azimuth(stadf.loc[ista, 'latitude'], 
                                                                          stadf.loc[ista, 'longitude'], 
                                                                          lat, lon)[0]
                stadf = stadf.sort_values(by='distance', ascending=True, ignore_index=True)
                for ista in stadf[:nstations].index:
                    sta = stadf.loc[ista, 'station']
                    mseedfiles = glob.glob(os.path.join(mseeddir, sta, '*.mseed'))
                    st = Stream()
                    for mseedfile in mseedfiles:
                        stt, edt = os.path.basename(mseedfile).replace('.mseed', '').split('__')[-2:]
                        stt, edt = UTCDateTime(stt), UTCDateTime(edt)
                        if (stt > t2) or (edt < t1):
                            pass
                        else:
                            st += read(mseedfile)
                    st = st.select(channel=channel)
                    st.trim(starttime=t1, endtime=t2)
                    st.detrend('demean').detrend('linear').taper(0.05)
                    st.filter('bandpass', freqmin=freqmin, freqmax=freqmax, corners=4, zerophase=True)
                    for tr in st:
                        filename = '{}.{}.{}.{}.SAC'.format(eventid, tr.stats.network, tr.stats.station, tr.stats.channel)
                        filepath = os.path.join(eventdir, filename)
                        tr.stats.sac = {}
                        tr.stats.sac.o = 0
                        tr.stats.sac.b = tr.stats.starttime - otime
                        tr.stats.sac.e = tr.stats.endtime - otime
                        tr.stats.sac.evla = lat
                        tr.stats.sac.evlo = lon
                        tr.stats.sac.evdp = dep
                        tr.stats.sac.mag = mag
                        tr.stats.sac.stla = stadf.loc[ista, 'latitude']
                        tr.stats.sac.stlo = stadf.loc[ista, 'longitude']
                        tr.stats.sac.stel = stadf.loc[ista, 'elevation']
                        tr.stats.sac.dist = stadf.loc[ista, 'distance']
                        tr.write(filepath, format='SAC')
                        print('processing %s'%(filename))
    elif len(line) == 121:
        if usepicks and iok == 1:
            sta = line[0:5].strip()
            net = line[5:7].strip()

            year = int(line[17:21])
            mon  = int(line[21:23])
            day  = int(line[23:25])
            hh   = int(line[25:27])
            mm   = int(line[27:29])

            parr_phase = line[13:15].strip()
            sec  = int(line[29:34])/100
            ptime = UTCDateTime(year=year, month=mon, day=day, hour=hh, minute=mm)+sec
            parr_time = ptime - otime

            sarr_phase = line[46:48].strip()
            sec  = int(line[41:46])/100
            stime = UTCDateTime(year=year, month=mon, day=day, hour=hh, minute=mm)+sec
            sarr_time = stime - otime

            dist = int(line[74:78])/10

            mseedfiles = glob.glob(os.path.join(mseeddir, sta, '*.mseed'))
            st = Stream()
            for mseedfile in mseedfiles:
                stt, edt = os.path.basename(mseedfile).replace('.mseed', '').split('__')[-2:]
                stt, edt = UTCDateTime(stt), UTCDateTime(edt)
                if (stt > t2) or (edt < t1):
                    pass
                else:
                    st += read(mseedfile)
            st = st.select(channel=channel)
            st.trim(starttime=t1, endtime=t2)
            st.detrend('demean').detrend('linear').taper(0.05)
            st.filter('bandpass', freqmin=freqmin, freqmax=freqmax, corners=4, zerophase=True)
            ista = stadf.loc[stadf['station'] == sta].index.tolist()[0]
            for tr in st:
                filename = '{}.{}.{}.{}.SAC'.format(eventid, tr.stats.network, tr.stats.station, tr.stats.channel)
                filepath = os.path.join(eventdir, filename)
                tr.stats.sac = {}
                tr.stats.sac.o = 0
                tr.stats.sac.b = tr.stats.starttime - otime
                tr.stats.sac.e = tr.stats.endtime - otime
                tr.stats.sac.evla = lat
                tr.stats.sac.evlo = lon
                tr.stats.sac.evdp = dep
                tr.stats.sac.mag = mag
                tr.stats.sac.stla = stadf.loc[ista, 'latitude']
                tr.stats.sac.stlo = stadf.loc[ista, 'longitude']
                tr.stats.sac.stel = stadf.loc[ista, 'elevation']
                tr.stats.sac.dist = dist
                if not parr_phase == '':
                    tr.stats.sac.a = parr_time
                if not sarr_phase == '':
                    tr.stats.sac.t0 = sarr_time
                tr.write(filepath, format='SAC')
                print('processing %s %s %s'%(filename, parr_phase, sarr_phase))

# Part two: plot waveforms
for line in lines:
    if len(line) == 180:
        iok = 0
        if line[18] == ' ': #N
            lat = (float(line[16:18]) + float(line[19:23]) / 6000)
        else:
            lat = float(line[16:18]) + float(line[19:23])/6000 * (-1)

        if line[26] == 'E':
            lon = (float(line[23:26]) + float(line[27:31]) / 6000)
        else:
            lon = (float(line[23:26]) + float(line[27:31]) / 6000) * (-1)
        if lat > minlat and lat < maxlat and lon > minlon and lon < maxlon:
            year = int(line[0:4])
            mon  = int(line[4:6])
            day  = int(line[6:8])
            hh = int(line[8:10])
            mm = int(line[10:12])
            sec  = int(line[12:16])/100
            dep = float(line[31:36])/100
            rms = float(line[48:52])/100
            mag = float(line[123:126])/100
            otime = UTCDateTime(year=year, month=mon, day=day, hour=hh, minute=mm)+sec
            eventid = UTCDateTime(otime, precision=0).isoformat().replace('-', '').replace('T', '').replace(':', '')
            eventdir = os.path.join(eventsdir, eventid)
            sacfiles = os.path.join(eventdir, '*.SAC')
            st = read(sacfiles)
            st = st.select(channel=channel)
            for tr in st:
                tr.stats.distance = gps2dist_azimuth(tr.stats.sac.stla, tr.stats.sac.stlo,
                                        tr.stats.sac.evla, tr.stats.sac.evlo)[0]
            fig = plt.figure(facecolor='white', dpi=200)
            st.plot(type='section', recordlength=beforeo+aftero, reftime=otime,
                time_down=False, linewidth=.25, grid_linewidth=.25, show=False, fig=fig)
            ax = fig.axes[0]
            transform = blended_transform_factory(ax.transData, ax.transAxes)
            if usepicks:
                p_arrsvec, p_distvec = [], []
                s_arrsvec, s_distvec = [], []
                for tr in st:
                    ax.text(tr.stats.sac.dist, 1, tr.stats.station, rotation=90,
                    va="bottom", ha="center", transform=transform, zorder=10)
                    if 'a' in tr.stats.sac.keys():
                        p_distvec.append(tr.stats.sac.dist)
                        p_arrsvec.append(tr.stats.sac.a)

                    if 't0' in tr.stats.sac.keys():
                        s_distvec.append(tr.stats.sac.dist)
                        s_arrsvec.append(tr.stats.sac.t0)

                max_dist = max(max(p_distvec), max(s_distvec))
                min_dist = min(min(p_distvec), min(s_distvec))

                ax.scatter(p_distvec, p_arrsvec, c='b', marker='_')
                p_velocity = 1 / curve_fit(ykx, p_distvec, p_arrsvec)[0][0]
                max_time = max_dist / p_velocity
                min_time = min_dist / p_velocity
                ax.plot([min_dist, max_dist], [min_time, max_time], 'b--', label='VP=%.3f km/s'%p_velocity)

                ax.scatter(s_distvec, s_arrsvec, c='r', marker='_')
                s_velocity = 1 / curve_fit(ykx, s_distvec, s_arrsvec)[0][0]
                max_time = max_dist / s_velocity
                min_time = min_dist / s_velocity
                ax.plot([min_dist, max_dist], [min_time, max_time], 'r--', label='VS=%.3f km/s'%s_velocity)

                plt.legend(loc='upper right')
            else:
                for tr in st:
                    ax.text(tr.stats.sac.dist, 1, tr.stats.station, rotation=90,
                    va="bottom", ha="center", transform=transform, zorder=10)
            ax.text(0.05, 0.95, 'Datetime: {}\nMagnitude: {}\nDepth: {} km\nResidual: {} s'.format(eventid, mag, dep, rms), 
                    ha='left', va='top', transform=ax.transAxes)
            fig.tight_layout()
            plt.savefig(os.path.join(eventdir, "waveform.png"))
            plt.close()

# Part three: plot map
stalon_vec = stadf['longitude'].to_numpy()
stalat_vec = stadf['latitude'].to_numpy()
plt.figure(facecolor='white', dpi=150)
plt.scatter(stalon_vec, stalat_vec, marker='^', edgecolors='black', facecolors='none')
plt.axis('equal')
for line in lines:
    if len(line) == 180:
        iok = 0
        if line[18] == ' ': #N
            lat = (float(line[16:18]) + float(line[19:23]) / 6000)
        else:
            lat = float(line[16:18]) + float(line[19:23])/6000 * (-1)

        if line[26] == 'E':
            lon = (float(line[23:26]) + float(line[27:31]) / 6000)
        else:
            lon = (float(line[23:26]) + float(line[27:31]) / 6000) * (-1)
        if lat > minlat and lat < maxlat and lon > minlon and lon < maxlon:
            sc = plt.scatter(lon, lat, marker='*')
            otime = UTCDateTime('{}-{}-{} {}:{}:{}'.format(year, mon, day, hh, mm, sec))
            eventid = UTCDateTime(otime, precision=0).isoformat().replace('-', '').replace('T', '').replace(':', '')
            eventdir = os.path.join(eventsdir, eventid)
            sacfiles = os.path.join(eventdir, '*.SAC')
            st = read(sacfiles, headonly=True)
            st = st.select(channel=channel)
            for tr in st:
                plt.plot([lon, tr.stats.sac.stlo], [lat, tr.stats.sac.stla], linestyle='--', lw=0.4, color=sc.get_facecolors()[0])
plt.tight_layout()
if sc:
    plt.savefig(os.path.join(eventsdir, "map_and_path.png"))
    plt.close()

