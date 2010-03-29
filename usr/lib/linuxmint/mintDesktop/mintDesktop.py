#!/usr/bin/env python

try:
	import os
	import commands
	import sys
	import string
	import pygtk
	pygtk.require("2.0")
	import gtk
	import gtk.glade
	import gettext
	import gconf
except Exception, detail:
	print detail
	sys.exit(1)


# i18n
gettext.install("mintdesktop", "/usr/share/linuxmint/locale")

# i18n for menu item
menuName = _("Desktop Settings")
menuGenericName = _("Gnome Gonfiguration Tool")
menuComment = _("Fine-tune Gnome settings")

class MintDesktop:	

	"""MintDesktop - Makes the best out of your Gnome desktop..."""

	# Set a string in gconf
	def set_string(self, key, value):
		client = gconf.client_get_default()
		client.set_string(key, value)
				
	# Get a string from gconf
	def get_string(self, key):
		client = gconf.client_get_default()
		return client.get_string(key)

	# Set a boolean in gconf according to the value
	def set_bool(self, key, value):
		client = gconf.client_get_default()
		client.set_bool(key, value)

	# Get a boolean from gconf
	def get_bool(self, key):
		client = gconf.client_get_default()
		return client.get_bool(key)


	def __init__(self):
		self.gladefile = '/usr/lib/linuxmint/mintDesktop/mintDesktop.glade'
		self.wTree = gtk.glade.XML(self.gladefile, "main_window") 

		self.wTree.get_widget("main_window").connect("destroy", gtk.main_quit)
		self.wTree.get_widget("button_cancel").connect("clicked", gtk.main_quit)

		# combobox
		wmstyles = gtk.ListStore(str, str)
		wmstyles.append([_("Traditional style"), "menu:minimize,maximize,close"])
		wmstyles.append([_("Mac style"), "close,minimize,maximize:"])
		wmstyles.append([_("Ubuntu style"), "maximize,minimize,close:"])
		self.wTree.get_widget("combo_wmlayout").set_model(wmstyles)

		# i18n
		self.wTree.get_widget("main_window").set_title(_("Desktop Settings"))
		self.wTree.get_widget("label3").set_text(_("Desktop Items"))
		self.wTree.get_widget("label5").set_text(_("Window Manager"))
		self.wTree.get_widget("label_layouts").set_text(_("Window buttons layout:"))
		self.wTree.get_widget("checkbox_computer").set_label(_("Computer"))
		self.wTree.get_widget("checkbox_home").set_label(_("Home"))
		self.wTree.get_widget("checkbox_network").set_label(_("Network"))
		self.wTree.get_widget("checkbox_trash").set_label(_("Trash"))
		self.wTree.get_widget("checkbox_volumes").set_label(_("Mounted Volumes"))
		self.wTree.get_widget("checkbox_compositing").set_label(_("Gnome compositing"))

		# tell gconf we want to be notified when these change
		client = gconf.client_get_default()
		client.add_dir("/apps/nautilus/desktop", gconf.CLIENT_PRELOAD_NONE)
		client.add_dir("/apps/metacity/general", gconf.CLIENT_PRELOAD_NONE)

		# initialise the checkboxes		
		self.init_checkbox("/apps/nautilus/desktop/computer_icon_visible", "checkbox_computer")
		self.init_checkbox("/apps/nautilus/desktop/home_icon_visible", "checkbox_home")
		self.init_checkbox("/apps/nautilus/desktop/network_icon_visible", "checkbox_network")
		self.init_checkbox("/apps/nautilus/desktop/trash_icon_visible", "checkbox_trash")
		self.init_checkbox("/apps/nautilus/desktop/volumes_visible", "checkbox_volumes")
		self.init_checkbox("/apps/metacity/general/compositing_manager", "checkbox_compositing")

		# sets up the metacity button layout combobox
		self.init_combobox("/apps/metacity/general/button_layout", "combo_wmlayout")

	''' Initialise the CheckButton with a gconf value, then bind it with the gconf system '''
	def init_checkbox(self, key, name):
		widget = self.wTree.get_widget(name)
		conf = self.get_bool(key)
		widget.set_active(conf)
		widget.connect("clicked", lambda x: self.set_bool(key, x.get_active()))
		self.add_notify(key, widget)

	''' Bind the ComboBox to gconf and assign the action '''
	def init_combobox(self, key, name):
		widget = self.wTree.get_widget(name)
		conf = self.get_string(key)
		index = 0
		for row in widget.get_model():
			if(conf == row[1]):
				widget.set_active(index)
				break
			index = index +1
		widget.connect("changed", lambda x: self.combo_fallback(key, x))
		self.add_notify(key, widget)
	
	''' Fallback for all combo boxes '''	
	def combo_fallback(self, key, widget):
		act = widget.get_active()
		value = widget.get_model()[act]
		self.set_string(key, value[1])

	''' adds a notify system... '''
	def add_notify(self, key, widget):
		client = gconf.client_get_default()
		notify_id = client.notify_add(key, self.key_changed_callback, widget)
		widget.set_data('notify_id', notify_id)
		widget.set_data('client', client)
		widget.connect("destroy", self.destroy_callback)


	''' destroy the associated notifications '''
	def destroy_callback (self, widget):
		client = widget.get_data ('client')
    		notify_id = widget.get_data ('notify_id')

		if notify_id:
			client.notify_remove (notify_id)

	''' Callback for gconf. update our internal values '''
	def key_changed_callback (self, client, notify_id, entry, widget):
		# deal with all boolean (checkboxes)
		if (type(widget) == gtk.CheckButton):
			if(entry.value.type == gconf.VALUE_BOOL):
				value = entry.value.get_bool()
				if(widget):
					widget.set_active(value)
		elif( type(widget) == gtk.ComboBox ):
			# Sanity check, if its crap ignore it.
			if(entry.value.type == gconf.VALUE_STRING):
				if(not widget and not value):
					return
				# the string in question :)
				value = entry.value.get_string()
				index = 0
				for row in widget.get_model():
					if(value == row[1]):
						widget.set_active(index)
						break
					index = index +1
			
if __name__ == "__main__":
	MintDesktop()
	gtk.main()
