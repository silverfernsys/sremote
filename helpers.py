#! /usr/bin/env python
import unittest

def binary_search(array, value):
	index = binary_search_helper(array, value, 0, len(array))
	return array[index:len(array)]

def binary_search_helper(array, value, start, end):
	if (start >= end):
		return end
	else:
		mid = start + (end - start) / 2
		if array[mid][0] > value:
			return binary_search_helper(array, value, start, mid)
		else:
			return binary_search_helper(array, value, mid + 1, end)


class BinarySearch(unittest.TestCase):
    def setUp(self):
        self.data = [[1454548327.310017, 0.0],
					[1454548330.334902, 0.0],
					[1454548333.361855, 0.0],
					[1454548336.392282, 0.0],
					[1454548339.420911, 0.0],
					[1454548342.450155, 0.0],
					[1454548345.478169, 0.0],
					[1454548348.508201, 0.0],
					[1454548351.536519, 0.0],
					[1454548354.56746, 0.0],
					[1454548357.597519, 0.0],
					[1454548360.625813, 0.0],
					[1454548363.652298, 0.0],
					[1454548366.680426, 0.0],
					[1454548369.708198, 0.0],
					[1454548372.735078, 0.0],
					[1454548375.766586, 0.0],
					[1454548378.795979, 0.0],
					[1454548381.826492, 0.0],
					[1454548384.856257, 0.0],
					[1454548387.883374, 0.0],
					[1454548390.913692, 0.0],
					[1454548393.943834, 0.0],
					[1454548396.973136, 0.0],
					[1454548400.001532, 0.0],
					[1454548403.031635, 0.0]]

    def tearDown(self):
        self.data = None

    def test_binary_search(self):
    	# self.assertEqual(0, 1, "Wow")
    	self.assertEqual(len(binary_search(self.data, 1454548328.310017)), len(self.data) - 1, "== self.data - 1")
    	self.assertEqual(len(binary_search(self.data, 1454548354.56746)), len(self.data) - 10, "== self.data - 10")
    	self.assertEqual(len(binary_search(self.data, 1454548403.031635)), len(self.data) - 26, "== self.data - 26")

    def test_binary_search_index(self):
    	index = binary_search_helper(self.data, 1454548328.310017, 0, len(self.data))
    	print('index: %s' % index)
    	self.assertEqual(index, 1, "Index == 1.")

    	index = binary_search_helper(self.data, 1454548354.56746, 0, len(self.data))
    	print('index: %s' % index)
    	self.assertEqual(index, 10, "Index == 10.")

    	index = binary_search_helper(self.data, 1454548403.031635, 0, len(self.data))
    	print('index: %s' % index)
    	self.assertEqual(index, 26, "Index == 26.")

    	index = binary_search_helper(self.data, 1454548404.031635, 0, len(self.data))
    	print('index: %s' % index)
    	self.assertEqual(index, 26, "Index == 26.")

if __name__ == '__main__':
	unittest.main()