import os

from cv_crawler.common.logManager import LogManage

PROJECT_NAME = 'cv_crawler'
PROJECT_PATH = os.getcwd()[:os.getcwd().find(PROJECT_NAME)+len(PROJECT_NAME)]

zl_data = {
    'keywords': 'java',
    'startNum': 0,
    'rowsCount': 30,
    'resumeGrade': '',
    'sortColumnName': 'sortUpDate',
    'sortColumn': 'sortUpDate desc',
    'onlyHasImg': False,
    'anyKeyWord': False,
    'hopeWorkCity': '',
    'ageStart': '',
    'ageEnd': '',
    'workYears': '',
    'liveCity': 653,
    'sex': '',
    'edu': '',
    'upDate': 30,
    'companyName': '',
    'jobType': '',
    'desiredJobType': '',
    'industry': '',
    'desiredIndustry': '',
    'careerStatus': '',
    'desiredSalary': '',
    'langSkill': '',
    'hukouCity': '',
    'major': '',
    'onlyLastWork': False
}

if __name__ == '__main__':
    pass