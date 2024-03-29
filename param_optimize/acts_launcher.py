import datetime
import os
import re
import shutil
import subprocess


def gen_logfile_name(postfix=''):
    now = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(now, '%Y-%d-%m-%H-%M-%S')
    return f"acts_{timestamp}{postfix}.txt"


def save_log(path, stdout, zip_log=True):
    fshort = gen_logfile_name()
    fname = os.path.join(path, fshort)
    with open(fname, 'w') as f:
        f.write(stdout)
    if zip_log:
        subprocess.run(['gzip', fname])


def get_mpdroot_bin_path():
    try:
        bin_path = os.environ['VMCWORKDIR']
    except:
        print('VMCWORKDIR environment variable is not set. '
              'Please run config/env.sh.')
        raise
    return bin_path


def run_acts(
        json_fname,
        infile=None,
        outfile=None,
        start_event=None,
        n_events=None):

    bin_path = get_mpdroot_bin_path()
    macro = os.path.join(bin_path, 'macros', 'common', 'trackingActs.C')
    outfile_full = os.path.join(bin_path, outfile)
    macro_s = f'{macro}("{infile}", "{outfile}", {start_event}, {n_events})'
    cmd_l = ['root', '-q', '-b', f"'{macro_s}'"]
    cmd_s = ' '.join(cmd_l)
    out = subprocess.run(
            cmd_s, text=True, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return out.stdout


def parse_line(line, recompile):
    match = recompile.match(line)
    if not match:
        return
    val_s = match.group(1)
    val = None
    try:
        val = float(val_s)
    except:
        print(f'Error: can not convert "{val_s}" to float')
    return val


def parse_output(arg):
    eff_sel_compile  = re.compile("^Total efficiency.*selected particles.* (.*)$")
    eff_all_compile  = re.compile("^Total efficiency.*all particles.* (.*)$")
    fake_sel_compile = re.compile("^Total fake rate.*selected particles.* (.*)$")
    fake_all_compile = re.compile("^Total fake rate.*all particles.* (.*)$")

    eff_sel  = None
    eff_all  = None
    fake_sel = None
    fake_all = None
    arg_sp = arg.split(os.linesep)

    for l in arg_sp:
        if (v1 := parse_line(l, eff_sel_compile))  is not None: eff_sel  = v1
        if (v2 := parse_line(l, eff_all_compile))  is not None: eff_all  = v2
        if (v3 := parse_line(l, fake_sel_compile)) is not None: fake_sel = v3
        if (v4 := parse_line(l, fake_all_compile)) is not None: fake_all = v4

    eff_sel  = -1 if eff_sel  is None else eff_sel
    eff_all  = -1 if eff_all  is None else eff_all
    fake_sel = -1 if fake_sel is None else fake_sel
    fake_all = -1 if fake_all is None else fake_all

    return eff_sel, eff_all, fake_sel, fake_all

# Run ACTS, parse stdout, return some values.
# This value must be non-negative. Otherwise some error occured.
def run(
        json_fname,
        infile='/home/vvburdelnaya/tracker/mpdroot/evetest.root',
        outfile='',
        start_event=0,
        n_events=2,
        log=False,
        log_dir=''):
    bin_path = get_mpdroot_bin_path()
    shutil.copy(json_fname, os.path.join(bin_path, 'etc'))
    if not outfile:
        outfile = os.path.join(bin_path, 'macros', 'common', 'dst.root')

    stdout = run_acts(
        json_fname,
        infile=infile,
        start_event=start_event,
        n_events=n_events,
        outfile=outfile)
    if log:
        save_log(log_dir, stdout)
    eff_sel, eff_all, fake_sel, fake_all = parse_output(stdout)
    return eff_sel, eff_all, fake_sel, fake_all

# test
#infile = '/path/to/input/root/file'
#json = '/path/to/acts_params_config.json'
#
#eff = run(json, infile=infile, log=True, log_dir='/tmp')
#print(f"eff = {eff}")
