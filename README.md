# ofxlist

## Clone the repo ##
```
$ git clone https://github.com/hleofxquotes/ofxlist.git
Cloning into 'ofxlist'...
remote: Enumerating objects: 47, done.
remote: Counting objects: 100% (47/47), done.
remote: Compressing objects: 100% (40/40), done.
remote: Total 47 (delta 13), reused 26 (delta 3), pack-reused 0
Receiving objects: 100% (47/47), 25.12 KiB | 12.56 MiB/s, done.
Resolving deltas: 100% (13/13), done.
```

## Create a virtual env ##

You should create a virtual env to keep Python packages related to this project separated from your normal Python env.

See also: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

```
$ cd ofxlist
# windows
py -m venv venv
# then activate
.\venv\Scripts\activate

# linux
$ python -m venv venv
$ source venv/bin/activate
```
## Install the required packages ##
```
pip install -r requirements.txt
```

## Genarate ofx file using sample input ##

```
$ python src/invtranlist.py --input data/example1.csv --output example1.ofx --acctid 987654321
# Reading input from file=data/example1.csv
# Writing output to file=example1.ofx
```

### Sample input CSV file ###

```
$ cat data/example1.csv 
txn_type,trade_date,symbol,units,unitprice,total
BUYSTOCK,2022/08/25,TSLA,100.00,50.00,-5000.00
SELLSTOCK,2022/07/12,AAPL,-10.00,129.93,1299.30
BUYMF,2022/06/11,VTI,35.00,191.19,-6691.65
SELLMF,2022/05/08,VOO,-12.00,351.34,4216.08
```

Four transactions

* Buy TSLA (stock) on 2022/08/25 (100.00 * $50) for a total -$5000.00 
  - notes that a **buy** transaction resulted in NEGATIVE **total**
  - and a POSITIVE **units**
* Sell AAPL (stock) on 2022/07/12 (-10.00 * $129.93) for a total 1299.30
  - notes that a **sell** transaction resulted in POSITIVE **total**
  - and a NEGATIVE **units**
* Buy VTI (mutual fund) on 2022/06/11 (35.00 * $191.19) for a total -$6691.65
  - notes that a **buy** transaction resulted in NEGATIVE **total**
  - and a POSITIVE **units**
* Sell VOO (mutual fund) on 2022/05/08 (-12.00 * $351.34) for a total 4216.08
  - notes that a **sell** transaction resulted in POSITIVE **total**
  - and a NEGATIVE **units**


## Errors ##

```
(venv) hle@hle-Latitude-7290:~/PycharmProjects/ofxlist$ python src/invtranlist.py --input data/example1.csv --output example1.ofx --acctid 987654321
Traceback (most recent call last):
  File "/home/hle/PycharmProjects/ofxlist/src/invtranlist.py", line 17, in <module>
    import pytz as pytz
ModuleNotFoundError: No module named 'pytz'
```

To fix, install the required packages

```
pip install -r requirements.txt
```
