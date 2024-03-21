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
        bin_path = os.environ['MPDROOT']
    except:
        print('MPDROOT environment variable is not set. '
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
    rout = subprocess.run(
            cmd_s, text=True, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return rout.stdout


def parse_output(arg):
    val_s = None
    recompile = re.compile("^Total efficiency \\(nReco\\).* (.*)$")

    arg_sp = arg.split(os.linesep)

    for l in arg_sp:
        match = recompile.match(l)
        if not match:
            continue
        val_s = match.group(1)
    val = -1
    try:
        val = float(val_s)
    except:
        print(f'Error: can not convert "{val_s}" to float')
    return val

# Run ACTS, parse stdout, return some value.
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
    val = parse_output(stdout)
    return val

# test
# infile = '/root/file'
# json = '/path/to/json/file'
#
# eff = run(json, infile=infile, log=True, log_dir='/tmp')
# print(f"eff = {eff}")
