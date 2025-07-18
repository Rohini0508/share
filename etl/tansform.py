# etl/transform.py
import pandas as pd

def transform_data(data):
    df = pd.DataFrame(data)

    df.rename(columns={
        "Title": "project_name",
        "Status": "status",
        "ProjectManager": "project_manager",
        "StartDate": "start_date",
        "EndDate": "end_date",
        "Budget": "budget",
        "Department": "department"
    }, inplace=True)

    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce').dt.date
    df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce').dt.date
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce').fillna(0)
    df['status'] = df['status'].astype(str).str.title()

    df.fillna({'project_manager': 'Unknown', 'department': 'General'}, inplace=True)

    return df[['project_name', 'status', 'project_manager', 'start_date', 'end_date', 'budget', 'department']]
