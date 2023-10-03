import plotly.express as px
import pandas as pd
def clean_data(df):
    # Separate city and state
    df[['city', 'state']] = df['location'].str.extract(r'(?P<city>.*(?=\s[A-Z]{2}$)) (?P<state>[A-Z]{2}$)')
    
    # Define the function to extract min and max salary values
    def extract_min_max(salary):
        if pd.isna(salary) or salary is None:
            return None, None
        clean_salary = salary.replace('$', '').replace(',', '').split(' (')[0].replace('\xa0', ' ')
        try:
            if 'Per Hour' in clean_salary:
                min_val, max_val = [float(val) for val in clean_salary.split(' Per Hour')[0].split(' - ')]
                # Convert hourly to yearly
                min_val, max_val = [val * 40 * 50 for val in (min_val, max_val)]
            elif 'K' in clean_salary:
                min_val, max_val = [float(val.split(' ')[0].replace('K', '')) * 1000 for val in clean_salary.split(' - ')]
        except:
            return None, None
        return min_val, max_val

    # Apply the function to extract and calculate the salary values
    df['min_salary'] = df['salary'].apply(lambda x: extract_min_max(x)[0] if not pd.isna(x) and extract_min_max(x)[0] is not None else None)
    df['max_salary'] = df['salary'].apply(lambda x: extract_min_max(x)[1] if not pd.isna(x) and extract_min_max(x)[1] is not None else None)
    df['avg_salary'] = (df['min_salary'] + df['max_salary']) / 2

    return df


def plot_avg_salary_distribution(df):
    fig = px.histogram(df, x='avg_salary', nbins=20, title='Average SWE Interns Pay')
    fig.update_layout(xaxis_title='Pay ($)')
    return fig.to_html(full_html=False)

def plot_jobs_by_state(df):
    state_counts = df['state'].value_counts()
    fig = px.bar(state_counts, title='Number of Jobs by State')
    fig.update_layout(xaxis_title='State', yaxis_title='Number of Jobs')
    return fig.to_html(full_html=False)

def plot_top_cities_by_jobs(df):
    city_counts = df['city'].value_counts().head(10)
    fig = px.bar(city_counts, title='Top 10 Cities by Job Count')
    fig.update_layout(xaxis_title='City', yaxis_title='Number of Jobs')
    return fig.to_html(full_html=False)

def plot_avg_salary_by_state(df):
    average_salary_by_state = df.groupby('state')['avg_salary'].mean().reset_index().sort_values(by='avg_salary', ascending=False)
    fig = px.bar(average_salary_by_state, x='state', y='avg_salary', title='Average Salary by State')
    return fig.to_html(full_html=False)

def plot_salaries_by_state(df):
    fig = px.strip(df, x='state', y='avg_salary', title='Scatterplot of Salaries by State')
    return fig.to_html(full_html=False)

def plot_salary_density_by_state(df):
    top_states = df['state'].value_counts().index[:10]
    subset = df[df['state'].isin(top_states)]
    fig = px.histogram(subset, x='avg_salary', color='state', histnorm='density', title='Density Plot of Salaries by State')
    fig.update_layout(xaxis_title='Salary ($)', yaxis_title='Density')
    return fig.to_html(full_html=False)

def plot_salary_boxplot_by_state(df):
    fig = px.box(df, x='state', y='avg_salary', title='Boxplot of Salaries by State')
    return fig.to_html(full_html=False)

def plot_company_wise_job_postings(df):
    # Counting job postings by company
    company_counts = df['name-of-company'].value_counts().head(10)  # Considering the top 10 companies for visualization

    # Creating the bar plot
    fig = px.bar(company_counts, 
                 x=company_counts.index, 
                 y=company_counts.values, 
                 title='Top Companies with Most Job Postings', 
                 labels={'x': 'Company', 'y': 'Number of Job Postings'})

    return fig.to_html(full_html=False)