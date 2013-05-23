#!/usr/bin/env python
"""
Test driver
Runs off plain text files, similar to how PHP's test harness works
"""
import subprocess
import os
import glob

def run(args):
    """
    Runs a command and returns stdout output, throws exception on failed run.
    Uses python's 2.7 check_output if available otherwise uses something else
    """

    try:
        getattr(subprocess, 'check_output')
        has_check_output = True
    except AttributeError:
        has_check_output = False

    if has_check_output:
        # 2.7
        return subprocess.check_output(args)
    else:
        # not 2.7
        aprocess = subprocess.Popen(args,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        (stdoutdata, stderrdata) = aprocess.communicate()
        if aprocess.returncode != 0:
            raise Exception("Test died!: " + stderrdata)
        return stdoutdata

def readtestdata(filename):
    """
    Read a test file and split into components
    """

    state = None
    info = {
        '--TEST--': '',
        '--INPUT--': '',
        '--EXPECTED--': ''
        }

    for line in open(filename, 'r'):
        line = line.rstrip()
        if line in ('--TEST--', '--INPUT--', '--EXPECTED--'):
            state = line
        elif state:
            info[state] += line + '\n'

    # remove last newline from input
    info['--INPUT--'] = info['--INPUT--'][0:-1]

    return (info['--TEST--'], info['--INPUT--'], info['--EXPECTED--'])

def runtest(testname):
    """
    runs a test, optionally with valgrind
    """
    data =  readtestdata(os.path.join('../tests', testname))

    command = os.getenv('PARSER_CMD', './sqli')

    if os.environ.get('VALGRIND', None):
        args = ['valgrind',
                '--gen-suppressions=no',
                '--read-var-info=yes',
                '--leak-check=full',
                '--error-exitcode=1',
                '--track-origins=yes',
                '--xml=yes',
                '--xml-file=valgrind-'+ testname.replace('.txt', '.xml'),
                command, data[1]]
        actual = run(args)
    else:
        actual = run([command, data[1]])

    if actual.strip() != data[2].strip():
        print "INPUT: \n" + data[1]
        print
        print "EXPECTED: \n" + data[2]
        print "GOT: \n" + actual
        assert False

def test_unit():
    for testname in sorted(glob.glob('../tests/test-*.txt')):
        testname = os.path.basename(testname)
        yield runtest, testname

if __name__ == '__main__':
    import sys
    sys.stderr.write("run using nosetests\n")
    sys.exit(1)
