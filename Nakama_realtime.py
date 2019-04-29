# Nakama-sublime
# Autocompletes all of nakama server functions from `require "nakama"`
# Presents documentation of nakama function on hover

import sublime
import sublime_plugin
import re
import urllib.request
import functools

# Popup template for on hover documentation
TEMPLATE = """
	<p>Nakama Function</p>
	<p><b>{func_name}</b> ({param_types})</p>
	<h4>Description:</h4>
	<p>{desc}</p>
	<h4>Example:</h4>
	{example}
	"""

class NakamaCompletionEvent(sublime_plugin.ViewEventListener):

	def is_lua(self):
		# Some plugins modify scope name, check if 'source.lua' is in the scope name
		return 'source.lua' in self.view.scope_name(0)

	def get_setting(self, key, default=None):
		settings = sublime.load_settings('nakama-rt-completion.sublime-settings')
		return settings.get(key, default)

	def get_doc_entry(self, key, default=None):
		settings = sublime.load_settings('nakama-rt-doc.sublime-settings')
		return settings.get(key, default)

	def on_query_completions(self, prefix, locations):
		if not self.is_lua():
			# Not Lua or nakama present, don't do anything.
			return

		# Get where the current word begins and ends
		word_location = self.view.word(locations[0])
		start_location = word_location.a
		end_location = word_location.b

		# Check if we're autocompleting from a dot
		if self.view.substr(sublime.Region(start_location-1, start_location)) != '.':
			return

		# Get the word before the dot
		before_word = self.view.word(start_location-2)
		class_var = self.view.substr(before_word)
		if class_var == "dispatcher":
			return (
				self.get_setting('autocomplete-dispatcher')
			)
		# Check if it's defining a function
		elif self.view.substr(self.view.word(before_word.a - 2)) == 'function':
			return (
				self.get_setting('autocomplete')
			)

	def on_hover(self, point, hover_zone):

		if hover_zone != sublime.HOVER_TEXT:
			return

		# Get start and finish for current hovered word
		word_location = self.view.word(point)
		start_location = word_location.a
		end_location = word_location.b

		# Get the entire current hovered word
		cur_word = self.view.substr(word_location)

		# Check for current hovered word in documentation function list
		entry = self.get_doc_entry(cur_word, None)

		if entry is None:
			return

		self.view.show_popup(TEMPLATE.format(**entry),
			sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, *self.view.viewport_extent())