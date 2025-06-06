import asyncio
import os
import pandas as pd
from services.synthetic import generate_synthetic_data, append_data_to_csv, get_next_ids

async def main():
    # Parameters for data generation
    total_teams = 1000
    students_per_team = 5
    total_projects = 1000
    
    # Batch size
    batch_size = 20
    
    # Base path for synthetic data
    base_path = os.path.join('synthetic')
    
    # Очищаем существующие файлы
    print("Cleaning up existing files...")
    for filename in ['teams', 'students', 'projects', 'team_compatibility']:
        file_path = os.path.join(base_path, f"{filename}.csv")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed {filename}.csv")
            except Exception as e:
                print(f"Warning: Could not remove {filename}.csv: {e}")
    
    # Calculate the number of batches
    num_batches = (total_teams + batch_size - 1) // batch_size
    
    print(f"\nStarting data generation:")
    print(f"Total teams: {total_teams}")
    print(f"Students per team: {students_per_team}")
    print(f"Total projects: {total_projects}")
    print(f"Number of batches: {num_batches}")
    print("---")
    
    # Generate data in batches
    for batch in range(num_batches):
        current_batch_size = min(batch_size, total_teams - batch * batch_size)
        current_projects_size = min(batch_size, total_projects - batch * batch_size)
        
        print(f"Generating batch {batch + 1}/{num_batches}")
        print(f"Teams in batch: {current_batch_size}")
        print(f"Projects in batch: {current_projects_size}")
        
        # Generate data for the current batch
        synthetic_data = generate_synthetic_data(
            num_teams=current_batch_size,
            num_students_per_team=students_per_team,
            num_projects=current_projects_size
        )
        
        # Save data
        append_data_to_csv(synthetic_data, base_path=base_path)
        print(f"Batch {batch + 1} successfully saved")
        print("---")
    
    print("Data generation complete!")
    
    # Verify results
    try:
        # Проверяем все файлы
        for filename in ['teams', 'students', 'projects']:
            file_path = os.path.join(base_path, f"{filename}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, encoding='cp1251')
                print(f"\nStatistics for {filename}.csv:")
                print(f"Number of records: {len(df)}")
                print(f"Columns: {df.columns.tolist()}")
                print(f"First few IDs: {df['id'].head().tolist()}")
                print(f"Last few IDs: {df['id'].tail().tolist()}")
                
                # Проверяем уникальность ID
                if len(df['id'].unique()) != len(df):
                    print(f"Warning: {filename}.csv contains duplicate IDs!")
            else:
                print(f"\nWarning: {filename}.csv not found!")
    except Exception as e:
        print(f"\nError verifying results: {e}")

if __name__ == "__main__":
    asyncio.run(main())