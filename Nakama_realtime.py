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

class NakamaCompletionEvent(sublime_plugin.EventListener):

	def is_lua(self, view):
		return view.settings().get("syntax") == "Packages/Lua/Lua.sublime-syntax"

	def get_setting(self, key, default=None):
		settings = sublime.load_settings('nakama-rt-completion.sublime-settings')
		if settings:
			return settings.get(key, default)
		else:
			return default

	def get_doc_entry(self, key, default=None):
		settings = sublime.load_settings('nakama-rt-doc.sublime-settings')
		if settings:
			return settings.get(key, default)
		else:
			return default

	def on_query_completions(self, view, prefix, locations):
		if not self.is_lua(view):
			# Not Lua or nakama present, don't do anything.
			return

		# Get where the current word begins and ends
		word_location = view.word(locations[0])
		start_location = word_location.a
		end_location = word_location.b

		# Check if we're autocompleting from a dot
		if view.substr(sublime.Region(start_location-1, start_location)) != '.':
			return

		# Get the word before the dot
		before_word = view.word(start_location-2)
		class_var = view.substr(before_word)
		if class_var == "dispatcher":
			return (
				self.get_setting('autocomplete-dispatcher')
			)
		# Check if it's defining a function
		elif view.substr(view.word(before_word.a - 2)) == 'function':
			return (
				self.get_setting('autocomplete')
			)

	def on_hover(self, view, point, hover_zone):

		if hover_zone != sublime.HOVER_TEXT:
			return

		# Get start and finish for current hovered word
		word_location = view.word(point)
		start_location = word_location.a
		end_location = word_location.b

		# Get the entire current hovered word
		cur_word = view.substr(word_location)

		# Check for current hovered word in documentation function list
		entry = self.get_doc_entry(cur_word, None)

		if entry is None:
			return

		view.show_popup(TEMPLATE.format(**entry),
			sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, *view.viewport_extent())