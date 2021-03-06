import traceback
import re
from collections import Counter
import argparse
import time, datetime
import sys

logEnabled = 0

path = '/home/cerebro84/Downloads/access_log'
regex = re.compile(("(?P<ip_from>[\d\.]+) - - "
                                        "\[(?P<datetime>.*?)\]"
                                        " \"(?P<operation>\w+) "
                                        "*(?P<url>.*?)\s"
                                        "(?P<protocol>.*?)\"\s"
                                        "(?P<responseCode>\d+)\s"
                                        "(?P<responseTime>\d+)"
                                        ))

class Stats:
    pagesToNumberOfAccesses = Counter()
    unsuccessfulPages = Counter()
    successful = 0
    unsuccessful = 0
    ipToNumberOfAccesses = Counter()
    ipToPages = {}
    accessesPerMinute = {} # Counter()

def get_dict_from_line(line):
    if logEnabled:
        print 'processing line ' + line
    match = regex.match(line)
    if match:
        dict = match.groupdict()
        if logEnabled:
            print(dict)
        timezone = dict.get("datetime")[-5:]
        minute = datetime.datetime.strptime (dict.get("datetime")[0:17], "%d/%b/%Y:%H:%M")
        universalMinute = minute - datetime.timedelta(hours=int(timezone[0:3]), minutes=int(timezone[-2]))
        dict['truncDate'] = universalMinute
        urlWithParamters = dict.get('url')
        questionMarkPosition = urlWithParamters.find("?")
        if ~questionMarkPosition:
            justTheUrl = urlWithParamters[0:questionMarkPosition]
        else:
            justTheUrl = urlWithParamters
        dict['justTheUrl'] = re.sub(r'[/]+', r'/',justTheUrl)
        return dict
    else:
        print 'WEIRD line did not match: ' + line

def add_data_from(line, stats, flags):
    """Adds data read from line (String) to maps"""
    dict = get_dict_from_line(line)
    if flags is None or flags.all_per_min:
        if (stats.accessesPerMinute.get(dict.get('universalMinute')) is None):
             stats.accessesPerMinute[dict.get('universalMinute')] = 1
        else:
            stats.accessesPerMinute[dict.get('universalMinute')] +=1
    ipFrom = dict.get('ip_from')
    if flags is None or flags.top_url_per_top_ip or flags.top_ips: #avoid consuming op
        stats.ipToNumberOfAccesses[ipFrom]+=1
    urlWithParamters = dict.get('url')
    questionMarkPosition = urlWithParamters.find("?")
    if ~questionMarkPosition:
        justTheUrl = urlWithParamters[0:questionMarkPosition]
    else:
        justTheUrl = urlWithParamters
    justTheUrl = re.sub(r'[/]+', r'/',justTheUrl)
    if stats.ipToPages.get(ipFrom) is None:
        stats.ipToPages[ipFrom] = Counter()
    stats.ipToPages[ipFrom][justTheUrl] += 1

    if (flags is None or flags.top_req_pages): #avoid consuming op
        stats.pagesToNumberOfAccesses[justTheUrl]+=1 #removing repeated forward slashes
    responseTime = dict.get('responseTime')
    if (int(responseTime) >= 200 and int(responseTime) <= 300):
        stats.successful+=1
    else:
        stats.unsuccessful+=1
        if flags is None or flags.top_uns_pages: #avoid consuming op
            stats.unsuccessfulPages[justTheUrl]+=1
    if logEnabled:
        print('Just the url: ' + justTheUrl)

def main():
    parser = argparse.ArgumentParser(description='Gathers stats for apache logs')
    parser.add_argument('--top-requested-pages', '-r', dest='top_req_pages', action='store_true',
                   help='Reports the top 10 requested pages and the number of requests made for each')
    parser.add_argument('--top-unsuccessful-pages', '-u', dest='top_uns_pages', action='store_true',
                   help='Reports the top 10 requested pages and the number of requests made for each')
    parser.add_argument('--top-ips', '-i', dest='top_ips', action='store_true',
                   help='Reports the top 10 requested pages and the number of requests made for each')
    parser.add_argument('--show-successful', '-s', dest='successful', action='store_true',
                   help='Reports percentage of successful requests')
    parser.add_argument('--show-unsuccessful', '-n', dest='unsuccessful', action='store_true',
                   help='Reports percentage of unsuccessful requests')
    parser.add_argument('--all-per-minute', '-m', dest='all_per_min', action='store_true',
                   help='Reports the total number of requests made every minute in the entire time period covered by the file provided')
    parser.add_argument('--top-urls-per-ip', '-l', dest='top_url_per_top_ip', action='store_true',
                   help='Reports for each of the top 10 IPs, the top 5 pages requested and the number of requests for each.')
    args = parser.parse_args()
    noargs = not len(sys.argv) > 1
    stats = Stats()

    try:
        #for i in range(1, 2):
            #print i
            for line in open(path):
                add_data_from(line, stats, None if noargs else args)
    except Exception as e:
        traceback.print_exc()
        exit(-1)

    try:
        f = open('output','w')
        if noargs or args.top_req_pages:
            f.write("Top 10 requested pages and the number of requests made for each:\n")
            for (page, requests) in stats.pagesToNumberOfAccesses.most_common(10):
                f.write(page)
                f.write(': ' )
                f.write(str(requests))
                f.write('\n')
            f.write('\n')
        if noargs or args.successful:
            f.write("Percentage of successful requests: ")
            f.write(str((float(stats.successful)/(stats.unsuccessful+stats.successful))*100)+'%')
            f.write('\n\n')
        if noargs or args.unsuccessful:
            f.write("Percentage of unsuccessful requests: ")
            f.write(str((float(stats.unsuccessful)/(stats.unsuccessful+stats.successful))*100)+'%')
            f.write('\n\n')
        if noargs or args.top_uns_pages:
            f.write("Most unsuccessful: \n")
            for (page, requests) in stats.unsuccessfulPages.most_common(10):
                f.write(page)
                f.write(': ' )
                f.write(str(requests))
                f.write('\n')
            f.write('\n')
        if noargs or args.top_ips:
            f.write("The top 10 IPs making the most requests, displaying the IP address and number of requests made: \n")
            for (page, requests) in stats.ipToNumberOfAccesses.most_common(10):
                f.write(page)
                f.write(': ' )
                f.write(str(requests))
                f.write('\n')
            f.write('\n')
        if noargs or args.all_per_min:
            f.write("The total number of requests made every minute in the entire time period covered by the file provided: \n")
            for date, accesses in stats.accessesPerMinute.iteritems():
                f.write(str(date))
                f.write(': ' )
                f.write(str(accesses))
                f.write('\n')
            f.write('\n')
        if noargs or args.top_url_per_top_ip:
            f.write("For each of the top 10 IPs, show the top 5 pages requested and the number of requests for each: \n")
            for (ip, requests) in stats.ipToNumberOfAccesses.most_common(10):
                f.write(page)
                f.write(': \n' )
                for page, views in stats.ipToPages.get(ip).most_common(5):
                    f.write('\t')
                    f.write(page)
                    f.write(': ')
                    f.write(str(views))
                    f.write('\n')
                f.write('\n')
            f.write('\n')
    except Exception as e:
        traceback.print_exc()
        exit(-1)



main()
