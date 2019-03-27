# Nakama-Sublime
This is a Sublime Text 3 plugin for Nakama which includes all server documentation

It's compose of two modules, regular and realtime functions.

Regular server functions are autocompleted with the variable that has `= require "nakama"`, the plugin will automatically detect the variable and autocomplete functions from it.

Realtime functions autocomplete upon trying to create a function from a table. Dispatcher functions autocomplete from `dispatcher` variable only.

All functions support on hover documentation. Documentation was extracted from nakama's documentation.