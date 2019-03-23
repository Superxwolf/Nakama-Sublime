# Nakama-sublime
# Autocompletes all of nakama server functions from `require "nakama"`
# Presents documentation of nakama function on hover

import sublime
import sublime_plugin
import re
import urllib.request

TEMPLATE = """
	<p>Nakama Function</p>
	<p><b>{func_name}</b> ({param_types})</p>
	<h4>Description:</h4>
	<p>{desc}</p>
	<h4>Example:</h4>
	{example}
	"""

class NakamaCompletionEvent(sublime_plugin.EventListener):
	def get_setting(self, key, default=None):
		settings = sublime.load_settings('nakama-completion.sublime-settings')
		if settings:
			return settings.get(key, default)
		else:
			return default

	def get_doc_entry(self, key, default=None):
		settings = sublime.load_settings('nakama-doc.sublime-settings')
		if settings:
			return settings.get(key, default)
		else:
			return default

	def on_query_completions(self, view, prefix, locations):
		if view.settings().get("syntax") != "Packages/Lua/Lua.sublime-syntax":
			# Not Lua, don't do anything.
			return

		# Get where the current word begins and ends
		word_location = view.word(locations[0])
		start_location = word_location.a
		end_location = word_location.b

		# Check if we're autocompleting from a dot
		if view.substr(sublime.Region(start_location-1, start_location)) != '.':
			return
		
		# Get all the document from start to current point
		src = view.substr(sublime.Region(0, start_location))

		# Check if nakama is included, and which variable is it saved to
		# match = re.search(r"""(local)?\s+([^\s]+)\s+=\s+require[\s\(]+['"]nakama['"][\s\)]*""", src)
		match = re.search(r"""local ([^\s]+) = require[\s\(]+['"]nakama['"]*""", src)

		if match is None:
			#nakama not included
			return

		# Get the nakama variable name
		nakama_var = match.group(1)

		# Get variable name before the dot in the current context
		class_var = view.substr(view.word(start_location-2))

		if nakama_var != class_var:
			# Not using the nakama variable
			return

		return (
			self.get_setting('autocomplete'),
			sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS
		)

	def on_hover(self, view, point, hover_zone):

		if hover_zone != sublime.HOVER_TEXT:
			return

		word_location = view.word(point)
		start_location = word_location.a
		end_location = word_location.b

		cur_word = view.substr(word_location)

		entry = self.get_doc_entry(cur_word, None)

		if entry is None:
			return

		# print("Nakama doc found")

		view.show_popup(TEMPLATE.format(**entry),
			sublime.HIDE_ON_MOUSE_MOVE_AWAY, point, *view.viewport_extent())