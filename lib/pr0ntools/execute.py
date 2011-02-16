'''
pr0ntools
Copyright 2011 John McMaster <JohnDMcMaster@gmail.com>
Licensed under the terms of the LGPL V3 or later, see COPYING for details
'''

import os

class Execute:
	@staticmethod
	def simple(cmd, working_dir = None):
		'''Returns rc of process, no output'''
		
		print 'cmd in: %s' % cmd
		if True:
			os.sys.stdout.flush()
			return os.system(cmd)
		else:
			cmd = "/bin/bash " + cmd 
			output = ''
			to_exec = cmd.split(' ')
			print 'going to execute: %s' % to_exec
			subp = subprocess.Popen(to_exec)
			while subp.returncode is None:
				# Hmm how to treat stdout  vs stderror?
				com = subp.communicate()[0]
				if com:
					print com
				com = subp.communicate()[1]
				if com:
					print com
				time.sleep(0.05)
				subp.poll()
	
			return subp.returncode

	@staticmethod
	def with_output(program, args, working_dir = None):
		'''Return (rc, output)'''
		to_exec = program
		for arg in args:
			to_exec += ' "' + arg + '"'
		return Execute.with_output_simple(to_exec, working_dir)
		
	@staticmethod
	def with_output_simple(cmd, working_dir = None):
		'''Return (rc, output)'''
		working_dir_str = ''
		if working_dir:
			working_dir_str = 'cd %s && ' % working_dir
		# ugly...but simple
		# ((false; true; true) 2>&1; echo "***RC_HACK: $?") |tee temp.txt
		rc = Execute.simple('(' + working_dir_str + cmd + ') 2>&1 |tee file.tmp; exit $PIPESTATUS')
		output = open('file.tmp').read()
		# print 'OUTPUT: %d, %s' % (rc, output)
		return (rc, output)
	
		'''
		print 'cmd in: %s' % cmd
		#rc = os.system(cmd)
		#output = ''
		#cmd = "/bin/bash " + cmd 
		output = ''
		#subp = subprocess.Popen(cmd.split(' '))
		#subp = subprocess.Popen(cmd, stdin=stdin)
		# Hmm okay why don't I get the output to stdout/stderr
		subp = subprocess.Popen(cmd, shell=True)
		while subp.returncode is None:
			# Hmm how to treat stdout  vs stderror?
			com = subp.communicate()[0]
			if com:
				output += com
			com = subp.communicate()[1]
			if com:
				output += com		 
			time.sleep(0.05)
			subp.poll()
	
		return (subp.returncode, output)
		'''

