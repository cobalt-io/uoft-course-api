import requests, http.cookiejar
from bs4 import BeautifulSoup
from collections import OrderedDict
#from secrets import *
import time
import re
import json
#import pymongo

LENGTH_COURSE_CODE = 8
COURSE_START_OFFSET = 4
COURSE_CODE_INDEX = 0
SEMESTER_INDEX = 1
TITLE_INDEX = 2
MEETING_SECTION_INDEX = 3
WAIT_INDEX = 4
TIME_INDEX = 5
LOCATION = 6
INSTRUCTORS = 7
SECTION_RE_SCHEME = [""]
class CourseTimetable:
	"""A wrapper for fetching U of T's Course Timetable data

	located at http://www.artsandscience.utoronto.ca/ofr/timetable/"""
	def __init__(self, season):
		self.host = 'http://www.artsandscience.utoronto.ca'
		self.urls = None
		self.cookies = http.cookiejar.CookieJar()
		#self.client = pymongo.MongoClient(MONGO_URL)
		#self.db = self.client[MONGO_DB]
		#self.courses = self.db.courses
		self.count = 0
		self.total = 0
		self.fall = None
		self.spring = None
		self.season = season


	"""A wrapper for retrieving the html files of each program."""
	def get_timetables(self):
		main = self.get_html("%s/ofr/timetable/%s/sponsors.htm"
		% (self.host,self.season))
		file = open("timetables/%s/sponsors.htm" % self.season, "w")
		file.write(str(main))
		file.close()
		programs = self.get_program_code(main)
		for program in programs:
			program_file = open("timetables/%s/%s" % (self.season, program), "w")
			program_html = self.get_html("%s/ofr/timetable/%s/%s"
			% (self.host, self.season, program))
			program_file.write(str(program_html))
			program_file.close()

	"""Retrieve the program names."""
	def get_program_code(self, html):
		file = open("sponsors.htm", "r")
		soup = BeautifulSoup(html)
		prefixes = []
		links = soup.find_all("a")
		for link in links:
			href = link.get("href")
			if ".html" in href:
				prefixes.append(href)
		return prefixes

	"""Return the html file at the url."""
	def get_html(self, url):
		html = None
		while html is None:
			try:
				r = requests.get(url, cookies=self.cookies)
				if r.status_code == 200:
					html = r.text
			except requests.exceptions.Timeout:
				continue

		return html.encode('utf-8')

	def parse_html(self, html):
		soup = BeautifulSoup(html)
		table = soup.find("table")
		table_rows = table.find_all("tr")
		cancelled = []
		cancelled.append(False)
		for i in range(COURSE_START_OFFSET, len(table_rows)):
			current = table_rows[i].find_all("td")
			space = current[COURSE_CODE_INDEX].get_text().strip()
			if table_rows[i].find(colspan = "5") != None and len(space) != LENGTH_COURSE_CODE:
				cancelled.append(True)
			elif len(space) != LENGTH_COURSE_CODE:
				cancelled.append(False)
			elif len(space) == LENGTH_COURSE_CODE:
				last = table_rows[i-len(cancelled)].find_all("td")
				last_course = last[COURSE_CODE_INDEX].get_text().strip()
				print("Current_row: " + (str)(i))
				print("Section_count: " + (str)(len(cancelled)))
				self.parse_course(last_course, table_rows, i, cancelled)
				cancelled = []
				cancelled.append(table_rows[i].find(colspan = "5") != None)

	def parse_course(self, courseid, table_rows, current_row, cancelled):
		current = table_rows[current_row-len(cancelled)].find_all("td")
		semester = current[SEMESTER_INDEX].get_text().strip()
		title = current[TITLE_INDEX].get_text().strip()
		print(courseid)
		print(semester)
		print(cancelled)
		sections = self.parse_meeting_sections(table_rows, current_row, cancelled)


	def parse_meeting_sections(self, table_rows, current_row, cancelled):
		sections = []
		last_section = None
		for i in range(current_row-len(cancelled), current_row):
			section = []
			section_code = None
			current = table_rows[i].find_all("td")
			if not cancelled[i-current_row]:
				if(table_rows[i].find(colspan = "3") != None): #Handles "Note messages"
					section_code = re.search("\w\d{4}",current[MEETING_SECTION_INDEX-2].get_text().strip()).group(0)
					print(section_code + " ", end="")
					last_section = section_code
					section = [section_code]
					time = re.search("[MTWRFS]{1,3}\d-*\d*", current[TIME_INDEX-2].get_text().strip())
					if(time != None):
						times.append(time.group(0))
						print(time.group(0))
					location_check = [LOCATION]
					section = [section_code, times]
					sections.append(section)
				elif(current[MEETING_SECTION_INDEX].get_text().strip() == ""):
					print(last_section + " ", end="")
					location_check = [LOCATION]
					time = re.search("[MTWRFS]{1,3}\d-*\d*", current[TIME_INDEX].get_text().strip())
					if(time != None):
						sections[-1][1].append(time.group(0))
						print(time.group(0))

				else:
					section_code = re.search("\w\d{4}",current[MEETING_SECTION_INDEX].get_text().strip()).group(0)
					print(section_code + " ",end="")
					last_section = section_code
					section = [section_code]
					times = []
					time = re.search("[MTWRFS]{1,3}\d-*\d*", current[TIME_INDEX].get_text().strip())
					if(time != None):
						times.append(time.group(0))
						print(time.group(0))
					section = [section_code, times]
					location_check = [LOCATION]
					sections.append(section)

		for section in sections:
			print(section)




ct = CourseTimetable("winter")
#ct.get_timetables()
html = ct.get_html("%s/ofr/timetable/%s/%s" % (ct.host, ct.season, "csc.html"))
ct.parse_html(html)
