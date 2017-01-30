#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Written by Fabian Clevermann <fabian.clevermann@udo.edu>

import optparse
import os.path as op
import os
import time as t
import shutil

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
    confirm = input("Are you sure [y/n]? ")
    if confirm == "y":
        print("I asked you.")
    elif confirm == "n":
        raise SystemExit(0)
    else:
        print("Only 'y' or 'n' is allowed!")
        raise SystemExit(1)

del_dirs = 0
#for i in range(140,141):
for i in range(1,151):
    path = userpath % i
#    print path
    if op.isdir(path):
        for d in os.listdir(path):
            fpath = op.join(path, d)
            if op.isfile(fpath):
                print("%s is a file. Here shouldn't be any files." % fpath)
                if opts.dry_run:
                    print("rm -f %s" % fpath)
                else:
                    os.remove(fpath)
            elif op.isdir(fpath):
                if opts.queue == "all":
                    diff = 0
                else:
                    diff = t.time() - op.getctime(fpath)
    #            print("%s - %s" % (t.time(),op.getctime(path)))
    #            print("diff = %s" % diff)
                if diff > queues[opts.queue]:
                    if opts.dry_run:
    #                    print("shutil.rmtree(%s)" % fpath)
                        if len(os.listdir(fpath)) == 0:
                            print("found empty directory on node%03d" % i)
                        else:
                            printi("found following directories/files on node%03d" % i)
                            for f in os.listdir(fpath):
                                if op.isdir(op.join(fpath,f)):
                                    print("%s/" % f)
                                    for f2 in os.listdir(op.join(fpath,f)):
                                        print("\t %s" % f2)
                                else:
                                    print(f)
                        print("rm -rf %s" % fpath)
                        del_dirs += 1
                    else:
    #                    print("shutil.rmtree(%s)" % fpath)
                        shutil.rmtree(fpath)
                        del_dirs += 1
                else:
                    #print("Ordner zu neu: %s" % fpath)
                    pass
            else:
                print("Something is wrong with %s" % fpath)
                #raise SystemExit(1)
    else:
#        print("Path doesn't exist: %s" % path)
        pass
    if not i % 15:
        print("node%03d finished" % i)
print("Deleted %s directories." % (del_dirs))
