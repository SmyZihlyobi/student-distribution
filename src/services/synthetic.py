import google.generativeai as genai
import pandas as pd
from config import settings
import io
import os
import re
import csv

genai.configure(api_key=settings.AI)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def generate_synthetic_data(num_teams=2, num_students_per_team=5, num_projects=3):
    """
    Generates synthetic data for teams, students, projects, and team-project compatibility.
    """
    # Generate Teams
    team_response = model.generate_content(f"""
    Сгенерируй {num_teams} синтетические команды студентов в формате CSV. 

    Формат:

    id,team_name,specialization
    1,CloudTeam,"Cloud Engineering"
    2,MLTeam,"Machine Learning"

    Специализации: Cloud, ML, Data, DevOps, Web.
    """)
    teams_csv = team_response.text

    # Generate Students
    students_response = model.generate_content(f"""
    Сгенерируй {num_teams * num_students_per_team} студентов (по {num_students_per_team} для каждой из {num_teams} команд) в формате CSV. 

    Формат:

    id,username,first_name,last_name,desired_role,resume_text,team_id

    Пример для CloudTeam:

    1,bochkarev_egor,Егор,Бочкарёв,"Cloud Engineer",
    "Технологии: AWS, Terraform, Docker", 1

    Пример для MLTeam:

    6,ivanova_anna,Анна,Иванова,"ML Engineer",
    "Технологии: Python, PyTorch, TensorFlow", 2

    Учти, что командам присвоены id от 1 до {num_teams}.
    """)
    students_csv = students_response.text

    # Generate Projects
    projects_response = model.generate_content(f"""
    Сгенерируй {num_projects} проекта для IT-компаний в формате CSV. 

    Формат:

    id,name,description,stack,required_roles,teams_amount,company_id,direction

    Пример:

    1,"Разработка ML-модели для анализа данных",
    "Проект требует команды из 5 ML-инженеров",
    "Python, PyTorch, TensorFlow",
    "ML Engineer, Data Scientist", 1, 1, "ML"

    Учитывай:
    - `teams_amount` — количество команд, которые могут работать над проектом.
    - `required_roles` — роли, которые должны быть в команде (например, "ML Engineer, Data Scientist").
    - `description` - описание проекта в котором часто указывают необходимые навыки
    """)
    projects_csv = projects_response.text

    # Generate Team Compatibility
    team_compatibility_response = model.generate_content(f"""
    Сгенерируй таблицу совместимости команд и проектов в формате CSV. 

    Формат:

    team_id,project_id,compatibility_score

    Пример:

    1,1,0.2 # CloudTeam и ML-проект — низкая совместимость
    2,1,0.9 # MLTeam и ML-проект — высокая совместимость

    Правила:
    1. Если у команды и проекта совпадает специализация (например, ML и ML) → score 0.8-1.0.
    2. Если частично совпадают технологии → score 0.4-0.7.
    3. Если нет пересечений → score 0.0-0.3.

    Сгенерируй данные для {num_teams} команд и {num_projects} проектов.
    """)
    team_compatibility_csv = team_compatibility_response.text

    return {
        "teams": teams_csv,
        "students": students_csv,
        "projects": projects_csv,
        "team_compatibility": team_compatibility_csv
    }

def parse_csv_string(csv_string):
    """Parses a CSV string into a list of lists."""
    f = io.StringIO(csv_string)
    reader = csv.reader(f)
    return list(reader)

def csv_string_from_list(data):
    """Converts a list of lists to a CSV string."""
    f = io.StringIO()
    writer = csv.writer(f)
    writer.writerows(data)
    return f.getvalue().strip()

def clean_csv_data(csv_data):
    """
    Очищает и форматирует CSV данные для корректного сохранения.
    """
    # Удаляем маркеры кода, пустые строки и лишние пробелы
    csv_data = re.sub(r"```csv\n|```", "", csv_data)
    csv_data = re.sub(r'\n\s*\n', '\n', csv_data)  # Удаляем пустые строки
    csv_data = csv_data.strip()
    
    # Читаем данные как CSV
    reader = csv.reader(io.StringIO(csv_data))
    rows = [row for row in reader if any(row)]  # Пропускаем полностью пустые строки
    
    # Форматируем каждую строку
    formatted_rows = []
    for row in rows:
        # Экранируем поля, содержащие запятые
        formatted_row = []
        for field in row:
            field = field.strip()
            if not field:  # Пропускаем пустые поля
                field = ""
            elif ',' in field and not (field.startswith('"') and field.endswith('"')):
                # Удаляем лишние кавычки внутри поля
                field = field.replace('"', '')
                field = f'"{field}"'
            formatted_row.append(field)
        if any(formatted_row):  # Добавляем только непустые строки
            formatted_rows.append(formatted_row)
    
    # Преобразуем обратно в CSV строку
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerows(formatted_rows)
    return output.getvalue()

def get_next_ids(base_path="synthetic"):
    """
    Получает следующие доступные ID для каждой сущности.
    """
    next_ids = {
        "team": 1,
        "student": 1,
        "project": 1
    }
    
    try:
        # Проверяем существующие файлы
        for entity in ["teams", "students", "projects"]:
            filepath = os.path.join(base_path, f"{entity}.csv")
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath, encoding='cp1251')
                    if not df.empty:
                        next_ids[entity[:-1]] = int(df['id'].max()) + 1
                except Exception as e:
                    print(f"Warning: Could not read {entity}.csv: {e}")
    except Exception as e:
        print(f"Warning: Error getting next IDs: {e}")
    
    return next_ids

def update_ids_in_data(data, next_ids):
    """
    Обновляет ID в сгенерированных данных.
    """
    updated_data = {}
    
    for filename, csv_data in data.items():
        # Очищаем данные
        cleaned_data = clean_csv_data(csv_data)
        reader = csv.reader(io.StringIO(cleaned_data))
        rows = list(reader)
        
        if not rows:
            continue
            
        header = rows[0]
        data_rows = rows[1:]
        
        # Определяем тип данных и соответствующий ID
        if filename == "teams":
            current_id = next_ids["team"]
            id_field = 0  # ID находится в первом поле
        elif filename == "students":
            current_id = next_ids["student"]
            id_field = 0
        elif filename == "projects":
            current_id = next_ids["project"]
            id_field = 0
            # Для проектов также обновляем company_id
            company_id_field = 6  # Индекс поля company_id
            current_company_id = 1
        else:
            updated_data[filename] = cleaned_data
            continue
        
        # Обновляем ID
        updated_rows = [header]
        for row in data_rows:
            if len(row) > id_field:
                # Создаем копию строки для изменения
                new_row = row.copy()
                # Обновляем ID
                new_row[id_field] = str(current_id)
                current_id += 1
                
                # Для проектов обновляем company_id
                if filename == "projects" and len(new_row) > company_id_field:
                    new_row[company_id_field] = str(current_company_id)
                    current_company_id = (current_company_id % 10) + 1  # Цикл от 1 до 10
                
                updated_rows.append(new_row)
        
        # Преобразуем обратно в CSV
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(updated_rows)
        updated_data[filename] = output.getvalue()
    
    return updated_data

def append_data_to_csv(data, base_path="synthetic"):
    """
    Appends the generated data to existing CSV files with proper ID handling.
    """
    os.makedirs(base_path, exist_ok=True)
    
    # Получаем следующие доступные ID
    next_ids = get_next_ids(base_path)
    
    # Обновляем ID в данных
    updated_data = update_ids_in_data(data, next_ids)
    
    for filename, csv_data in updated_data.items():
        filepath = os.path.join(base_path, f"{filename}.csv")
        try:
            # Проверяем существование файла и его содержимое
            file_exists = os.path.exists(filepath)

            # Очищаем данные CSV *перед* записью в файл
            cleaned_csv_data = clean_csv_data(csv_data) # Clean data first
            
            if file_exists:
                try:
                    df = pd.read_csv(filepath, encoding='cp1251')
                    is_empty = len(df) == 0
                except Exception as e:
                    print(f"Warning: Could not read existing {filename}.csv: {e}")
                    is_empty = True
            else:
                is_empty = True #If the file doesn't exist, it is "empty"

            # Записываем данные
            if file_exists and not is_empty:
                # Append to existing file, skipping the header
                lines = cleaned_csv_data.splitlines()
                if len(lines) > 1: # Check if cleaned_csv_data has data rows
                    data_without_header = '\n'.join(lines[1:]) # Skip header
                    with open(filepath, "a", encoding='cp1251', newline='') as f: # use newline=''
                        f.write(data_without_header + '\n')
                else:
                    print(f"Skipping append for {filename}.csv because there are no data rows.")
            else:
                # Write to new file, including the header
                with open(filepath, "w", encoding='cp1251', newline='') as f: # use newline=''
                    f.write(cleaned_csv_data + '\n') # Write cleaned data

            print(f"Data appended to {filename}.csv successfully.")

        except Exception as e:
            print(f"Error appending to {filename}.csv: {e}")
            raise
        
if __name__ == '__main__':
    # Example Usage:
    num_teams = 2
    num_students_per_team = 5
    num_projects = 3

    base_path = "synthetic"
    # Generate data multiple times and append to files
    for i in range(3):  # Generate 3 batches of data
        synthetic_data = generate_synthetic_data(
            num_teams=num_teams,
            num_students_per_team=num_students_per_team,
            num_projects=num_projects,
        )
        append_data_to_csv(synthetic_data, base_path)
        print(f"Batch {i+1} of synthetic data generated and appended to CSV files.")