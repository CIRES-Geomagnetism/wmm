## Create the environment for developing wmm Python module

### Install the package in developer mode

`pip install -e .`

### Update the depepdency from github repository
If you want to reinstall the updated Git dependency without installing entire prohect, you can use
  
`pip install --upgrade --force-reinstall git+https://github.com/CIRES-Geomagnetism/geomaglib.git@v0.1.0`

- **git+https://github.com/liyo6397/geomaglib.git**: git repository url
- **v0.1.2:** git tag. Please check the latest tag at https://github.com/liyo6397/geomaglib.git


