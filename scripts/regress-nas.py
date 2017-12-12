#!/usr/bin/env python
import os
import util
import glob
import json
import argparse
import scrape_build
import scrape_run
import aggregate_scrape_run
import time

def main():
    parser = argparse.ArgumentParser(description=
    """Run a bunch of jobs to collect various statistics about contech.
    1. Recompile all parsec benchmarks for bldconf's contech and llvm.
    2. Run all parsec benchmarks using both bldconfs.
    3. Run output aggregation scripts to collect the data and format into a table.
    """)
    parser.add_argument("-i", "--inputs", help="The input sets to run", default="S W A") 
    parser.add_argument("-n", "--numthreads", help="The number of threads to run.", default="16")
    parser.add_argument("-b", "--benchmarks", help="The benchmarks to run", default="")
    args = parser.parse_args()
    if args.benchmarks == "":
        args.benchmarks = util.Benchmarks.nas
    else:
        args.benchmarks = args.benchmarks.split(" ")
    args.inputs = args.inputs.split(" ")
    
    regressContech(inputs=args.inputs, numthreads=args.numthreads, benchmarks=args.benchmarks)

def regressContech(inputs, numthreads, benchmarks):
 
    if os.environ.has_key("NAS_HOME"):
        NAS_HOME = os.environ["NAS_HOME"]
    else:
        print ">Error: Could not find NAS installation. Set NAS_HOME to the root of your NAS directory."
        exit(1)

    # Rebuild benchmarks
    # NAS must be built sequentially
    compileJobIds = []
    for input in inputs:
        for b in benchmarks:
            x = compilationTimeCompare(b, input)
            compileJobIds.append(x)
            util.waitForJobs(x)
    time.sleep(10)    #Wait for files to be copied back
    buildRoot = scrape_build.processAll([util.getFileNameForJob(j) for j in compileJobIds])
    
    # Run the benchmarks
    os.environ["TIME"] = '{"real":%e, "user":%U, "sys":%S, "mem":%M }'
    for input in inputs:
        runJobIds = []
        runJobIds.extend([statsRun(b, numthreads, input, "contech") for b in benchmarks])
        runJobIds.extend([nativeRun(b, numthreads, input) for b in benchmarks])
        util.waitForJobs(runJobIds)
        root = buildRoot + scrape_run.processAll([util.getFileNameForJob(j) for j in runJobIds])
    
        # Aggregate output
        table = aggregate_scrape_run.aggregate(root)
        aggregate_scrape_run.computeSlowdown(table)
        aggregate_scrape_run.generateCsv(table, "results-{}.csv".format(input))
        
def compilationTimeCompare(benchmark, input):
    CONTECH_HOME = util.findContechInstall()
    script = """
    cd $CONTECH_HOME/scripts
"""
    
    test = """
    # {0}
    ./build_nas.py {0} -i {3} -c llvm | {1}   
    ./build_nas.py {0} -i {3} -c contech | {2}
"""
    label = "sed s/'Build'/'{0}'/ "
    script += test.format(benchmark, label.format(benchmark+"-llvm"), label.format(benchmark+"-contech"), input)
    
#     print script
    return util.quicksub(name="timed_compilation_{}".format(benchmark), code=script, resources=["nodes=1:ppn=1,pmem=1gb"], queue="newpasta")

def nativeRun(benchmark, n, input):
    PARSEC_HOME = util.findParsecInstall()
    script = """
    mkdir /tmp/$USER
    cp $NAS_HOME/bin-llvm/{0}.{2}.x /tmp/$USER
    cd /tmp/$USER
    setenv OMP_NUM_THREADS {1}
    /usr/bin/time /tmp/$USER/{0}.{2}.x 
    cd -
    rm -f /tmp/$USER/*
"""
    script = script.format(benchmark, n, input)
    jobName = "llvm_{}_{}_{}".format(input,  n, benchmark)
    print jobName
    return util.quicksub(name=jobName, code=script, resources=["nodes=1:ppn=24,pmem=1gb"], queue="newpasta")
    
def statsRun(benchmark, n, input, option):
       
    CONTECH_HOME = util.findContechInstall()
    if os.environ.has_key("CONTECH_OUTDIR"): 
        script = """
    cd $CONTECH_HOME/scripts
    
    ./run_nas.py {0} -n {1} -i {2} {3} --backends stats
    rm -f --verbose $CONTECH_OUTDIR/{0}.contech.trace
    rm -f --verbose $CONTECH_OUTDIR/{0}.taskgraph;
"""
    else:
        script = """
    cd $CONTECH_HOME/scripts
    
    ./run_nas.py {0} -n {1} -i {2} {3} --backends stats
    rm -f --verbose /tmp/{0}.contech.trace
    rm -f --verbose /tmp/{0}.taskgraph;
"""
    options = {"discard": "--discardTrace",
               "pin" : "--pinFrontend",
               "contech" :  "",
               "contechmarker" : ""}
    
    script = script.format(benchmark, n, input, options[option])
    jobName = "{}_{}_{}_{}".format(option, input,  n, benchmark)
    print jobName
    return util.quicksub(name=jobName, code=script, resources=["nodes=1:ppn=24,pmem=1gb"], queue="newpasta")
    
    
if __name__ == "__main__":
    main()
