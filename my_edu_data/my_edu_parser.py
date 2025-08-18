from collections import defaultdict
from bs4 import BeautifulSoup

class MyEduFunctions:
    def __init__(self, data):
        self.data = data
    
    def grade_grouper(self, gradel):
        grade_dict = defaultdict(list)
        for student in self.data:
            grade = student['Grade Level']
            grade_dict[grade].append(student)
        return grade_dict[str(gradel)]  # Return the first grade group as an example
    
    def name_reorderer(self):
        for student in self.data:
            name = student['Student Name']
            parts = name.split(', ')
            if len(parts) == 2:
                student['Student Name'] = f"{parts[1]} {parts[0]}"
            else:
                print(f"Unexpected name format: {name}")
                student['Student Name'] = name
        return self.data

    def initialize_last_name(self):
        for student in self.data:
            name = student['Student Name']
            parts = name.split(' ')
            if len(parts) > 2: print(f"Double check the formating of this person: {student['Student Name']} | {parts[0]} {parts[-1][0]}")
            student['Student Name'] = f"{parts[0]} {parts[-1][0]}"
        return self.data
        

class MyEduParser:
    def __init__(self, content):
        self.content = content
    
    def get_table_headers(self):
        ret_vals = []
        soup = BeautifulSoup(self.content, 'html.parser')
        tables = soup.find('table', attrs={'style': 'margin-left: 0px; width: 718px;'}) # NTS: gets the first table which SHOULD be the table on the students hopefully not staff

        spans = tables.find_all('span', attrs={'class': 'dt-column-title'}) # gets rows
        for i in spans: #2do: change to list comprehension to speed it up
            ret_vals.append(i.text)
        
        return ret_vals
    
    def parse_content(self, headers):
        data = []
        soup = BeautifulSoup(self.content, 'html.parser')
        table = soup.find('table', attrs={'style': 'width: 100%;'}) # NTS: gets the first table which SHOULD be the table on the students hopefully not staff
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')

        for row in rows:
            row_data = {}
            cells = row.find_all('td')
            for i in zip(headers, cells): #2do : change to dict comprehension to speed it up
                row_data[i[0]] = i[1].text
            data.append(row_data)
        return data


with open('my_edu_data/cur_my_edu_html', 'r') as f:
    html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    parser = MyEduParser(html_content)
    big_data = parser.parse_content(parser.get_table_headers())
    
    parsed_data = MyEduFunctions(big_data)

    grouped_data = MyEduFunctions(parsed_data.grade_grouper(2))
    grouped_data.name_reorderer()
    stuff = grouped_data.initialize_last_name()

names = [student['Student Name'] for student in stuff]
print(names)
print(len(names))