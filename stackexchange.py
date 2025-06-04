# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Title: Visualising NHANES dataset


# # Introduction: 
# In this task, I explored data from the National Health and Nutrition Examination Survey (NHANES), a large-scale survey conducted to assess the health and nutritional status of adults and children in the United States. The datasets I worked with included various modules such as demographics, body measurements, alcohol use, dietary intake, and blood test results. These files were provided in .xpt format, which I imported using the pyreadstat library. After importing the datasets, I merged them on the unique participant identifier SEQN to create a unified DataFrame for analysis.
# To prepare the data, I cleaned the merged DataFrame by removing duplicate records, dropping columns with missing values, and eliminating unnecessary variables based on a careful review of the NHANES documentation. I also renamed and recoded multiple columns to make them more human-readable and suitable for analysis. This included converting coded values (such as gender, race, and participation status) into descriptive labels, which helped make the analysis more intuitive and easier to interpret.
# Following data preparation, I performed exploratory analysis using value_counts() and crosstab functions to understand the distribution and relationships among key variables like age group, gender, language of interview, country of birth, and proxy/interpreter usage. These insights guided the development of five visualisations using the Bokeh library, which allowed me to create interactive, aesthetically appealing plots such as heatmaps, scatter plots, and more. Throughout the task, I also reflected on the considerations and limitations of working with survey data, particularly when analyzing sensitive variables such as race, accessibility needs, and participation patterns.

import pandas as pd

# # Installing required package 
# The following command installs the pyreadstat package, a Python interface to the ReadStat C library. This library allows for fast and efficient reading Stata data files directly into pandas DataFrames. 

pip install pyreadstat

import pyreadstat

# # Loading files (in .xpt format) into dataframe
# The following code uses the pyreadstat library to load multiple NHANES .xpt (SAS transport) files into pandas DataFrames. Each of these files contains data from a different NHANES survey module, including demographics, body measurements, alcohol use, complete blood counts, and dietary intake. The function pyreadstat.read_xport() returns a tuple where the first element is the actual dataset in the form of a pandas DataFrame, and the second element contains metadata such as column labels and data types. By appending [0] to each function call, we extract only the DataFrame portion, which is what we need for further data analysis. 

df1= pyreadstat.read_xport(r"C:\Users\YAKSH CHEEMA\Downloads\P_DEMO.xpt")[0]
df2= pyreadstat.read_xport(r"C:\Users\YAKSH CHEEMA\Downloads\P_BMX.xpt")[0]
df3= pyreadstat.read_xport(r"C:\Users\YAKSH CHEEMA\Downloads\P_ALQ.xpt")[0]
df4= pyreadstat.read_xport(r"C:\Users\YAKSH CHEEMA\Downloads\P_CBC.xpt")[0]
df5= pyreadstat.read_xport(r"C:\Users\YAKSH CHEEMA\Downloads\P_DR1TOT.xpt")[0]


# # Merging dataframes 
# This code merges the five individual NHANES DataFrames into a single combined dataset called dfs. Each merge is performed on the SEQN column, which serves as the unique participant identifier across all NHANES modules. The how="left" parameter ensures that all participants present in the main demographics file (df1) are retained, even if corresponding records from the other modules are missing. This approach preserves the full sample while integrating additional information from body measurements, alcohol use, blood tests, and dietary intake into one unified DataFrame, ready for analysis.
#

dfs= df1.merge(df2, on= "SEQN", how= "left")\
     .merge(df3, on= "SEQN", how= "left")\
     .merge(df4, on= "SEQN", how= "left")\
     .merge(df5, on= "SEQN", how= "left")


dfs.shape

dfs.info()

# # Filtering Data

# This line removes any duplicate rows from the merged dataset dfs to ensure that each participant record is unique. 

dfs.drop_duplicates(inplace=True)

# This line removes all columns from the dfs DataFrame that contain any missing values. This step is useful for simplifying the dataset by retaining only complete variables, especially when preparing data for visualisation or modeling where missing values could cause errors or skew results.

dfs.dropna(axis= 1, how= 'any', inplace= True)

dfs.shape

dfs.info()

dfs

# I deleted the columns SEQN and SDDSRVYR from the dfs DataFrame because, after reading the documentation on the NHANES website, I found that these columns were not useful for my analysis. SEQN is just a participant identifier used for merging the files, and SDDSRVYR indicates the survey cycle, which wasn't relevant for my current task since all the data comes from the same cycle. Removing them helped simplify the dataset and focus only on the variables that actually matter for my visualisations and insights.

dfs.drop(columns= ['SEQN','SDDSRVYR'], inplace= True)

dfs.shape

# I deleted the column RIDRETH1 from the dfs DataFrame because, after comparing it with RIDRETH3, I found that the only difference was that RIDRETH1 did not include the Asian population category, whereas RIDRETH3 provides a more complete representation of race/ethnicity, including Asians. Since RIDRETH3 is more comprehensive, I decided to keep it and remove RIDRETH1 to avoid redundancy in the dataset.

dfs.drop(columns= 'RIDRETH1', inplace= True)

# # Decoding 
# **Changing column names:** 
# I carefully checked the NHANES website and read through the documentation for each dataset to understand what the columns represent. Based on that, I renamed several columns in the dfs DataFrame to make them more readable and meaningful for my analysis. For example, I renamed RIDSTATR to ParticipationStatus, RIAGENDR to Gender, and RIDAGEYR to AgeGroup. I followed this approach for all key variables like race, country of birth, interview language, interpreter and proxy use, and weight variables.

dfs.rename(columns= {
    'RIDSTATR': 'ParticipationStatus',
    'RIAGENDR': 'Gender',
    'RIDAGEYR': 'AgeGroup',
    'RIDRETH3': 'Race',
    'DMDBORN4': 'CountryofBirth',
    'SIALANG': 'LanguageofInterview',
    'SIAPROXY': 'ProxyUsed',
    'SIAINTRP': 'InterpreterUsed',
    'WTINTPRP': 'InterviewWeight',
    'WTMECPRP': 'ExamWeight',
    'SDMVPSU': 'VariancePSU',
    'SDMVSTRA': 'VarianceStratum'
}, inplace= True)

# **Decoding column values **
# I performed these mappings after checking the NHANES documentation, where I found that many of the columns used numeric codes to represent categorical values. For example, ParticipationStatus used 1 and 2 to indicate whether a person was only interviewed or both interviewed and examined, and Gender used 1.0 and 2.0 for male and female. To make the dataset more readable and easier to interpret, I converted these coded values into clear labels like "Male", "Female", "English", "Yes", "No", and so on.

dfs['ParticipationStatus']= dfs['ParticipationStatus'].map({1: 'Interviewed only', 2: 'Interviewed and Examined'})
dfs['Gender']= dfs['Gender'].map({1.0: 'Male', 2.0: 'Female'})
dfs['AgeGroup']= dfs['AgeGroup'].apply(lambda x: '80 or above' if x== 80 else 'Below 80' )
dfs['Race']= dfs['Race'].map({1.0: 'Mexican American', 2.0: 'Other Hispanic', 3.0: 'Non- Hispanic Black', 4.0: 'Non- Hispanic White', 6.0: 'Non- Hispanic Asian', 7.0: 'Other Race'})
dfs['CountryofBirth']= dfs['CountryofBirth'].map({1.0: 'US', 2.0: 'Others', 77.0: 'Refused', 99.0: 'Unknown'})
dfs['LanguageofInterview']= dfs['LanguageofInterview'].map({1.0: 'English', 2.0: 'Spanish'})
dfs['ProxyUsed']=dfs['ProxyUsed'].map({1.0: 'Yes', 2.0: 'No'})
dfs['InterpreterUsed']= dfs['InterpreterUsed'].map({1.0: 'Yes', 2.0: 'No'})


# # Exploring Categorical Variable Distributions 
# I used the value_counts() function to quickly examine the distribution of values in each of the key categorical columns. This helped me understand how the data is spread across different categories such as participation status, gender, age group, race, country of birth, language of interview, and whether a proxy or interpreter was used. 

print(dfs['ParticipationStatus'].value_counts())
print("---------------------------------------")
print(dfs['Gender'].value_counts())
print("---------------------------------------")
print(dfs['AgeGroup'].value_counts())
print("---------------------------------------")
print(dfs['Race'].value_counts())
print("---------------------------------------")
print(dfs['CountryofBirth'].value_counts())
print("---------------------------------------")
print(dfs['LanguageofInterview'].value_counts())
print("---------------------------------------")
print(dfs['ProxyUsed'].value_counts())
print("---------------------------------------")
print(dfs['InterpreterUsed'].value_counts())

# # Examining relationships between different attributes

# I used a crosstab to examine the relationship between AgeGroup and ProxyUsed. This allowed me to see how proxy usage varies between participants who are below 80 years old and those who are 80 or above. The crosstab displays the count of participants in each age group who either did or did not use a proxy, helping me identify any patterns or significant differences in accessibility needs based on age. I used the same approach for three additional comparisons: Race vs LanguageofInterview, CountryofBirth vs InterpreterUsed, and ParticipationStatus vs Gender.

pd.crosstab(dfs['AgeGroup'], dfs['ProxyUsed'])


# Surprisingly, proxy usage was more common among participants below 80 years of age, with nearly 36% requiring assistance during their interviews. In contrast, participants aged 80 or above had a much lower rate of proxy use, accounting for only 59 out of 682 individuals. This contradicts common assumptions that older adults are more likely to need assistance, and may reflect differences in survey engagement or living situations across age groups.

pd.crosstab(dfs['Race'], dfs['LanguageofInterview'])

# Language needs varied significantly across racial groups. Spanish was frequently used among Mexican American and Other Hispanic participants, with these two groups having hundreds of interviews conducted in Spanish. Meanwhile, Non-Hispanic White, Black, Asian, and Other Race participants almost exclusively conducted their interviews in English, indicating that Spanish-language resources are particularly critical for Hispanic subpopulations.

pd.crosstab(dfs['Gender'], dfs['ParticipationStatus'])

# Participation in both the interview and examination components of the survey was high across genders, with only a small portion of individuals completing the interview alone. Interestingly, female participants were slightly more likely to complete the full examination process compared to males, with 92% of females and 91% of males participating fully.

pd.crosstab(dfs['CountryofBirth'], dfs['InterpreterUsed'])

# Interpreter assistance was used far more often by participants born outside the United States, with 348 non-U.S. born individuals needing interpreters compared to only 52 among U.S.-born respondents. This highlights the significant impact of language barriers among the immigrant population and underscores the importance of providing interpretation services to ensure accessibility and accurate data collection in public health research.

# The following code generates a grouped bar chart using Bokeh to visualize the estimated population coverage of NHANES participants who completed both the interview and physical examination, broken down by race and participation status. It uses the ExamWeight variable to reflect population representation, not individual counts, and includes hover tooltips and value labels for enhanced readability.

# # Visualization 1: Weighted Participation Status by Race

# **Objective**
# To visualize the estimated U.S. population representation of NHANES participants who completed both the interview and the physical examination, broken down by racial group and participation status. This helps to understand the demographic distribution in the weighted dataset, not just raw participant counts.

# +

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, LabelSet, NumeralTickFormatter
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20

# Group and prepare data
grouped = (
    dfs.groupby(['Race', 'ParticipationStatus'])['ExamWeight']
    .sum()
    .reset_index()
)

# Calculate percentages within each race group
grouped['TotalByRace'] = grouped.groupby('Race')['ExamWeight'].transform('sum')
grouped['Percentage'] = (grouped['ExamWeight'] / grouped['TotalByRace']) * 100

# Handle very small values for display
grouped['DisplayWeight'] = grouped['ExamWeight'].apply(lambda x: x if x > 100000 else 100000)

# Prepare x-axis as factor pairs
grouped['x'] = list(zip(grouped['Race'], grouped['ParticipationStatus']))

# Label for bar tops
grouped['LabelText'] = grouped.apply(
    lambda row: f"{int(row['ExamWeight']):,} ({row['Percentage']:.1f}%)", axis=1
)

# Create ColumnDataSource
source = ColumnDataSource(grouped)

# Build figure
p = figure(
    x_range=FactorRange(*grouped['x']),
    height=500,
    width=1000,
    title="Weighted Participation Status by Race (with Percentages)",
    toolbar_location=None,
    tools=""
)

# Draw bars
p.vbar(
    x='x',
    top='DisplayWeight',
    width=0.8,
    source=source,
    fill_color=factor_cmap('x',
        palette=Category20[20],
        factors=list(dfs['ParticipationStatus'].unique()),
        start=1, end=2)
)

# Hover tool
hover = HoverTool(tooltips=[
    ("Race", "@Race"),
    ("Participation", "@ParticipationStatus"),
    ("Weighted Count", "@ExamWeight{0,0}"),
    ("Percent", "@Percentage{0.0}%")
])
p.add_tools(hover)

# Labels on top of bars
labels = LabelSet(
    x='x',
    y='DisplayWeight',
    text='LabelText',
    y_offset=5,
    text_font_size="8pt",
    text_align="center",
    source=source
)
p.add_layout(labels)

# Axis styling
p.yaxis.formatter = NumeralTickFormatter(format="0,0")
p.xaxis.major_label_orientation = 1.2
p.xaxis.axis_label = "Race & Participation Status"
p.yaxis.axis_label = "Weighted Population"
p.xgrid.grid_line_color = None
p.title.text_font_size = "14pt"

# Show plot
show(p)

# -

# **Description:**
#
# This visualization presents the estimated population coverage of NHANES participants who completed both the interview and the physical examination, broken down by race and participation status. The key metric used is ExamWeight, which does not represent individual participants directly, but rather the number of people in the U.S. population that each participant represents. For those who were only interviewed and did not complete the examination, NHANES assigns an ExamWeight of 0.0.
# The dataset was grouped by race and participation status, and the ExamWeight values were summed to calculate the total estimated population represented by each group. Since bars representing “Interviewed only” participants typically have a summed weight of zero, a display value (DisplayWeight) was added to ensure they remain visible in the chart for comparative purposes. The visualization uses grouped bars for each racial group, enhanced with hover tooltips and numeric value labels to improve readability and insight.
#
# **Conslusion:**
#
# The visualization highlights that among those who completed both the interview and exam, the estimated population distribution is relatively balanced across racial groups. “Interviewed only” participants appear with a value of zero, not because no one participated, but because NHANES does not assign them a weight in the exam-based sample. This reinforces the idea that the chart reflects population representation, not raw participation.
# The key takeaway is that the NHANES examination data is designed to be statistically representative of the U.S. population, and ExamWeight enables analyses to scale up the findings. Thus, the height of the bars represents how many people in the U.S. each race contributes to the weighted dataset, rather than how many individuals actually participated.


# # Visualization 2: Language of Interview by Race (Weighted)

# **Objective**
# To explore the distribution of interview languages (English vs. Spanish) among different racial groups in the NHANES dataset, using population-weighted values. This helps assess linguistic accessibility and the need for multilingual survey support across racial demographics.

# +
import pandas as pd
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.transform import dodge
from bokeh.palettes import Category10

output_notebook()

# Group data and sum InterviewWeight
lang_group = (
    dfs.groupby(['Race', 'LanguageofInterview'])['InterviewWeight']
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

# Create a ColumnDataSource
source = ColumnDataSource(lang_group)

# Create figure
races = lang_group['Race'].tolist()
p = figure(x_range=races, height=500, width=950,
           title="Language of Interview by Race (Weighted)",
           toolbar_location=None, tools="")

# Plot stacked bars
p.vbar(x=dodge('Race', -0.15, range=p.x_range), top='English', width=0.3,
       source=source, color=Category10[3][0], legend_label="English")

p.vbar(x=dodge('Race', 0.15, range=p.x_range), top='Spanish', width=0.3,
       source=source, color=Category10[3][1], legend_label="Spanish")

# Add hover tool
hover = HoverTool(tooltips=[
    ("Race", "@Race"),
    ("English (Weighted)", "@English{0,0}"),
    ("Spanish (Weighted)", "@Spanish{0,0}")
])
p.add_tools(hover)

# Styling
p.yaxis.axis_label = "Weighted Population"
p.xaxis.axis_label = "Race"
p.xaxis.major_label_orientation = 1.2
p.yaxis.formatter = NumeralTickFormatter(format="0,0")
p.xgrid.grid_line_color = None
p.legend.location = "top_right"
p.title.text_font_size = "14pt"

# Show the plot
show(p)

# -

# **Description:**
#
# This visualization explores the relationship between race and language preference during interviews in the NHANES dataset. Specifically, it displays the estimated population-level distribution of participants who were interviewed in either English or Spanish, broken down by racial groups.
# To generate the chart, the dataset was grouped by Race and LanguageofInterview, and the InterviewWeight for each combination was summed. InterviewWeight reflects how many people in the broader U.S. population each participant represents — making it appropriate for measuring national-level language accessibility needs. The chart is rendered as a grouped bar chart, with each racial group displaying two bars: one for English and one for Spanish. Hover tooltips reveal the weighted population figures for each language, and the axes and labels are formatted for readability and clarity.
#
# **Conclusion:**
#
# The visualization reveals clear and meaningful patterns in language use across racial groups. Spanish was predominantly used among Mexican American and Other Hispanic participants, reflecting the linguistic diversity and accessibility requirements of these communities. In contrast, nearly all participants identified as Non-Hispanic White, Non-Hispanic Black, Non-Hispanic Asian, and Other Race were interviewed in English, with negligible use of Spanish.
# These findings suggest that while English remains the default language of interview for the majority of racial groups, Spanish-language resources are essential for effective communication and inclusion of Hispanic subpopulations. This has important implications for the design of health surveys and public health services, emphasizing the need for multilingual support to ensure equitable participation and accurate data collection.

# # Visualization 3: Accessibility Support Need by Age Group (Weighted %)

# **Objective**
# To analyze the percentage of NHANES participants who required accessibility support (either a proxy or an interpreter) during their interviews, across two age groups: “Below 80” and “80 or above.” This helps identify age-related support patterns in data collection.

# +
import pandas as pd
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.transform import transform
from bokeh.palettes import OrRd

output_notebook()

# Prepare simplified data
data = []

# Loop through both support types
for col in ['ProxyUsed', 'InterpreterUsed']:
    grouped = dfs.groupby(['AgeGroup', col])['InterviewWeight'].sum().unstack(fill_value=0)
    
    # Calculate percentage of 'Yes' for each AgeGroup
    if 'Yes' in grouped.columns:
        total = grouped.sum(axis=1)
        percentage_yes = (grouped['Yes'] / total) * 100

        for age_group, value in percentage_yes.items():
            data.append({
                'AgeGroup': age_group,
                'SupportType': 'Proxy' if col == 'ProxyUsed' else 'Interpreter',
                'Percentage': value
            })

# Convert to DataFrame and source
df_heat = pd.DataFrame(data)
source = ColumnDataSource(df_heat)

# Color mapping
mapper = LinearColorMapper(palette=OrRd[5], low=0, high=100)

# Create figure
p = figure(x_range=['Proxy', 'Interpreter'],
           y_range=['Below 80', '80 or above'],
           title="Accessibility Support Need by Age Group (Weighted %)",
           tools="", toolbar_location=None,
           width=600, height=350)

# Draw heatmap
p.rect(x="SupportType", y="AgeGroup", width=1, height=1,
       source=source,
       fill_color=transform('Percentage', mapper),
       line_color=None)

# Add hover
p.add_tools(HoverTool(tooltips=[
    ("Age Group", "@AgeGroup"),
    ("Support", "@SupportType"),
    ("Percentage", "@Percentage{0.0}%")
]))

# Add color bar
color_bar = ColorBar(color_mapper=mapper, location=(0, 0))
p.add_layout(color_bar, 'right')

# Show plot
show(p)

# -

# **Description:**
#
# This visualization presents a heatmap showing the weighted percentage of accessibility support usage—specifically proxy and interpreter assistance—across two age groups: Below 80 and 80 or above. The data was grouped by age and support type (ProxyUsed, InterpreterUsed), and the percentage of participants who answered "Yes" to requiring support was calculated using their InterviewWeight to represent population-level trends. The x-axis displays the type of support, while the y-axis separates the age categories. The color intensity of each tile corresponds to the percentage of participants within each group who required support, and interactive hover tooltips reveal the exact values.
#
# **Conslusion:**
#
# The heatmap reveals that proxy usage is significantly more common among participants under 80, with a substantial proportion requiring assistance during the interview. In contrast, interpreter use is very low across both age groups, with a slightly higher percentage in the below-80 category. These findings suggest that proxy support plays a more prominent role in accessibility than interpreter services when age is considered. This could indicate that younger participants may face challenges that require assistance unrelated to language, such as cognitive or situational factors. Overall, the visualization underscores the importance of designing survey processes that account for diverse support needs across all age groups.

# # Visualization 4: Interpreter Use by Country of Birth (Weighted Count)

# **Objective**
# To visualize the relationship between interpreter usage and participants’ country of birth using weighted population data. This helps identify accessibility needs based on linguistic background and origin.

# +
import pandas as pd
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category10

output_notebook()

# Group data by CountryOfBirth and InterpreterUsed
grouped = (
    dfs.groupby(['CountryofBirth', 'InterpreterUsed'])['InterviewWeight']
    .sum()
    .reset_index()
)

# Create data source
source = ColumnDataSource(grouped)

# Create scatter plot
p = figure(x_range=grouped['CountryofBirth'].unique().tolist(),
           height=450,
           width=700,
           title="Interpreter Use by Country of Birth (Weighted Count)",
           toolbar_location=None, tools="")

# Draw circles
colors = {'Yes': Category10[3][0], 'No': Category10[3][1]}
grouped['color'] = grouped['InterpreterUsed'].map(colors)
source.data['color'] = grouped['color']

p.scatter(x='CountryofBirth',
          y='InterviewWeight',
          size=15,
          source=source,
          fill_color='color',
          line_color='black',
          legend_field='InterpreterUsed')


# Add hover
hover = HoverTool(tooltips=[
    ("Country", "@CountryofBirth"),
    ("Interpreter Used", "@InterpreterUsed"),
    ("Weighted Count", "@InterviewWeight{0,0}")
])
p.add_tools(hover)

# Style axes
p.yaxis.axis_label = "Weighted Population (Interpreter Use)"
p.xaxis.axis_label = "Country of Birth"
p.yaxis.formatter = NumeralTickFormatter(format="0,0") 
p.title.text_font_size = "14pt"
p.legend.location = "top_right"
p.legend.title = "Interpreter Used"
p.xgrid.grid_line_color = None

# Show plot
show(p)

# -

# **Description:**
# This scatter plot visualizes the relationship between interpreter usage and participants’ country of birth using NHANES data. The x-axis displays the participant’s reported country of birth (US, Others, Refused, and Unknown), while the y-axis shows the total population each group represents, weighted by InterviewWeight. Each data point represents whether participants from that group used an interpreter during the interview, with color indicating interpreter usage (Yes or No). Hovering over each point reveals the exact weighted population. This format provides a clear and minimalistic way to observe trends in accessibility support based on country of origin.
#
# **Conslusion:**
# The plot highlights a significant difference in interpreter usage between participants born in the United States and those born elsewhere. Interpreter use among U.S.-born participants was extremely low, whereas participants from other countries showed a substantially higher need for interpreter support, reinforcing the role of language as a key accessibility factor for foreign-born populations. This finding emphasizes the importance of providing interpreter services in national health surveys to ensure equitable participation and accurate data collection for linguistically diverse communities.

# # Visualization 5: Distribution of Interview Weights by Gender and Age Group

# **Objective**
# To analyze how the interview weight (which reflects the estimated U.S. population each participant represents) is distributed across combinations of gender and age group. This helps assess balance and sampling design in the NHANES dataset.

# +
import plotly.express as px

# Create a combined group label
dfs['Group'] = dfs['Gender'] + ' - ' + dfs['AgeGroup']

# Filter rows with InterviewWeight present
filtered_df = dfs.dropna(subset=['Group', 'InterviewWeight'])

# Create refined box plot
fig = px.box(
    filtered_df,
    x='Group',
    y='InterviewWeight',
    title='Distribution of Interview Weights by Gender and Age Group',
    labels={'InterviewWeight': 'Interview Weight'},
    color='Group',
    color_discrete_sequence=px.colors.qualitative.Set3,
    points=False, # Hide individual points for cleaner visual
    height= 600
)

# Show plot
fig.update_layout(showlegend=False)
fig.show()

# -

# **Description:**
# This box plot visualizes the variation in InterviewWeight across different combinations of gender and age group. The x-axis groups participants into categories such as “Male - Below 80” and “Female - 80 or above,” while the y-axis represents their assigned interview weight — a metric that estimates how many individuals each respondent represents in the overall U.S. population. The plot displays the median, interquartile range (IQR), and any statistical outliers for each demographic group. Colors differentiate each category, and the layout is optimized for readability by hiding individual data points and increasing figure height.
#
# **Conclusion:**
# The distribution of interview weights reveals some variation between demographic groups. Generally, the IQR and median values are relatively consistent across categories, suggesting balanced population representation in the NHANES sample design. However, slight differences in spread or outliers may reflect specific subpopulations that were either oversampled or underrepresented in certain age or gender segments. This visualization reinforces the importance of understanding the weight variable not as a direct count, but as a reflection of national-level representation — key for drawing generalizable health conclusions from the survey data.


