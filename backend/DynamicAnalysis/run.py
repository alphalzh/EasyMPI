#!/usr/bin/env python

import os
import sys
import argparse
sys.path.append(os.path.join(os.environ["CONTECH_HOME"], "scripts"))
import util
import subprocess
import shutil
import tempfile

def main(arg):
    # TODO: usage should be based on argparse
    if (len(arg)) == 1:
        print "Usage: {0} input\n".format(arg[0])
        exit()
    
    parser = argparse.ArgumentParser(description="Runs dynamic analysis backend on benchmark")
    parser.add_argument("-b", "--bitcode", help="Bitcode file to analyze")
    parser.add_argument("-t", "--taskgraph", help="Taskgraph file to analyze")
    parser.add_argument("-o", default="output", help="Output directory")
    parser.add_argument("-n", default="65", help="Number of contexts to analyze")
    args = parser.parse_args()
    
    DynAnalysisLib = "-load=lib/LLVMDynAnalysis.so"
    ExecLatency = "-execution-units-latency={1,2,3,1,3,5,6,1,4,4,12,12,30,30,100,100}"
    ROBSize = "-reorder-buffer-size=168"
    LBSize = "-load-buffer-size=64"
    SBSize = "-store-buffer-size=36"
    CacheLineSize = "-cache-line-size=64"
    ILP = "-instruction-fetch-bandwidth=4"
    RSSize = "-reservation-station-size=56"
    L1Size = "-l1-cache-size=32768"
    L2Size = "-l2-cache-size=262144"
    LLCSize = "-llc-cache-size=20971520"
    ExecIssue = "-execution-units-parallel-issue={1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1}"
    ExecThru = "-execution-units-throughput={3,1,1,1,1,1,1,1,8,8,32,32,32,32,8,8}"
    FillBufSize = "-line-fill-buffer-size=10"
    WordSize = "-memory-word-size=8"
    AccessGran = "-mem-access-granularity={8,8,64,64,64,64,64,64}"
    
    # Assume that the taskgraph is formatted according to regress / util script convention
    benchName = args.taskgraph.split('/')[-1]
    b = benchName.split('.')

    if (b[0] == "splash2x"):
        benchName = b[1]
    else:
        benchName = b[0]
    
    try:
        os.makedirs(args.o + "/" + benchName)
    except os.error:
        #path already exists
        arg = arg
    
    for ctid in range(int(args.n)):
        filename = args.o + "/" + benchName + "/ct_{0}".format(ctid)
        ofile = tempfile.NamedTemporaryFile(suffix=".bc")
        with open(filename, "w") as of:
            #Use bash to expand arguments per https://stackoverflow.com/questions/8945826/expand-shell-path-expression-in-python
            util.pcall(["bash -c \" opt", DynAnalysisLib, "-EnginePass", args.bitcode, "-taskgraph-file=" + args.taskgraph,
                        "-o " + ofile.name, "-context-number={0}".format(ctid), 
                        ExecLatency, ROBSize, LBSize, SBSize, CacheLineSize, ILP, RSSize, L1Size,
                        L2Size, LLCSize, ExecIssue, ExecThru, FillBufSize, WordSize, AccessGran, "\""],
                        outputFile=of, suppressOutput=False, silent=False)
        ofile.close()
        try:
            os.unlink(ofile.name)
        except os.error:
            # we expect that there will be an error returned by the unlink
            #   The file should already be deleted, but we are calling just in case
            arg = arg

if __name__ == "__main__":
    main(sys.argv)
