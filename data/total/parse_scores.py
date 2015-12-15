import os,sys
import utils

HWFILES = ['hw1','hw2','hw3','hw4','hw5','hw6']
QUIZFILES = ['quiz1','quiz2']
PROJECTFILES = ['project1','project2']
# one hw is dropped, so divided by 5
WEIGHTS = [0.5/5,0.125/2,0.25/2] #hws, quizes, project

class Students(object):

	def __init__(self, headers, map_TA):
		self.headers = headers#+['total']+['normalized']+['TA']
		self.student_dict = {}
		self.student_drop = {}

		with open(map_TA) as f:
			map_TA_list = f.readlines()

		self.map_TA = dict( (ta.strip().split()[0], ta.strip().split()[-1]) for ta in map_TA_list)

	def addGrade(self, sunet, grade, weight):
		if not sunet:
			return
		if not grade:
			grade = '0'
		grade = float(grade)*weight
		if sunet in self.student_dict:
			self.student_dict[sunet].append(grade)
		else:
			self.student_dict[sunet] = [grade]

	def setDropDict(self):
		for sunet in self.student_dict.keys():
			# only include hws
			score_list = self.student_dict[sunet][:6]

			# drop idx num
			self.student_drop[sunet] = self.student_dict[sunet].index(min(score_list))

	def checkExists(self, sunet):
		return bool(sunet in self.student_dict)

	def checkConsistent(self):
		num_grades = len(self.student_dict.values()[0])
		for grade_lst in self.student_dict.values():
			if len(grade_lst) != num_grades:
				return False
		return True

	def addTotal(self):
		self.headers.append('total')
		for sunet, grade_lst in self.student_dict.iteritems():
			sum_scores = 0
			for idx, score in enumerate(grade_lst):
				# skip over minimum idx
				if idx == self.student_drop[sunet]:
					continue
				sum_scores += score
			self.student_dict[sunet].append(sum_scores)
	
	def addNormalized(self):
		# get total scores list per TA, but drop outliers and quiz scores in calculation
		TA_scores = {}
		for sunet, scores in self.student_dict.iteritems():
			TA = self.map_TA[sunet]
			if TA not in TA_scores:
				# -1 is total score minus minimum, 6 and 7 is quizzes
				TA_scores[TA] = [scores[-1] - scores[6] - scores[7]]
			else:
				TA_scores[TA].append(scores[-1] - scores[6] - scores[7])

		# get mean total and mean per TA
		tot_mean = 0.0
		TA_mean = {}
		for TA, scores in TA_scores.iteritems():

			# get rid of outliers
			sort_scores = sorted(scores)
			Q1 = sort_scores[int(len(scores) * (1.0/4))]
			Q3 = sort_scores[int(len(scores) * (3.0/4))]
			IQR = Q3 - Q1
			no_out = [score for score in sort_scores if score > (Q1 - 1.5*IQR) and score < (Q3 + 1.5*IQR)]
			
			mean = utils.mean(no_out)
			tot_mean += mean
			TA_mean[TA] = mean
		
		# mean everyone should adjust to (means together, divided by num TA's)
		avg_mean = tot_mean / float(len(TA_mean))

		TA_adjust = {}
		print("\nAdjust score by:")
		for TA in TA_mean.keys():
			TA_adjust[TA] = avg_mean - TA_mean[TA] 
			print("TA:\t\t{0}\nadjust score:\t{1}".format(TA, TA_adjust[TA]))
		
		
		self.headers.append('normalized')
		for sunet, grade_lst in self.student_dict.iteritems():
			self.student_dict[sunet].append(int(round(self.student_dict[sunet][-1] + TA_adjust[self.map_TA[sunet]])))
			

	def addTA(self):
		self.headers.append('TA')
		for sunet, TA in self.map_TA.iteritems():
			self.student_dict[sunet].append(TA)		

	def toCSV(self):

		self.addTotal()
		self.addNormalized()
		self.addTA()

		self.headers.insert(0,'sunet')

		# adding empty cols to fill in excel/pages/googlesheets
		self.headers += ['empty1','empty2','empty3']

		with open('gradebook.csv', 'w') as f:
			# write headers
			f.write(','.join(self.headers))
			f.write('\n')
			for sunet, grade_lst in self.student_dict.iteritems():
				write_string = sunet + ',' + ','.join([str(col) for col in grade_lst]) + ',,,'
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
	map_TA = '/afs/ir/class/cme211/git/repos_project_p2/TA_assignments.txt'

	if not all(os.path.exists(l) for l in hw_paths):
		raise RuntimeError('HW files do not exist!')
	
	if not all(os.path.exists(l) for l in quiz_paths):
		raise RuntimeError('QUIZ files do not exist!')		
	
	if not all(os.path.exists(l) for l in project_paths):
		raise RuntimeError('PROJECT files do not exist!')	

	if not os.path.exists(map_TA):
		raise RuntimeError(map_ta + 'does not exist!')

	# Init object from class, headers are in order of processing
	students = Students(HWFILES+QUIZFILES+PROJECTFILES, map_TA)

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
				students.addGrade(sunet, score, WEIGHTS[0])


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
				raise RuntimeError('Line in quiz is not formatted correctly: '+line)

			sunet, score = line_lst[1].lower(), line_lst[9]
			if not students.checkExists(sunet):
				raise RuntimeError('Student '+sunet+' does not exist in quiz1?')
			students.addGrade(sunet, score, WEIGHTS[1])

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
				raise RuntimeError('Line in quiz is not formatted correctly: '+line)

			sunet, score = line_lst[1].lower(), line_lst[10]
			print(score)
			if not students.checkExists(sunet):
				raise RuntimeError('Student '+sunet+' does not exist in quiz2?')
			students.addGrade(sunet, score, WEIGHTS[1])

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
				raise RuntimeError('Line in project1 is not formatted correctly: '+line)

			sunet, score = line_lst[0].lower(), line_lst[1]
			if num_hw != 0:
				if not students.checkExists(sunet):
					raise RuntimeError('Student '+sunet+' does not exist in project1?')
			students.addGrade(sunet, score, WEIGHTS[2])

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
				raise RuntimeError('Line in project2 is not formatted correctly: '+line)

			sunet, score = line_lst[0].lower(), line_lst[1]
			if num_hw != 0:
				if not students.checkExists(sunet):
					raise RuntimeError('Student '+sunet+' does not exist in project2?')
			students.addGrade(sunet, score, WEIGHTS[2])


	if not students.checkConsistent():
		raise RuntimeError('Dictionary is not consistent. Different number of grades per student...')

	# Decide which hw to drop
	students.setDropDict()

	# Calc total, normalized etc.. and write to CSV
	students.toCSV()

if __name__=='__main__':
	main()
