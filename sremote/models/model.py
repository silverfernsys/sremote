# -*- coding: utf-8 -*-

class Manager(object):
	def __init__(self):
		self.create_table()
	
	def create_table(self):
		pass

	def destroy_table(self):
		pass

	def create_object(self, obj):
		pass

	def delete_object(self, obj):
		pass

	def update_object(self, obj):
		pass

class Model(object):
	def database_name(self):
		return self.__class__.__name__.lower()

