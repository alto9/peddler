# Code Contribution Guidelines

#### 1. Fork this repository
#### 2. Checkout the source code with:
```git clone https://github.com/alto9/peddler.git```
#### 3. Start a new git branch with
```
cd peddler
git checkout -b yournewbranch
```
#### 4. Make change code
#### 5. Install cli in your local
```
python setup.py install
```
#### 6. Testing
```
make test
```
#### 7. When the tests pass, add the new files and change and push the result, like this:
```angular2html
git add yourchangedfile
git commit -m yourcommitname
git push origin yourbranchname
```
#### 8. Finally, [create a pull request](https://help.github.com/articles/creating-a-pull-request). We'll then review and merge it.
