import os
import yaml

with open('./configuration.yaml', 'r') as f:
    cfgs = yaml.safe_load(f)

input_model = os.path.join(cfgs['Cwd'], cfgs['Hypoinv']['input_model'])
input_station = os.path.join(cfgs['Cwd'], cfgs['Hypoinv']['input_station'])
phase_files = os.path.join(cfgs['Cwd'], cfgs['Hypoinv']['phase_files'])
params_file = os.path.join(cfgs['Cwd'], cfgs['Hypoinv']['params_file'])
err_hor = cfgs['Hypoinv']['err_hor']
err_dep = cfgs['Hypoinv']['err_dep']
max_gap = cfgs['Hypoinv']['max_gap']
max_rms = cfgs['Hypoinv']['max_rms']

os.chdir(cfgs['Hypoinv']['run_hypoinv_dir'])

# model
os.system('python mk_velmodel.py {}'.format(input_model))
# phase
os.system('cat {} > phase_sel_all.txt'.format(phase_files))
os.system('python mk_inputfile.py phase_sel_all.txt {} > hypoinput.arc'.format(input_station))
os.system('rm phase_sel_all.txt')
# run hypoinverse
os.system('hyp1.40 < {}'.format(params_file))
# screen out some eqs
os.system('python convertformat_outputfile.py hypoOut.arc new.cat dele.cat {} {} {} {}'.format(err_hor, err_dep, max_gap, max_rms))

os.chdir(cfgs['Cwd'])
