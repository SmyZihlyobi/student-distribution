import asyncio
import os
import pandas as pd
from services.synthetic import generate_teams, generate_projects, generate_students, generate_team_compatibility, append_data_to_csv, get_next_ids

async def main():
    total_teams = 100
    students_per_team = 5
    total_projects = 100
    

    batch_size = 10

    base_path = os.path.join('synthetic')

    print("Cleaning up existing files...")
    for filename in ['teams', 'students', 'projects', 'team_compatibility']:
        file_path = os.path.join(base_path, f"{filename}.csv")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed {filename}.csv")
            except Exception as e:
                print(f"Warning: Could not remove {filename}.csv: {e}")
    
    next_ids = get_next_ids(base_path)
    print(f"Initial Next IDs: {next_ids}")

    team_count = 0
    project_count = 0
    student_count = 0


    num_batches = (total_teams + batch_size - 1) // batch_size

    print(f"\nStarting data generation:")
    print(f"Total teams: {total_teams}")
    print(f"Students per team: {students_per_team}")
    print(f"Total projects: {total_projects}")
    print(f"Number of batches: {num_batches}")
    print("---")

    all_teams_data = []
    all_projects_data = []
    all_students_data = []


    for batch in range(num_batches):
        current_batch_size = min(batch_size, total_teams - team_count)
        current_projects_size = min(batch_size, total_projects - project_count)
        
        print(f"Generating batch {batch + 1}/{num_batches}")
        print(f"Teams in batch: {current_batch_size}")
        print(f"Projects in batch: {current_projects_size}")


        teams_data = generate_teams(current_batch_size)
        team_ids_in_batch = [x['id'] for x in teams_data]
        team_count = team_count + len(teams_data)


        projects_data = generate_projects(current_projects_size)
        project_ids_in_batch = [x['id'] for x in projects_data]

        project_count = project_count + len(projects_data)


        total_students = len(team_ids_in_batch) * students_per_team 
        students_data = generate_students(total_students, teams_data)

        all_teams_data.extend(teams_data)
        all_projects_data.extend(projects_data)
        all_students_data.extend(students_data)

        team_compatibility_data = generate_team_compatibility(all_teams_data, all_projects_data, all_students_data)

        all_data = {
            'teams': teams_data,
            'students': students_data,
            'projects': projects_data,
            'team_compatibility': team_compatibility_data
        }

        append_data_to_csv(all_data, base_path=base_path)


        print(f"Batch {batch + 1} successfully saved")
        print("---")

    print("Data generation complete!")

    try:
        for filename in ['teams', 'students', 'projects']:
            file_path = os.path.join(base_path, f"{filename}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, encoding='cp1251')
                print(f"\nStatistics for {filename}.csv:")
                print(f"Number of records: {len(df)}")
                print(f"Columns: {df.columns.tolist()}")
                print(f"First few IDs: {df['id'].head().tolist()}")
                print(f"Last few IDs: {df['id'].tail().tolist()}")

                if len(df['id'].unique()) != len(df):
                    print(f"Warning: {filename}.csv contains duplicate IDs!")
            else:
                print(f"\nWarning: {filename}.csv not found!")
    except Exception as e:
        print(f"\nError verifying results: {e}")

if __name__ == "__main__":
    asyncio.run(main())