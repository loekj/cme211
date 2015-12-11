import os,sys

HWFILES = ['hw1','hw2','hw3','hw4','hw5','hw6']
QUIZFILES = ['quiz1','quiz2']
PROJECTFILES = ['project1','project2']

class Students(object):

	def __init__(self, headers):
		self.headers = ['sunet']+headers+['total']
		self.student_dict = {}

	def addGrade(self, sunet, grade):
		if not sunet:
			return
		if not grade:
			grade = '0'

		if sunet in self.student_dict:
			self.student_dict[sunet].append(grade)
		else:
			self.student_dict[sunet] = [grade]

	def checkExists(self, sunet):
		return bool(sunet in self.student_dict)

	def checkConsistent(self):
		num_grades = len(self.student_dict.values()[0])
		for grade_lst in self.student_dict.values():
			if len(grade_lst) != num_grades:
				return False
		return True

	def toCSV(self):
		with open('gradebook.csv', 'w') as f:
			# write headers
			f.write(','.join(self.headers))
			f.write('\n')
			for sunet, grade_lst in self.student_dict.iteritems():
				write_string = sunet + ',' + ','.join(grade_lst) + ',' + str(int(sum([float(el) for el in grade_lst])))
				f.write(write_string)
				f.write('\n')

	def __repr__(self):
		return ('\n').join("{0:<20}{1}".format(student,str(grades)) for student,grades in self.student_dict.iteritems())


def toList(lst):
	if isinstance(lst, basestring):
		return [lst]
	return lst

def main():
	# Check if files exist
	hw_paths = map(lambda x: '../'+x+'/Scores.txt',toList(HWFILES))
	quiz_paths = map(lambda x: '../'+x+'/'+x+'.csv',toList(QUIZFILES))
	project_paths = map(lambda x: '../'+x+'/Scores.txt',toList(PROJECTFILES))

	if not all(os.path.exists(l) for l in hw_paths):
		raise RuntimeError('HW files do not exist!')
	
	if not all(os.path.exists(l) for l in quiz_paths):
		raise RuntimeError('QUIZ files do not exist!')		
	
	if not all(os.path.exists(l) for l in project_paths):
		raise RuntimeError('PROJECT files do not exist!')				


	# Init object from class, headers are in order of processing
	students = Students(HWFILES+QUIZFILES+PROJECTFILES)

	# Process HWs
	for num_hw, hw in enumerate(hw_paths):
		with open(hw, 'r') as f:
			for line in f:
				line = line.strip()
				if not line:
					continue
				if ',' not in line:
					line_lst = line.split(':')
				else:
					line_lst = line.split(',')
				line_lst = [word.strip() for word in line_lst]

				if len(line_lst) < 2:
					RuntimeError('Line in file '+hw+' is not formatted correctly: '+line)

				sunet, score = line_lst[0].lower(), line_lst[1]
				if num_hw != 0:
					if not students.checkExists(sunet):
						raise RuntimeError('Student '+sunet+' does not exist in checking hw '+str(num_hw+1))
				students.addGrade(sunet, score)


	# Process QUIZs
	quiz1, quiz2 = quiz_paths[0], quiz_paths[1]
	with open(quiz1, 'r') as f:
		print('Burning line "'+f.readline()+'"')
		for line in f:
			if 'Mean' in line:
				break
			line = line.strip()
			if not line:
				continue

			while(line.find('"') >= 0):
				idx1 = line.find('"')
				if idx1 >= 0:
					idx2 = line.find('"',idx1+1)
					line = line[idx2+1:]
			line_lst = line.split(',')
			line_lst = [word.strip() for word in line_lst]
			if len(line_lst) < 2:
				RuntimeError('Line in quiz is not formatted correctly: '+line)

			sunet, score = line_lst[1].lower(), line_lst[9]
			if not students.checkExists(sunet):
				raise RuntimeError('Student '+sunet+' does not exist in quiz1?')
			students.addGrade(sunet, score)


	with open(quiz2, 'r') as f:
		print('Burning line "'+f.readline()+'"')
		for line in f:
			if 'Mean' in line:
				break
			line = line.strip()
			if not line:
				continue

			while(line.find('"') >= 0):
				idx1 = line.find('"')
				if idx1 >= 0:
					idx2 = line.find('"',idx1+1)
					line = line[idx2+1:]
			line_lst = line.split(',')
			line_lst = [word.strip() for word in line_lst]
			if len(line_lst) < 2:
				RuntimeError('Line in quiz is not formatted correctly: '+line)

			sunet, score = line_lst[1].lower(), line_lst[10]
			if not students.checkExists(sunet):
				raise RuntimeError('Student '+sunet+' does not exist in quiz2?')
			#students.addGrade(sunet, score)
			students.addGrade(sunet, '0')


	# Process Project
	project1, project2 = project_paths[0], project_paths[1]
	with open(project1, 'r') as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			if ',' not in line:
				line_lst = line.split(':')
			else:
				line_lst = line.split(',')
			line_lst = [word.strip() for word in line_lst]

			if len(line_lst) < 2:
				RuntimeError('Line in project1 is not formatted correctly: '+line)

			sunet, score = line_lst[0].lower(), line_lst[1]
			if num_hw != 0:
				if not students.checkExists(sunet):
					raise RuntimeError('Student '+sunet+' does not exist in project1?')
			students.addGrade(sunet, score)	

	with open(project2, 'r') as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			if ',' not in line:
				line_lst = line.split(':')
			else:
				line_lst = line.split(',')
			line_lst = [word.strip() for word in line_lst]

			if len(line_lst) < 2:
				RuntimeError('Line in project2 is not formatted correctly: '+line)

			sunet, score = line_lst[0].lower(), line_lst[1]
			if num_hw != 0:
				if not students.checkExists(sunet):
					raise RuntimeError('Student '+sunet+' does not exist in project2?')
			students.addGrade(sunet, score)				


	if not students.checkConsistent():
		raise RuntimeError('Dictionary is not consistent. Different number of grades per student...')
	students.toCSV()

if __name__=='__main__':
	main()