# Nakama Doc Fetch
# This command retrieves and parses code function references from heroic-labs/nakama-doc
# And saves it locally, so updating on documentation update is easy
# As long as Heroic Labs doesn't change the documentation format/layout

import sublime
import sublime_plugin
import re
import urllib.request

def strip_newlines(x):
    if x.endswith("\n\n"): x = x[:-2]
    if x.endswith("\n"): x = x[:-1]
    if x.startswith("\n"): x = x[1:]
    return x

# Parse parameters details from the table format
def parse_args(args):
	arg_list = []
	for line in args.split('\n'):
		parts = line.split('|')
		if len(parts) == 5:
			arg_list.append({
					'name': parts[1].strip(),
					'type': parts[2].strip(),
					'details': parts[3].strip()
				})

	return arg_list

class NakamaDocFetchCommand(sublime_plugin.TextCommand):
	def get_setting(self, key, default=None):
		settings = sublime.load_settings('nakama-doc-regex.sublime-settings')
		if settings:
			return settings.get(key, default)
		else:
			return default

	def get_doc_settings(self):
		return sublime.load_settings('nakama-doc.sublime-settings')

	def save_doc_settings(self):
		sublime.save_settings('nakama-doc.sublime-settings')

	def fetch_doc(self):
		print("Fetching Nakama Doc...")
		try:
			doc_response = urllib.request.urlopen('https://raw.githubusercontent.com/heroiclabs/nakama-docs/master/docs/runtime-code-function-reference.md')
		except Exception as e:
			print("Could not fetch Nakama docs")
			return

		doc_text = str(doc_response.read())

		# Change text \n to actual new lines so that regex behaves nicely
		doc_text = doc_text.replace("\\n", "\n")
		
		regex_pattern = self.get_setting('regex')
		param_indexes = self.get_setting('params')
		param_keys = param_indexes.keys()

		matches = re.findall(regex_pattern, doc_text)
		api_functions = self.get_doc_settings();
		for m in matches:
			cur_func = {}
			for k in param_keys:
				cur_val = strip_newlines(m[param_indexes[k]])
				if cur_val == '': cur_val = None
				else: cur_val = cur_val.replace('\n', '<br>')
				cur_func[k] = cur_val

			if cur_func['args'] is not None: cur_func['args'] = parse_args(cur_func['args'])
			api_functions.set(m[param_indexes['func_name']], cur_func)

		self.save_doc_settings()

		print("Finished loading Nakama doc")

	def run(self, edit):
		sublime.set_timeout_async(self.fetch_doc, 0)