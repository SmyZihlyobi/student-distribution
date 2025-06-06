import google.generativeai as genai
import pandas as pd
from config import settings
import io
import os
import re
import csv
from typing import Dict, List

genai.configure(api_key=settings.AI)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def csv_to_dict_list(csv_data: str) -> List[Dict[str, str]]:
    """Преобразует CSV строку в список словарей."""
    csv_data = re.sub(r'```csv\n|```\n', '', csv_data)
    csv_data = csv_data.strip()

    lines = csv_data.split('\n')
    if not lines:
        return []

    headers = [h.strip() for h in lines[0].split(',')]

    result = []
    for line in lines[1:]:
        if not line.strip():
            continue

        fields = []
        current_field = []
        in_quotes = False

        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                current_field.append(char)
            elif char == ',' and not in_quotes:
                fields.append(''.join(current_field).strip().strip('"'))
                current_field = []
            else:
                current_field.append(char)

        if current_field:
            fields.append(''.join(current_field).strip().strip('"'))

        if len(fields) == len(headers):
            row_dict = dict(zip(headers, fields))
            result.append(row_dict)

    return result

def generate_teams(num_teams: int) -> List[Dict[str, str]]:
    """Генерирует данные для команд."""
    teams_prompt = f"""Сгенерируй {num_teams} команд в CSV формате.
    Формат:

    id,team_name,specialization
    1,CloudTeam,Cloud
    2,MLTeam,ML

    Specializations: Cloud, ML, Data, DevOps, Web.  Team name и specialization должны быть на English.
    """
    team_response = model.generate_content(teams_prompt)
    teams_data = csv_to_dict_list(team_response.text)
    return teams_data

def generate_projects(num_projects: int) -> List[Dict[str, str]]:
    """Генерирует данные для проектов."""
    projects_prompt = f"""Сгенерируй {num_projects} проектов в CSV формате.
    Формат:

    id,name,description,stack,required_roles,teams_amount,company_id,direction
    1,"ML Platform","Разработка платформы для ML","Python, PyTorch, Docker","ML Engineer, DevOps Engineer",2,1,ML
    2,"Cloud Migration","Миграция в облако","AWS, Terraform, Python","Cloud Engineer, DevOps Engineer",1,2,Cloud

    Directions: ML, Cloud, Data, DevOps, Web. Project names, stacks and roles should all be in English.
    descriptions должен быть на русском и описывать проект и необходимые навыки.
    """
    projects_response = model.generate_content(projects_prompt)
    projects_data = csv_to_dict_list(projects_response.text)
    return projects_data

def generate_students(num_students: int, teams: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Generates data for students and assigns them to teams."""

    students_prompt = f"""Сгенерируй {num_students} студентов в CSV формате. Прикрепи их к командам.

    Формат:

    id,username,first_name,last_name,desired_role,resume_text,team_id
    1,ivanov_i,Ivan,Ivanov,"Python Developer","Навыки: Python, Django, Flask",1
    2,petrov_p,Petr,Petrov,"ML Engineer","Навыки: ML, PyTorch, scikit-learn",1

    For the team_id, choose a team from the following options: {", ".join([team["id"] for team in teams])}.  The number of students per team should be roughly equal.

    Roles: Python Developer, ML Engineer, Data Scientist, DevOps Engineer, Frontend Developer, Backend Developer. All text should be in English.
    resume_text должен содержать навыки студента на русском языке.
    """
    students_response = model.generate_content(students_prompt)
    students_data = csv_to_dict_list(students_response.text)
    return students_data

def generate_team_compatibility(teams: List[Dict[str, str]], projects: List[Dict[str, str]], students: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Генерирует совместимость между командами и проектами, учитывая данные студентов."""

    team_skills = {}
    for team in teams:
        team_id = team['id']
        team_skills[team_id] = []
        for student in students:
            if student['team_id'] == team_id:
                team_skills[team_id].append(student['resume_text'])

    formatted_teams = "\n".join([f"{team['id']}: {team['team_name']} ({team['specialization']}). Skills: {', '.join(team_skills.get(team['id'], []))}" for team in teams])
    formatted_projects = "\n".join([f"{project['id']}: {project['name']} ({project['description']})" for project in projects])

    compatibility_prompt = f"""
    Given the following teams, projects, and student skills, generate a table of team and project compatibility scores in CSV format.

    Teams:
    {formatted_teams}

    Projects:
    {formatted_projects}

    Format:

    team_id,project_id,compatibility_score
    1,1,0.85
    1,2,0.45
    2,1,0.65
    2,2,0.90

    The compatibility score should be a number between 0 and 1, representing how well suited a team is for a project. Base the score on the team's specialization, the project's description, stack, required roles, AND the skills of the students in each team. A higher score means a better fit.
    Each possible team/project combination must have an entry. All data and descriptions are in English. Do not leave anything out.
    """

    compatibility_response = model.generate_content(compatibility_prompt)
    compatibility_data = csv_to_dict_list(compatibility_response.text)
    return compatibility_data

def clean_csv_data(csv_data: str) -> str:
    """Очищает и форматирует CSV данные."""
    csv_data = re.sub(r'```csv\n|```\n', '', csv_data)
    csv_data = re.sub(r'\n\s*\n', '\n', csv_data)
    csv_data = csv_data.strip()

    lines = csv_data.split('\n')
    cleaned_lines = []

    for line in lines:
        if not line.strip():
            continue

        fields = []
        current_field = []
        in_quotes = False

        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                current_field.append(char)
            elif char == ',' and not in_quotes:
                fields.append(''.join(current_field).strip())
                current_field = []
            else:
                current_field.append(char)

        if current_field:
            fields.append(''.join(current_field).strip())

        processed_fields = []
        for field in fields:
            if ',' in field and not (field.startswith('"') and not field.endswith('"')) :
                field = f'"{field}"'

            processed_fields.append(field)

        cleaned_lines.append(','.join(processed_fields))

    return '\n'.join(cleaned_lines)

def update_ids_in_data(data: Dict[str, List[Dict]], next_ids: Dict[str, int]) -> Dict[str, List[Dict]]:
    """Обновляет ID в данных, используя следующие доступные ID."""
    updated_data = {}

    for data_type, items in data.items():
        if data_type == 'team_compatibility':
            continue

        if not items:
            updated_data[data_type] = []
            continue

        updated_items = []
        for item in items:
            updated_item = item.copy()

            if data_type == 'teams':
                updated_item['id'] = str(next_ids['teams'])
                next_ids['teams'] += 1
            elif data_type == 'students':
                updated_item['id'] = str(next_ids['students'])
                next_ids['students'] += 1
            elif data_type == 'projects':
                updated_item['id'] = str(next_ids['projects'])
                company_id = (next_ids['projects'] - 1) % 10 + 1
                updated_item['company_id'] = str(company_id)
                next_ids['projects'] += 1

            updated_items.append(updated_item)

        updated_data[data_type] = updated_items
    team_id_mapping = {}
    project_id_mapping = {}

    for item in updated_data.get('teams', []):
        team_id_mapping[item['id']] = item['id']

    for item in updated_data.get('projects', []):
        project_id_mapping[item['id']] = item['id']
    if 'team_compatibility' in data:
        updated_compatibility = []
        for item in data['team_compatibility']:
            updated_item = item.copy()
            old_team_id = item['team_id']
            old_project_id = item['project_id']
            if old_team_id in team_id_mapping and old_project_id in project_id_mapping:
                updated_item['team_id'] = team_id_mapping[old_team_id]
                updated_item['project_id'] = project_id_mapping[old_project_id]
                updated_compatibility.append(updated_item)

        updated_data['team_compatibility'] = updated_compatibility

    return updated_data

def get_next_ids(base_path: str = "synthetic") -> Dict[str, int]:
    """Получает следующие доступные ID для каждого типа данных."""
    next_ids = {
        'teams': 1,
        'students': 1,
        'projects': 1
    }

    for data_type in ['teams', 'students', 'projects']:
        file_path = os.path.join(base_path, f"{data_type}.csv")
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, encoding='cp1251')
                if 'id' in df.columns and not df.empty:
                    next_ids[data_type] = int(df['id'].max()) + 1
            except Exception as e:
                print(f"Warning: Could not read {data_type}.csv: {e}")

    return next_ids

def dict_list_to_csv_string(data: List[Dict[str, str]], headers: List[str]) -> str:
    """Converts a list of dictionaries to a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

    writer.writerow(headers)
    for item in data:
        row = [item.get(header, "") for header in headers]
        writer.writerow(row)

    return output.getvalue()

def append_data_to_csv(all_data: Dict[str, List[Dict]], base_path: str = 'synthetic') -> None:
    """Добавляет данные в CSV файлы с правильной обработкой ID."""
    os.makedirs(base_path, exist_ok=True)

    next_ids = get_next_ids(base_path)
    print(f"Next IDs: {next_ids}")

    updated_data = update_ids_in_data(all_data, next_ids)
    print("Updated data", updated_data)

    headers = {
        'teams': ['id', 'team_name', 'specialization'],
        'students': ['id', 'username', 'first_name', 'last_name', 'desired_role', 'resume_text', 'team_id'],
        'projects': ['id', 'name', 'description', 'stack', 'required_roles', 'teams_amount', 'company_id', 'direction'],
        'team_compatibility': ['team_id', 'project_id', 'compatibility_score']
    }

    for data_type, items in updated_data.items():
        file_path = os.path.join(base_path, f"{data_type}.csv")
        print(f"Writing data to {file_path}")

        csv_data = dict_list_to_csv_string(items, headers[data_type])
        file_exists = os.path.exists(file_path)

        with open(file_path, 'a', encoding='cp1251', newline='') as f:
            if not file_exists:
                f.write(csv_data)
            else:
                lines = csv_data.splitlines()
                f.write('\n'.join(lines[1:]))
            print(f"Data saved to {file_path}")

def team_project_matrix(teams: List[Dict[str, str]], projects: List[Dict[str, str]], compatibility: List[Dict[str, str]]):
    print ("Here is team project compatiability matrix")
    team_ids = [team['id'] for team in teams]
    project_ids = [project['id'] for project in projects]
    matrix = pd.DataFrame(index=team_ids, columns=project_ids)

    for row in compatibility:
        team_id = row['team_id']
        project_id = row['project_id']
        compatibility_score = row['compatibility_score']
        matrix.loc[team_id, project_id] = compatibility_score

    print(matrix)
