import os
import glob
import yaml
import pandas as pd


with open('./configuration.yaml', 'r') as f:
    cfgs = yaml.safe_load(f)

f_taup_tt = open(os.path.join(cfgs['REAL']['run_real_dir'], 'tt_db/taup_tt.py'), 'r')
f_taup_tt_source = f_taup_tt.read()
f_taup_tt.close()

f_taup_tt_source = f_taup_tt_source.replace('DIST_RANGE_IN_DEG_KEY', '%s'%cfgs['REAL']['dist_range_in_deg'])
f_taup_tt_source = f_taup_tt_source.replace('DEPTH_IN_KM_KEY', '%s'%cfgs['REAL']['depth_in_km'])
f_taup_tt_source = f_taup_tt_source.replace('DIST_INTERVAL_KEY', '%s'%cfgs['REAL']['dist_interval'])
f_taup_tt_source = f_taup_tt_source.replace('DEPTH_INTERVAL_KEY', '%s'%cfgs['REAL']['depth_interval'])

f_taup_tt_temp = open(os.path.join(cfgs['REAL']['run_real_dir'], 'tt_db/taup_tt_temp.py'), 'w')
f_taup_tt_temp.writelines(f_taup_tt_source)
f_taup_tt_temp.close()

os.chdir(os.path.join(cfgs['REAL']['run_real_dir'], 'tt_db'))
taup_tt_output = os.system('python taup_tt_temp.py')
print('STATUS: {}'.format(taup_tt_output))
os.chdir(cfgs['Cwd'])


df = pd.read_csv(cfgs['REAL']['stations_text'])
sta_dict = {}
for i in df.index:
    sta = df.loc[i, 'station']
    net = df.loc[i, 'network']
    code= net+'.'+sta
    if code not in sta_dict.keys():
        sta_dict[code] = {}
        sta_dict[code]['channels'] = [df.loc[i, 'channel']]
        sta_dict[code]['coords'] = [round(float(df.loc[i, 'latitude']), 6), 
                                   round(float(df.loc[i, 'longitude']), 6), 
                                   round(float(df.loc[i, 'elevation'])/1000, 3)]
    else:
        sta_dict[code]['channels'].append(df.loc[i, 'channel'])

with open(cfgs['REAL']['stations_real'], 'w') as w:
    for code in sta_dict.keys():
        net, sta = code.split('.')
        channels = sorted(sta_dict[code]['channels'])
        cha = channels[-1]
        lat, lon, ele = sta_dict[code]['coords']
        w.writelines('%.6f %.6f %s %s %s %.3f\n'%(lon, lat, net, sta, cha, ele))

r_key = cfgs['REAL']['r_key']
g_key = cfgs['REAL']['g_key']
v_key = cfgs['REAL']['v_key']
s_key = cfgs['REAL']['s_key']
station = cfgs['REAL']['stations_real']
f_ttime = os.path.join(cfgs['REAL']['run_real_dir'], 'tt_db/ttdb.txt')
####
daily_pick_dirs = sorted(glob.glob(cfgs['REAL']['pks_4_REAL_dir']))

for daily_pick_dir in daily_pick_dirs:
    yyyymmdd = os.path.basename(daily_pick_dir)
    year = yyyymmdd[0:4]
    month = yyyymmdd[4:6]
    day = yyyymmdd[6:8]
    f_perl = open(os.path.join(cfgs['REAL']['run_real_dir'], 'runREAL.pl'), 'r')
    f_perl_source = f_perl.read()
    f_perl.close()
    f_perl_source = f_perl_source.replace('YEAR_KEY', year)
    f_perl_source = f_perl_source.replace('MON_KEY', month)
    f_perl_source = f_perl_source.replace('DAY_KEY', day)
    f_perl_source = f_perl_source.replace('DIR_KEY', daily_pick_dir)
    f_perl_source = f_perl_source.replace('STATION_KEY', station)
    f_perl_source = f_perl_source.replace('TTIME_KEY', f_ttime)
    f_perl_source = f_perl_source.replace('R_KEY', r_key)
    f_perl_source = f_perl_source.replace('G_KEY', g_key)
    f_perl_source = f_perl_source.replace('V_KEY', v_key)
    f_perl_source = f_perl_source.replace('S_KEY', s_key)
    f_perl_temp = open(os.path.join(cfgs['REAL']['run_real_dir'], 'runREAL_temp.pl'),'w')
    f_perl_temp.write(f_perl_source)
    f_perl_temp.close()
    
    real_output = os.system('perl %s'%(os.path.join(cfgs['REAL']['run_real_dir'], 'runREAL_temp.pl')))
    print('{} {} {} ...... STATUS: {}'.format(year, month, day, real_output))
    
    os.rename('./catalog_sel.txt', '{}.catalog_sel.txt'.format(yyyymmdd))
    os.rename('./hypolocSA.dat', '{}.hypolocSA.dat'.format(yyyymmdd))
    os.rename('./hypophase.dat', '{}.hypophase.dat'.format(yyyymmdd))
    os.rename('./phase_sel.txt', '{}.phase_sel.txt'.format(yyyymmdd))
    
# merge all daily outputs
os.system('mv *.catalog_sel.txt *.hypolocSA.dat *.hypophase.dat *.phase_sel.txt %s'%cfgs['REAL']['run_real_dir'])
os.chdir(cfgs['REAL']['run_real_dir'])
os.system('perl ./combine_and_select.pl')
os.chdir(cfgs['Cwd'])



