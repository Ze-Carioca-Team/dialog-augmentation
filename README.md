# dialog-augmentation

get word vectors
```sh
wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.pt.300.bin.gz
gzip -d cc.pt.300.bin.gz
```

install requirements
```sh
pip install -r requirements
```

run MADA with data aug
```sh
python mada.py --filename file.json
```

run EDA with data aug
```sh
python eda.py --filename file.json
```

run backtranslation with data aug
```sh
python backtranslation.py --filename file.json
```

run deanonymization with data aug
```sh
python deanonymization.py --filename file.json
```

run all dialog augmentation algorithms
```sh
python dialog_augmentation.py --filename file.json
```
