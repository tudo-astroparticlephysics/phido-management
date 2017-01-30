#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Written by Fabian Clevermann <fabian.clevermann@udo.edu>

import optparse
import os.path as op
import os
import time as t
import shutil
from commands import getstatusoutput
p = optparse.OptionParser()

p.add_option("-u","--user",action="store",dest="user",default=os.environ["USER"], help="default = $USER")

queues = ["short", "one_day","three_days","one_week","four_weeks","eternal","all"]
p.add_option("-q","--queue", action="store",dest="queue", choices=queues, default="eternal", help="Choose one queue out of " + ", ".join(queues) + ". Choose 'all' to delete everything. default = eternal")

p.add_option("--dry-run", "-n", "--just-print", action="store_true", dest="dry_run", default=False,help="Print the commands that would be executed, but do not execute them.")

p.add_option("--yes", "-y", action="store_true", dest="yes", default=False, help="Assume yes, no questions asked.")

p.set_usage("del_localdisks [options]")

opts, args = p.parse_args()

queues = {
"all"        :          -1,
"short"      :    6 * 3600,
"one_day"    :   24 * 3600,
"three_days" :   72 * 3600,
"one_week"   :  168 * 3600,
"four_weeks" :  672 * 3600,
"eternal"    : 8760 * 3600}

userpath = "/net/node%03d/local/" + str(opts.user)

print("Selected user: %s" % opts.user)
print("Selected queue: %s" % opts.queue)
print("Dry_run: %s" % opts.dry_run)

if opts.dry_run:
    print("Nothing happens, only commands will be printed.")
else:
    print("All directories in /local/%s on all nodes will be deleted if the last modification date is longer in the past than the maximum walltime for the %s queue!" % (opts.user,opts.queue))

if not opts.yes:
    confirm = raw_input("Are you sure [y/n]? ")
    if confirm == "y":
        print("I asked you.")
    elif confirm == "n":
        raise SystemExit(0)
    else:
        print("Only 'y' or 'n' is allowed!")
        raise SystemExit(1)
def my_remove( fpath ):
  if opts.dry_run:
    print("rm -f %s" % fpath)
  else:
    os.remove(fpath)


del_dirs = 0
total_size_in_mb = 0
for i in range(1,151):
    if i == 50:
        print "Skipping node 50!"
        continue
    path = userpath % i
    if not op.isdir(path):
        print "path doesn't exist", path
        continue
    for d in os.listdir(path):
        fpath = op.join(path, d)
        if op.isfile(fpath):
            print("%s is a file. Here shouldn't be any files." % fpath)
            my_remove(fpath)
        elif op.isdir(fpath):
            diff = t.time() - op.getctime(fpath)
            dirname = op.split(fpath)[1]
            st,ou = getstatusoutput( "qstat -f " + dirname)
            if diff > queues[opts.queue] and st==39168:
                if opts.dry_run:
                    if len(os.listdir(fpath)) == 0:
                        print "found empty directory on node%03d" %(i)
                    else:
                        print "found following directories/files in \n\t", fpath
                        for root, dirs, files in os.walk( fpath ):
                            for filename in files:
                                print op.join( root, filename), op.getsize(op.join( root, filename))
                                total_size_in_mb += float(op.getsize(op.join( root, filename)))/(1024.*1024.)
                    print("rm -rf %s" % fpath)
                    del_dirs += 1
                else:
                    shutil.rmtree(fpath)
                    del_dirs += 1
            else:
                #print("Ordner zu neu: %s" % fpath)
                pass
        else:
            print("Something is wrong with %s" % fpath)
            #raise SystemExit(1)
    print("node%03d finished" % i)
print("Deleted %s directories." % (del_dirs))
print "Deleted a total of", total_size_in_mb, "MB"
