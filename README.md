## EasyMPI: an easy to use MPI profiler
We are going to implement a easy-to-use yet powerful profiler for OpenMPI which aims to provide useful insights to OpenMPI programmers and help them improve their target OpenMPI programs' performance. This project will be based on [Contech](https://github.com/bprail/contech), an instrumentation framework for parallel computing developed by B. P. Railing et al. 

### Schedule (Revised):
Past weeks:
- Week 0 (Wed. 11/01 - Sun. 11/05) Propose the project, meet with Prof. Railing to discuss about questions and issues, study Contech.
- Week 1 (Mon. 11/06 - Sun. 11/12) (A lot of thanks to Prof. Railing, as he configured Contech for MPI on Latedays and started collecting data using our code) Verified that Contech can be used on OpenMPI and started data collection part of the profiler. Studied Contech and tried to configure it on latedays.
- Week 2 (Mon. 11/13 - Sun. 11/19) Collected data from Prof. Railing on Wednesday, begin testing on the collected data and implementing the backend.

Current & future weeks:
- Week 3 (Mon. 11/20 - Sun. 11/26) Finish checkpoint report, finish 80% of backend implementation and testing, start frontend (the web interface) implementation and predictor implementation. 
- Week 4 (Mon. 11/27 - Sun. 12/03) Finish frontend implementation and predictor implementation.
- Week 5 (Mon. 12/04 - Sun. 12/10) Tweak the product, finish project report, finish project poster.

### Demo
The project will be demoed at the poster session on December 12th. An MPI program will be profiled by the profiler, and we will show how it can help the programmers optimize their code based on the profiling result.
