# crypto-indicator

Cryptocurrency Indicator app for linux written in python with Gtk.

## Installation

### Installing with debian package

[Download](https://github.com/ankitgyawali/crypto-indicator/raw/master/dist/crypto-indicator_1.0.0_release.deb) the release debian file located on `dist` folder and install with `sudo dpkg -i crypto-indicator_1.0.0_release.deb`.

Refer to configuration section [below](https://github.com/ankitgyawali/crypto-indicator#configuration) for configuration options.

[Screenshots](https://github.com/ankitgyawali/crypto-indicator#screenshots) provided.

If your newer coins are missing icons, run [scrape.py](https://github.com/ankitgyawali/crypto-indicator/blob/master/scrape.py), with `python /usr/share/crypto-indicator/icons` which will download new icons. You might need to run this as `sudo`.


### Dev Installation

If you would like to run the indicator manually, you can also clone the repository and run `python crypto-indicator`. This picks up `config.ini` and icons from its current folder if it doesn't detect one on `/usr/share/crypto-indicator/config.ini`.

Development was done using `pm2` process manager. If you already have nodejs installed and would like to mess around the code with livereload enabled, run `pm2 start crypto-indicator --interpreter=python --watch --name=crypto-indicator-dev-mode` from root of folder. [This](https://github.com/ankitgyawali/crypto-indicator/blob/master/crypto-indicator) is the main script. If you have nodejs installed but do not have `pm2` install it by running `npm install -g pm2`.


## Configuration

The default configuration file, [config.ini](https://github.com/ankitgyawali/crypto-indicator/blob/master/config.ini) is located on path, `/usr/share/crypto-indicator/config.ini`. You will need root permissions to modify the file. `sudo nano /usr/share/crypto-indicator/config.ini` 

Crypto-indicator will have to be manually restarted once you modify `config.ini`. This can be done by Quitting the indicator from its Menu options and running `crypto-indicator-background` on terminal.

`config.ini` will contain detailed explanation of what each values are used for. Some relevant configuration options are described in greater detail below:

Within `INDICATOR_OPTIONS`:

| Property  | Type | Details |
| :-------------- |:------:|:----- |
| COINS_TO_SHOW        | array | An array of coins to be shown on indicator menu. |
| COINS_BASE_VALUE        | string | If you don't use `USD`, this can be set to `EUR` or `AUD` to display the prices on different base value. |
| DISPLAY_HOLDINGS_IN_MENU        | integer | If you would like the indicator to track your crypto-portfolio, set this to `1`. It will calculate your holdings from the value you set under `HOLDINGS` inside `config.ini`.  |
| REFRESH_TIME_IN_SECONDS        | integer | `crypto-indicator` uses [cryptocompare](https://www.cryptocompare.com/api/) api to fetch coin prices. The minimum possible value is 15. By default the indicator makes an api call & updates price every 20 seconds.  |

Note that if your system does not use monospace font by default the alignment gets messed up which can be [/r/mildlyinfuriating](https://www.reddit.com/r/mildlyinfuriating/). I wasn't able to find a good solution to this beside using `png` files as labels which would require significantly more memory. Feel free to submit a PR/open up an [issue](https://github.com/ankitgyawali/crypto-indicator/issues) if you have any ideas.

Within `INDICATOR_LABELS`:

| Property  | Type | Details |
| :-------------- |:------:|:----- |
| PAIRS        | array | An array containing arrays of [COIN, BASE] pairs to be shown on indicator label. It is recommended to use only 1 or 2 pairs otherwise your indicator bar looks clunky. |
| SEPARATOR_SYMBOL        | string | Separator between each labels on indicator. |
| DISPLAY_TOTAL_HOLDINGS_IN_INDICATOR_LABEL        | integer | If you would like to your portfolio value on indicator label set this to 1. |

Enabling `DISPLAY_TOTAL_HOLDINGS_IN_INDICATOR_LABEL` is not recommended, as your portfolio value might get shared when you take screenshots or if you are using your pc on shared space.

## Screenshots

![Default Configuration Screenshot](/docs/default-screenshot.png?raw=true "Default Configuration Screenshot")


![Indicator with multiple coins](/docs/extended-screenshot.png?raw=true "Indicator with multiple coins")


![Portfolio tracked enabled with random portfolio value](/docs/screenshot-with-random-holdings.png?raw=true "Portfolio tracked enabled with random portfolio value")


## Issues
Report all issues related to crypto-indicator on <a href="https://github.com/ankitgyawali/crypto-indicator/issues" target="_blank">issue page</a>.


## License

[![CC0](http://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
