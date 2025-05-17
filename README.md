# XView
Python library to help visualize your learning processes experiments.

## install

### BASE

```shell
git clone git@github.com:Joffrey-Michaud/XView.git
cd XView
pip install -r requirements.txt
pip install -e .
```

### + for WSL2 users

```shell
# base install
sudo apt update
sudo apt install libxcb-xinerama0 libxcb-xinput0 libegl1-mesa libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xkb1 libxkbcommon-x11-0 libxcb-randr0 libxcb-shape0 libxcb-util1 libxcb-cursor0

# more QT systems
sudo apt install build-essential libgl1-mesa-glx libx11-xcb1 libfontconfig1 libdbus-1-3 libx11-6 libxext6 libxrender1 libxcb1 libxkbcommon0 libxcb-xfixes0

chmod 0700 /run/user/$(id -u)
```

## First use

Run config.py, configure your experiment folder, and modify the graph style if you want.

