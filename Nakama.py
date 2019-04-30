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

	# Setting for the current view
	_is_lua = False
	has_nakama = False
	cur_nakama_var = ""
	cur_nakama_line = -1

	# Keep count for idle execution
	timeout = 0
    
	def handle_timeout(self):
		self.timeout = self.timeout - 1

		# Keep the loop running
		if self.timeout > 0:
			sublime.set_timeout_async(self.handle_timeout, 500)

		else: self.on_idle()

	# Start or reset the timer on document modification
	def on_modified_async(self):
		if not self.is_lua():
			# Not Lua, don't do anything.
			return

		# If document was changed to Nakama after view focus, search for nakama
		if not self._is_lua:
			self.find_nakama_var()
			self._is_lua = True

		# Start idle timer loop if none is running
		if self.timeout == 0: 
			sublime.set_timeout_async(self.handle_timeout, 500)

		# Set timer to 1 seconds, 2 ticks of 500ms
		self.timeout = 2
        
    # Find Nakama var when idle times out
	def on_idle(self):
		self.find_nakama_var()

	def is_lua(self):
		# Some plugins modify scope name, check if 'source.lua' is in the scope name
		return 'source.lua' in self.view.scope_name(0)

	def get_setting(self, key, default=None):
		settings = sublime.load_settings('nakama-completion.sublime-settings')
		return settings.get(key, default)

	def get_doc_entry(self, key, default=None):
		settings = sublime.load_settings('nakama-doc.sublime-settings')
		return settings.get(key, default)

	def get_nakama_var(self):
		return self.cur_nakama_var

	def find_nakama_var(self):
		var_region = self.view.find(r"""local [^\s]+ = require[\s\(]+['"]nakama['"]""", 0)
		if var_region.a == -1:
			self.has_nakama = False
			return

		match = re.search(r"""local ([^\s]+) = require[\s\(]+['"]nakama['"]""", self.view.substr(var_region))
		self.cur_nakama_var = match.group(1)
		self.cur_nakama_line = self.view.rowcol(var_region.a)[0]
		self.has_nakama = True

	# Search for nakama on view focus
	def on_load_async(self):
		self._is_lua = self.is_lua()
		if self._is_lua:
			self.find_nakama_var()
		else:
			self.has_nakama = False

	def on_query_completions(self, prefix, locations):
		if not self._is_lua or not self.has_nakama:
			# Not Lua or nakama present, don't do anything.
			return

		# Get where the current word begins and ends
		word_location = self.view.word(locations[0])
		start_location = word_location.a
		end_location = word_location.b

		# Check if we're autocompleting from a dot
		if self.view.substr(sublime.Region(start_location-1, start_location)) != '.':
			return

		# Get the nakama variable name
		nakama_var = self.get_nakama_var()

		# Get the word before the dot
		class_var = self.view.substr(self.view.word(start_location-2))

		if nakama_var != class_var:
			# Not using the nakama variable
			return

		return (
			self.get_setting('autocomplete'),
			sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS
		)

	def on_hover(self, point, hover_zone):

		if hover_zone != sublime.HOVER_TEXT or not self.has_nakama:
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