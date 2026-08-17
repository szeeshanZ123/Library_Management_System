import pandas as pd
import numpy as np
students = {

    "Roll":[1,2,3,4,5,6],

    "Name":["Aman","Rahul","Aisha","Sara","Ali","Neha"],

    "Semester":[3,3,4,4,3,4],

    "Python":[78,70,90,55,82,88],

    "DBMS":[65,88,76,62,91,84],

    "Statistics":[82,75,84,68,79,91],

    "Attendance":[82,68,91,72,88,94],

    "SGPI":[7.2,6.8,8.5,6.5,7.9,9.1],

    "Exam_Date":[
        "15-05-2026",
        "15-05-2026",
        "20-06-2026",
        "20-06-2026",
        "15-05-2026",
        "20-06-2026"
    ]

}

df = pd.DataFrame(students)
'''
print(df)
print(df.describe())'''

'''print(df.head())
print(df.tail())
print(df.info())
print(df.describe())
print(df.columns)
print(df.shape)'''
df['Exam_Date']=pd.to_datetime(df['Exam_Date'],format='%d-%m-%Y')
df.year = df['Exam_Date'].dt.year
#print(df.year)
print(df.isnull().sum())