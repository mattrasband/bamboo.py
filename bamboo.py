#!/usr/bin/env python

from __future__ import print_function
import argparse
import collections
from colorama import Fore
try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser
import os
import re
import requests
from subprocess import Popen, PIPE
import sys


BRANCH_PATH = '{server}/rest/api/latest/plan/{project_key}-{build_key}/branch/{branch_name}'


class ExitCode:
    IN_PROGRESS = 1
    PASSED = 0
    FAILED = -1
    EXEC_ERR = 2


class BuildResult(dict):
    def __init__(self, branch=None, result=None, duration=None, passed=None, failed=None,
            skipped=None, href=None, reason=None, sha1=None, relative_time=None, build_number=None):
        self.branch = branch
        self.build_number = build_number
        self.duration = duration
        self.failed = failed
        self.href = href
        self.passed = passed
        self.reason = reason
        self.relative_time = relative_time
        self.result = result
        self.sha1 = sha1
        self.skipped = skipped

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def status(self):
        '''
        Get a status code as to the result.
        :return: Failure(-1), Success(0), In Progress(1)
        '''
        if self.result in ['Success', 'Passed', 'Successful']:
            return ExitCode.PASSED
        elif self.result in 'In Progress':
            return ExitCode.IN_PROGRESS
        else:
            return ExitCode.FAILED


class HTMLStripper(HTMLParser):
    '''
    A loose HTML parser that allows HTML to be stripped from
    strings (e.g. invalid HTML)
    '''
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    @staticmethod
    def strip(string):
        '''
        Strip all HTML elements from a string.
        '''
        stripper = HTMLStripper()
        stripper.feed(string)
        return stripper.get_data()

    def handle_data(self, d):
        self.fed.append(d)
    
    def get_data(self):
        return ''.join(self.fed)


def get_vcs_branch_name_from_cwd():
    with open(os.devnull, 'w') as fnull:
        proc = Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=PIPE, stderr=fnull)
        output, err = proc.communicate()
        if proc.returncode == 0:
            return output.strip()
    return None


def clean_branch_name(branch_name):
    '''
    Clean the branch name for the URL, this isn't a standard urlencode,
    as bamboo drops slashes in favor of hyphens.
    '''
    return re.sub(r' ', '%20', re.sub(r'/', '-', branch_name.decode()))


def query_build_result(server, project_key, build_key, branch_name):
    branch_name = clean_branch_name(branch_name)
    headers = {
        'Accept': 'application/json'
    }
    params = {
        'expand': 'latestResult'
    }
    href = BRANCH_PATH.format(server=server, project_key=project_key, build_key=build_key, branch_name=branch_name)

    resp = requests.get(href, headers=headers, params=params)
    resp.raise_for_status()

    return resp.json()


def parse_result_json(result_json):
    r = BuildResult()

    r.branch = result_json['shortName']

    if 'latestCurrentlyActive' in result_json:
        print('BUILDING: {}'.format(result_json))
        r.result = 'In Progress'
    else:
        latest_res = result_json['latestResult']
        r.result = latest_res['buildState']
        r.duration = latest_res['buildDuration']
        r.passed = latest_res['successfulTestCount']
        r.failed = latest_res['failedTestCount']
        r.skipped = latest_res['skippedTestCount']
        r.reason = HTMLStripper.strip(latest_res['buildReason'])
        r.sha1 = latest_res['vcsRevisionKey']
        r.relative_time = latest_res['buildRelativeTime']
        r.build_number = latest_res['buildNumber']

    return r


def print_result(build_result, verbose=False):
    if build_result.result in ['Passed', 'Successful', 'Success']:
        print(Fore.GREEN + 'Passed' + Fore.RESET)
    elif build_result.result == 'In Progress':
        print(Fore.YELLOW + 'In Progress' + Fore.RESET)
    else:
        fmt = [
            build_result.passed,
            build_result.failed,
            build_result.skipped
        ]
        print(Fore.RED + 'Failure: Passed {}, Failed {}, Skipped {}'.format(*fmt) + Fore.RESET)

    if verbose:
        ordered = collections.OrderedDict(sorted(build_result.items(), key=lambda t: t[0]))
        for k, v in ordered.items():
            print('\t{}: {}'.format(k, v))


def main():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Get a build result from bamboo.')
    parser.add_argument(
            '--branch',
            dest='branch',
            default=get_vcs_branch_name_from_cwd(),
            type=str,
            help='VCS branch name to check the results of. If none is provided \
                    and execution is from a repository, the current branch will \
                    be used')
    parser.add_argument(
            '--project',
            type=str,
            required=True,
            help='Project plan the build belongs to.')
    parser.add_argument(
            '--plan',
            type=str,
            required=True,
            help='Specific plan the build ran on.')
    
    parser.add_argument(
            '--server',
            type=str,
            required=True,
            help='Bamboo server path, this should be in the format http://bamboo.mydomain.com, or http://mydomain.com/bamboo.')
    parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='Verbose output.')
    args = parser.parse_args()

    if not args.branch:
        parser.error('--branch must not be empty.')

    try:
        build_result = query_build_result(args.server, args.project, args.plan, args.branch)    
        result = parse_result_json(build_result)
        print_result(result, args.verbose)
        sys.exit(result.status())
    except requests.exceptions.HTTPError as e:
        print('Error with request:', e)
        sys.exit(ExitCode.EXEC_ERR)
    except Exception as e:
        print('Error locating branch, it may have not built yet?', e)
        sys.exit(ExitCode.EXEC_ERR)


if __name__ == '__main__':
    main()

