# vfs-ind-appointments

[![Latest Release](https://img.shields.io/github/v/tag/sinhadotabhinav/vfs-ind-appointments.svg)](https://github.com/sinhadotabhinav/vfs-ind-appointments/releases)

## Overview

This application is a VFS appointment notifier to obtain consulate assistance from kingdom of the Netherlands. This project sends email alerts as follows:
1. Welcome email
2. New appointments availability
3. Daily digest report

## Usage

Prerequisites:

> 1. pip and python command line tools
> 2. chrome browser or chromium in case of a server
>> [download links](https://chromium.woolyss.com) for chromium, please use appropriate platform.
> 3. latest chrome driver
>> [download links](https://chromedriver.chromium.org/downloads) for chromedriver, please use appropriate platform.


Fork and clone this repository:
```
$ git clone https://github.com/sinhadotabhinav/vfs-ind-appointments.git
```

Place the `chromedriver` in the root of the project.

```
vfs-ind-appointments/
|
|___chromedriver
|___LICENSE
|___main.py
|___README.md
```

Update the recipient email address in [`main.py`](https://github.com/sinhadotabhinav/vfs-ind-appointments/blob/master/main.py#L149) file.

Install selenium using pip and execute the python script

```
$ pip install selenium
$ py main.py
```

## License

Read license information [here](https://github.com/sinhadotabhinav/vfs-ind-appointments/blob/master/LICENSE).
