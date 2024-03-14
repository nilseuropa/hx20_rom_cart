#
# Epson HX-20 HX-20 ROM Cartridge Image Creator
#
# Martin Hepperle, 3/2024
#

class ROM:
	'''Epson HX-20 ROM Cartridge Image File'''

	def __init__(self):
		'''Create a new image'''
		self.files = []

	def addFile ( self, ROMMember ):
		'''Add a file to the image'''
		# data starts behind directory
		start  = (len(self.files)+1)*32
		# update address pointers
		for e in self.files:
			e.start = start
			# include trailng CTRL-Z
			start = start + len(e.data) + 1

		self.files = self.files + [ROMMember]

	def write ( self, fileName ):
		'''write the complete image'''
		f = open(fileName,'wb')

		# write directory
		for e in self.files:
			e.write(f)

		# write data
		for e in self.files:
			f.write(e.data.encode('ASCII'))
			if len(e.data) > 0: # TODO: check whether the dummy file should have a CTRL-Z
				f.write(b'\032')	# append CTRL-Z to regular files

		f.close()


class ROMMember:
	'''Epson HX-20 ROM cartridge Image File or Data Object'''

	def __init__(self,name,data):
		'''Create a new file'''
		name = name.split('.')
		# pad with spaces
		if len(name) > 1:
			self.name = (name[0] + '       ')[0:8]
			self.ext = (name[1] + '   ')[0:3]
		else:
			self.name = ''
			self.ext  = ''
		self.start  = 0
		self.length = len(data)
		self.data = data

	def write ( self, stream ):
		'''write directory entry for this file'''
		if self.length == 0:
			stream.write(b'\377')     # 0xFF name[0]
			stream.write(b'       ')  # name[1:7]
			stream.write(b'   ')      # extension[0:2]
			stream.write(b'\0')       # 0: BASIC, 1: BASIC data, 2: machine code program
			stream.write(b'\0')       # 0: binary, 0xFF: ASCII
			stream.write(b'\0\0\0')   # 0,0,0
			stream.write(b'\0\0\0\0') # start
			stream.write(b'\0\0\0\0') # next
			stream.write(b'\0\0\0\0\0\0')
			stream.write(b'\0\0')
		else:
			stream.write(self.name.encode('ASCII'))
			stream.write(self.ext.encode('ASCII'))
			stream.write(b'\0')       # 0: BASIC, 1: BASIC data, 2: machine code program
			stream.write(b'\377')     # 0: binary, 0xFF: ASCII
			stream.write(b'\0\0\0')   # 0,0,0
			stream.write(format('%04X' % (self.start)).encode('ASCII'))
			# include trailing CTRL-Z
			stream.write(format('%04X' % (self.start+self.length+1)).encode('ASCII'))
			stream.write(format('%02d%02d%02d' % (2,4,22)).encode('ASCII'))
			stream.write(b'\0\0')

# BASIC program text, each line ends with with CR/LF
program1 = '10 FOR I=1 TO 10\r\n' + \
			  '20 PRINT I;I^2\r\n' + \
			  '30 NEXT I\r\n' + \
			  '40 END\r\n'
program2 = '10 I=2\r\n' + '20 PRINT I\r\n' + '30 END\r\n'

# import codecs
# with codecs.open("pong.bas", 'r', encoding='utf-8', errors='ignore') as f:
# 	filedata = f.read()

# create a new ROM
theROM = ROM()
# add files
theROM.addFile(ROMMember('FILE1.BAS',program1))
theROM.addFile(ROMMember('FILE2.BAS',program2))

# TODO: check whether there must be exactly 32 directory entries.
#       in this case add duplicates of last empty file
# add last file: program length should be 0
theROM.addFile(ROMMember('',''))

# output the image
theROM.write('pac0.rom')
