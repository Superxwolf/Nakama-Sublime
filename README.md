# Nakama Autocomplete
This is a Sublime Text plugin for [Nakama](https://heroiclabs.com/) which includes all server documentation.

It's compose of two modules, regular and realtime functions.

Regular server functions are autocompleted with the variable that has `= require "nakama"`, the plugin will automatically detect the variable and autocomplete functions from it.

Realtime functions autocomplete upon trying to create a function from a table. Dispatcher functions autocomplete from `dispatcher` variable only.

All functions support on hover documentation. Documentation was extracted from nakama's documentation.

## Install

#### [Package Control](https://packagecontrol.io/installation)

Using Package Control: `Ctrl + Shift + P -> Package Control: Install Package -> Nakama Autocomplete`

#### Manual
Download or clone the repository to your package folder.

To access the packge folder from sublime: `Preferences -> Browse Packages...`
