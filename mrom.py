'''
This file is part of pr0ntools
mask ROM utilities
Copyright 2010 John McMaster
Licensed under GPL V3+
'''

import common_driver
import sys
import pimage
import projection_profile
import profile

class MROM:
	def __init__(self, pimage):
		self.pimage = pimage
		self.threshold_0 = 0.3
		self.threshold_1 = 0.3

	def print_bits(self):
		print self.get_bits()


	def process_adjacent_bits(self, pimage):
		'''
		1: confident is a 1
		0: confident is a 0
		X: unknown value
		
           2 |    12.925781  ========================================
           3 |    12.304688    ======================================
           4 |     9.988281            ==============================
           5 |     7.976562                  ========================
           6 |     5.769531                         =================
           7 |     4.167969                              ============
           8 |     3.324219                                ==========
           9 |     4.269531                             =============
          10 |     5.867188                        ==================
          11 |     8.164062                 =========================
          12 |    11.476562       ===================================
          13 |    12.003906     =====================================
          14 |    11.992188     =====================================
          15 |    11.476562       ===================================
          16 |     7.636719                   =======================
          17 |     4.960938                           ===============
          20 |     4.531250                            ==============
          18 |     2.796875                                  ========
          19 |     2.496094                                   =======
          21 |     6.664062                      ====================
          22 |    10.011719            ==============================
          23 |    11.234375        ==================================
          24 |    11.335938       ===================================
          25 |    11.332031       ===================================

		We are considering black 1 and white 0
		Data is where the lower spots are
		It is unknown which is 0 and which is a 1
		Arbitrarily call a 1 the higher/darker value and 0 the lower/lighter value

		Example 1's
          50 |     4.937500                           ===============
          29 |     4.421875                             =============
          60 |     4.328125                             =============
           8 |     3.324219                                ==========

		Examle 0's
          40 |     2.929688                                 =========
          19 |     2.496094                                   =======
          71 |     2.562500                                   =======
          82 |     2.453125                                   =======		
		'''
		
		threshold_0_min = 2.3
		threshold_0_max = 3.0
		threshold_0_min = 3.1
		threshold_0_max = 5.0
		
		# How may pixels between bits
		bit_spacing = None
		pprofile = projection_profile.ProjectionProfile(pimage)
		pprofile.print_horizontal_profile()
		
		# pprofile.print_horizontal_profile()
	
	def get_bits(self):
		self.process_adjacent_bits(self.pimage)
		
		return '10101100'

class Driver(common_driver.CommonDriver):
	def __init__(self):
		common_driver.CommonDriver.__init__(self)
		self.program_name_help_line = 'Mask ROM dumper'
		
		self.input_files = list()

	def print_args(self):
		print '--input: input file'
		print '--threshold-0: fraction of error to recognize 0, 0 being none 1 being severe'
		print '--threshold-1: fraction of error to recognize 1, 0 being none 1 being severe'

	def parse_arg(self, arg):
		arg_key = None
		arg_value = None
		if arg.find("--") == 0:
			arg_value_bool = True
			if arg.find("=") > 0:
				arg_key = arg.split("=")[0][2:]
				arg_value = arg.split("=")[1]
				if arg_value == "false" or arg_value == "0" or arg_value == "no":
					arg_value_bool = False
			else:
				arg_key = arg[2:]			
			
			if arg_key == '--input':
				self.input_files.append(arg_value)
			elif arg_key == '--threshold_0':
				self.threshold_0 = float(arg_value)
			elif arg_key == '--threshold_1':
				self.threshold_1 = float(arg_value)
			else:
				return False
		else:
			self.input_files.append(arg)
		
		return True

	def process(self):
		if len(self.input_files) == 0:
			print 'WARNING: no input files given, try --help'
			return
			
		for image_file_name in self.input_files:
			print 'Processing %s' % image_file_name
			image = pimage.PImage.from_file(image_file_name)
			mrom = MROM(image)

			try:
				mrom.print_bits()
			except:
				print 'Error printing bits'
				if self.propagate_exceptions:
					raise			

if __name__ == "__main__":
	driver = Driver()
	driver.parse_main()
	driver.process()
	sys.exit(0)

