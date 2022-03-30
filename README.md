# *SimpleCGRA*
*SimpleCGRA*: An Open-Source Platform for Temporal-Mapping CGRAs

We are still tidying the codes of SimpleCGRA. The codes of all modules are available. We will keep improving *SimpleCGRA*. 

## How to compile and run *SimpleCGRA*?

>* Most modules of *SimpleCGRA* are written in Python. We test *SimpleCGRA* on *anaconda* and *python 3.7*.  

>* Install the dependencies: 
```
conda create -n scip python=3.7
conda activate scip
conda install matplotlib scikit-learn networkx xmltodict scip graphviz pyscipopt cvxpy -c conda-forge
pip install graphviz
```

>* Run the benchmark
```
export SET=express
export BENCH=cosine2
python3 ./test/pnr.py ./benchmark/${SET}/${BENCH}/${BENCH}_DFG.txt ./benchmark/${SET}/${BENCH}/${BENCH}_compat.txt \
        -p ./benchmark/${SET}/${BENCH}/${BENCH}_param.txt 
```
>>* The default mapping parameters will be used if ./test/pnr.py is run without "-p xxx_param.txt ". 

>* Compilation is optional. It is needed if you want to use the front-end or use the C++ interface. 
>>* You can compile *SimpleCGRA* by running "make". The front-end is tested in LLVM 11.  

## Experiments

### Mapping

#### IIs on CGRA-ME benchmarks (ADRES-4x4)

|Benchmark	|ILP	|RAMP	|SA	|HybridMap|
|---|---|---|---|---|
|accumulate	|2	|2	|1	|1|
|cap	|3	|3	|3	|3|
|conv2	|2	|2	|1	|1|
|conv3	|2	|4	|1	|1|
|mac	|1	|-	|1	|1|
|mac2	|3	|-	|1	|1|
|matrixmultiply	|2	|2	|1	|1|
|mults1	|3	|5	|2	|2|
|mults2	|3	|-	|2	|2|
|nomem1	|1	|-	|1	|1|
|simple	|1	|2	|1	|1|
|simple2	|1	|2	|1	|1|
|sum	|1	|2	|1	|1|

#### Mapping times on CGRA-ME benchmarks

|Benchmark	|ILP	|RAMP	|SA 	|HybridMap|
|---|---|---|---|---|
|accumulate	|5m50s	|5.58s	|2.49s	|1.95s|
|cap	|8m28s	|1m32s	|1m2s	|18.49s|
|conv2	|2m31s	|50.21s	|1.41s	|1.34s|
|conv3	|4m10s	|4m22s	|27.97s	|2.52s|
|mac	|2.95s	|-	|0.99s	|1.27s|
|mac2	|28m22s	|-	|4m19s	|45.68s|
|matrixmultiply	|14.43s	|0.44s	|3.73s	|2.36s|
|mults1	|20m17s	|1m22s	|12.32s	|12.01s|
|mults2	|23m19s	|-	|14.24s	|40.56s|
|nomem1	|7.83s	|-	|0.90s	|1.13s|
|simple	|12.75s	|1.14s	|0.96s	|1.47s|
|simple2	|34.33s	|1.09s	|0.93s	|1.43s|
|sum	|2.32s	|0.37s	|0.87s	|1.18s|

#### IIs on ExPRESS benchmarks

|Benchmark	|SA  	|Analytic	|
|---|---|---|
|arf	|2	|2	|
|cosine1	|6	|6	|
|cosine2	|10	|10	|
|ewf	|3	|3	|
|feedback	|4	|4	|
|fir1	|6	|6	|
|fir2	|6	|5	|
|horner	|1	|1	|
|motion	|3	|3	|
|matmul	|7	|7	|
|matinv	|20	|20	|

#### Mapping times on ExPRESS benchmarks

|Benchmark	|SA  	|Analytic|
|---|---|---|
|arf	|3m27s	|1m36s|
|cosine1	|1m49s	|1m13s|
|cosine2	|23.24s	|32.34s|
|ewf	|2m6s	|57.48s|
|feedback	|7m51s	|2m31s|
|fir1	|6.10s	|11.23s|
|fir2	|12.10s	|15.91s|
|horner	|27.02s	|3.33s|
|motion	|4m51s	|1min21s|
|matmul	|13m37s	|3m54s|
|matinv	|31m4s	|10m13s|

#### IIs on standard benchmarks

|Benchmark	|SA  	|Analytic|
|---|---|---|
|aes	|6	|6|
|bitcount	|3	|3|
|cap	|1	|1|
|fir	|3	|3|
|fourier	|3	|3|
|gsm	|37	|37|
|interpol	|10	|10|
|isqrt	|3	|3|
|mac	|1	|1|
|mac2	|2	|1|
|mults1	|2	|1|
|mults2	|1	|1|
|sha	|4	|4|
|susan	|10	|10|

#### Mapping times on standard benchmarks

|Benchmark	|SA  	|Analytic|
|---|---|---|
|aes	|39.91s	|43s|
|bitcount	|1m21s	|39.77s|
|cap	|4.63s	|6.09s|
|fir	|3.16s	|4.11s|
|fourier	|1m21s	|1m16s|
|gsm	|7m2s	|5m37s|
|interpol	|3m28s	|1m15s|
|isqrt	|1m29s	|33.68s|
|mac	|0.94s	|1.41s|
|mac2	|1.33s	|1.84s|
|mults1	|9.17s	|2.78s|
|mults2	|1.22s	|2.08s|
|sha	|26.55s	|17.56s|
|susan	|12.57s	|18.65s|

####  CGRA-ME benchmarks, ADRES vs. HyCUBE, II comparison

|Benchmark	|ADRES	|HyCUBE|
|---|---|---|
|accumulate	|1	|1|
|cap	|3	|1|
|conv2	|1	|1|
|conv3	|1	|1|
|mac	|1	|1|
|mac2	|1	|1|
|matrixmultiply	|1	|1|
|mults1	|2	|1|
|mults2	|2	|1|
|nomem1	|1	|1|
|simple	|1	|1|
|simple2	|1	|1|
|sum	|1	|1|

####  CGRA-ME benchmarks, ADRES vs. HyCUBE, mapping time comparison

|Benchmark	|HybridMap	|HyCUBE|
|---|---|---|
|accumulate	|1.95s	|1.95s|
|cap	|18.49s	|2.71s|
|conv2	|1.34s	|1.40s|
|conv3	|2.52s	|2.35s|
|mac	|1.27s	|1.09s|
|mac2	|45.68s	|2.96s|
|matrixmultiply	|2.36s	|1.90s|
|mults1	|12.01s	|3.62s|
|mults2	|40.56s	|3.30s|
|nomem1	|1.13s	|0.47s|
|simple	|1.47s	|1.03s|
|simple2	|1.43s	|1.11s|
|sum	|1.18s	|0.55s|

####  ExPRESS benchmarks, ADRES vs. HyCUBE, II comparison

|Benchmark	|Analytic	|HyCUBE|
|---|---|---|
|arf	|2	|2|
|cosine1	|6	|6|
|cosine2	|10	|10|
|ewf	|3	|3|
|feedback	|4	|4|
|fir1	|6	|6|
|fir2	|5	|5|
|horner	|1	|1|
|motion	|3	|2|
|matmul	|7	7|
|matinv	|20	|20|

####  ExPRESS benchmarks, ADRES vs. HyCUBE, mapping time comparison

|Benchmark	|Analytic	|HyCUBE|
|---|---|---|
|arf	|1m36s	|16.83s|
|cosine1	|1m13s		|23.33s|
|cosine2	|32.34s	|27.35s|
|ewf	|57.48s	|23.19s|
|feedback	|2m31s	|15.52s|
|fir1	|11.23s	|8.77s|
|fir2	|15.91s	|9.18s|
|horner	|3.33s	|2.72s|
|motion	|1min21s	|11.13s|
|matmul	|3m54s	|30.99s|
|matinv	|10m13s	|1m29s|

####  standard benchmarks, ADRES vs. HyCUBE, II comparison

|Benchmark	|Analytic	|HyCUBE|
|---|---|---|
|aes	|6	|4|
|bitcount	|3	|3|
|cap	|1	|1|
|fir	|3	|3|
|fourier	|3	|3|
|gsm	|37	|25|
|interpol	|10	|6|
|isqrt	|3	|3|
|mac	|1	|1|
|mac2	|1	|1|
|mults1	|1	|1|
|mults2	|1		|1|
|sha	|4	|4|
|susan	|10	|10|

####  standard benchmarks, ADRES vs. HyCUBE, mapping time comparison

|Benchmark	|Analytic	|HyCUBE|
|---|---|---|
|aes	|43.00s	|33.05s|
|bitcount	|39.77s	|6.77s|
|cap	|6.09s	|3.95s|
|fir	|4.11s	|3.26s|
|fourier	|1m16s	|16.09s|
|gsm	|5m37s	|2m7s|
|interpol	|1m15s	|54.24s|
|isqrt	|33.68s	|39.35s|
|mac	|1.41s	|0.48s|
|mac2	|1.84s	|1.58s|
|mults1	|2.78s	|2.50s|
|mults2	|2.08s	|2.95s|
|sha	|17.56s	|7.97s|
|susan	|18.65s	|17.11s|



### Partition

|Benchmark	|Ops	|II(M.)	|II(P.)	|Sub-DFGs	|Time|
|---|---|---|---|---|---|
|cosine1	|66	|8	|9	|2	|31s|
|cosine2	|82	|10	|10	|2	|35s|
|matmul	|109	|7	|10	|2	|43s|
|matinv	|333	|20	|36	|8	|527s|
