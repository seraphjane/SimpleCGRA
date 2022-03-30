# *SimpleCGRA*
*SimpleCGRA*: An Open-Source Platform for Temporal-Mapping CGRAs

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

>* Compilation is optional. It is needed if you want to use the front-end or use the C++ interface. 
>>* You can compile *SimpleCGRA* by running "make". The front-end is tested in LLVM 11.  
