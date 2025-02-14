# speed tests

This folder contains speed tests. Run them from within the root folder (next to the module).

Get the time of a benchmark:

```sh
time python3 benchmark/issue42.py
```

Profile what takes time during a run:

```sh
python3 -m profile benchmark/issue42.py | tee benchmark/issue42.txt
python3 benchmark/CLN007.py | tee benchmark/CLN007.txt
```


