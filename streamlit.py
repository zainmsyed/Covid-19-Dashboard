import requests
import streamlit as st  
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json

#### IMPORT AND SAVE DATA ####
us_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
us_death = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
us_vax = 'https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/us_data/time_series/people_vaccinated_us_timeline.csv'


df_us_confirmed = pd.read_csv(us_confirmed)
df_us_death = pd.read_csv(us_death)
df_us_vax = pd.read_csv(us_vax)


df_us_confirmed.to_csv('confirmed_US_covid')
df_us_death.to_csv('death_US_covid')
df_us_vax.to_csv('vax_US_covid')

df_us_confirmed = pd.read_csv('confirmed_US_covid')
df_us_deaths = pd.read_csv('death_US_covid')
df_us_vax = pd.read_csv('vax_US_covid')

#### CLEAN DATA ####
df_confirmed_dropped = df_us_confirmed.drop(columns=(['FIPS', 'UID', 'iso2', 'iso3', 'code3', 'Country_Region', 'Lat', 'Long_', 'Combined_Key', 'Unnamed: 0']))
df_death_dropped = df_us_deaths.drop(columns=(['Population', 'FIPS', 'UID', 'iso2', 'iso3', 'code3', 'Country_Region', 'Lat', 'Long_', 'Combined_Key', 'Unnamed: 0']))
df_vax_dropped = df_us_vax.drop(columns=(['Unnamed: 0', 'FIPS', 'Country_Region', 'Lat', 'Long_', 'Combined_Key']))

df_confirmed_stategroup = df_confirmed_dropped.groupby('Province_State').sum()
df_death_stategroup = df_death_dropped.groupby('Province_State').sum()
df_vax_stategroup = df_vax_dropped.groupby('Date').sum()
df_vax_statepop = df_vax_dropped.groupby(['Province_State', 'Date']).sum()


## STATE POPULATION 
df_state_population = df_us_death.groupby('Province_State').sum()
df_state_population = df_state_population['Population']


#### WEBSCRAPPING COUNTRY POPULATION ####
wikipoptable = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'

df_pop = pd.read_html(wikipoptable, flavor='html5lib')[0]
df_pop.to_csv('world_population_wiki_table')
df_pop = pd.read_csv('world_population_wiki_table')
df_pop = df_pop[['Country / Dependency', 'Population']]
df_pop_country_index = df_pop.set_index('Country / Dependency')




#### WEBAPP ####
st.set_page_config(layout='wide')


#### US Population and Statistics ####
uspop = df_pop_country_index.loc['United States']['Population']
last_row = df_vax_stategroup.iloc[-1]
vacpercentage = last_row.div(uspop)
vaxxed = (vacpercentage.round(2).loc['People_Fully_Vaccinated']*100)
partialvaxxed = (vacpercentage.round(2).loc['People_Partially_Vaccinated']*100)


## TITLE 
st.title('Covid-19 Dashboard by Zain Syed')
st.markdown('''
###### Covid-19 data is obtained from Johns Hopkins Center for Systems Science and Engineering (CSSE) [github page](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/README.md#daily-reports-csse_covid_19_daily_reports) and population data for countries is obtained from [Wikipedia](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population) 
###### This dashboard was created using [pandas](https://pandas.pydata.org/), [plotly](https://plotly.com/), and [streamlit](https://streamlit.io/)
###### This dashboard updates daily
---
###### [github](https://github.com/zainmsyed) [linkedin](https://www.linkedin.com/in/zainmsyed/)
---
''')


st.header('United States Vacination Statistics')

hcol1, hcol2, hcol3, hcol4 = st.columns(4)

with hcol2:
    st.metric('Vaccinated', f'{vaxxed} %')
with hcol3:
    st.metric('Partially Vaccinated', f'{partialvaxxed} %')
st.markdown('''---''')

st.header('Number of Confirmed Cases and Deaths per State(s)')


# st.dataframe(df_death_stategroup)
# st.dataframe(df_confirmed_stategroup[df_confirmed_stategroup.columns[0]])
state_selection = st.multiselect(
    label='Select State(s)', 
    options=df_confirmed_dropped['Province_State'].unique(), 
    default='Wisconsin'
)


## STATES GRAPH: CONFIRMED
fig_state_confimed = px.line(df_confirmed_stategroup.T[state_selection], 
title='Total Number of Confirmed Cases Per State')
fig_state_confimed.update_xaxes(title_text='Date')
fig_state_confimed.update_yaxes(title_text='# Of People (million)')
#st.plotly_chart(fig_state_confimed, use_container_width=True)

## STATES GRAPH: DEATHS
fig_state_death = px.line(df_death_stategroup.T[state_selection],
title='Total Number of Confirmed Deaths Per State')
fig_state_death.update_xaxes(title_text='Date')
fig_state_death.update_yaxes(title_text='# Of People (thousand)')
#st.plotly_chart(fig_state_death, use_container_width=True)




#### ROW 1 LAYOUT ####

r1col1, r1col2 = st.columns(2)

with r1col1:
    st.plotly_chart(fig_state_confimed, use_container_width=True)

with r1col2:
    st.plotly_chart(fig_state_death, use_container_width=True)


#st.dataframe(df_confirmed_stategroup)



## PICK COUNTY
st.header('Number of Confirmed Cases and Death per County/Counties in State')


state_county = st.selectbox(
    label='Select State',
    options=df_confirmed_dropped['Province_State'].unique()
)

state_county_list = [state_county]
county_filter_name = df_confirmed_dropped[df_confirmed_dropped['Province_State'].isin(state_county_list)]

county_selection = st.multiselect(
    label='Select County/Counties',
    options=county_filter_name['Admin2']
)

county_cases_confirmed = df_confirmed_dropped[df_confirmed_dropped['Province_State'] == state_county]
index_county_cases = county_cases_confirmed.set_index('Admin2')
trans_index_county_cases = index_county_cases.T.drop('Province_State')

county_cases_death = df_death_dropped[df_death_dropped['Province_State'] == state_county]
index_county_death = county_cases_death.set_index('Admin2')
trans_index_county_death = index_county_death.T.drop('Province_State')

## COUNTY GRAPH: CONFIRMED
fig_county_confimed = px.line(trans_index_county_cases[county_selection],
title='Total Number of Confirmed Cases Per County')
fig_county_confimed.update_xaxes(title_text='Date')
fig_county_confimed.update_yaxes(title_text='# Of People')
#st.plotly_chart(fig_county_confimed, use_container_width=True)

## COUNTY GRAPH: DEATHS
fig_county_death = px.line(trans_index_county_death[county_selection],
title='Total Number of Confirmed Deaths Per County')
fig_county_death.update_xaxes(title_text='Date')
fig_county_death.update_yaxes(title_text='# Of People')
#st.plotly_chart(fig_county_death, use_container_width=True)

picked_state_vax = df_vax_statepop.loc[state_county]
picked_state_vax = picked_state_vax.iloc[-1]
picked_state_pop = df_state_population.loc[state_county]
percent_vaxstatus = picked_state_vax.div(picked_state_pop)

picked_stat_vaxxed = (percent_vaxstatus.round(2).loc['People_Fully_Vaccinated']*100)
picked_state_partialvaxxed = (percent_vaxstatus.round(2).loc['People_Partially_Vaccinated']*100)


#### ROW 2/3 LAYOUT ####
r2col1, r2col2, r2col3, r2col4 = st.columns(4)
r3col1, r3col2 = st.columns(2)

with r2col2:
    st.metric('Vaccinated in State', f'{picked_stat_vaxxed} %')

with r2col3:
    st.metric('Partially Vaccinated in State', f'{picked_state_partialvaxxed} %')

with r3col1:
    st.plotly_chart(fig_county_confimed, use_container_width=True)

with r3col2:
    st.plotly_chart(fig_county_death, use_container_width=True)`
