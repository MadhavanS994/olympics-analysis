import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import preprocessor
import helper

st.set_page_config(layout="wide")

st.title("Olympics Analysis Dashboard")

#read data
df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")

df = preprocessor.preprocess(df, region_df)

st.sidebar.title("Olympics Analysis")

user_menu = st.sidebar.radio(
    "Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis",
     "Athlete-wise Analysis")
)

#medal
if user_menu == "Medal Tally":

    st.sidebar.header("Medal Tally")

    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Medal Tally")
    elif selected_year == "Overall":
        st.title(f"Medal Tally for {selected_country}")
    elif selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year}")
    else:
        st.title(f"{selected_country} Medal Tally in {selected_year}")

    st.table(medal_tally)

#overall analysis
if user_menu == "Overall Analysis":

    st.title("Overall Olympics Analysis")

    editions = df['Year'].nunique()
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.header("Top Statistics")

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("Editions", editions)
    col2.metric("Host Cities", cities)
    col3.metric("Sports", sports)
    col4.metric("Events", events)
    col5.metric("Athletes", athletes)
    col6.metric("Nations", nations)

    # Nations over time
    st.title("Participating Nations Over the Years")
    nations_over_time = helper.data_over_time(df, "region")

    fig, ax = plt.subplots()
    ax.plot(nations_over_time["Edition"], nations_over_time["region"])
    ax.set_xlabel("Year")
    ax.set_ylabel("No. of Countries")
    st.pyplot(fig)

    # Events over time
    st.title("Events Over the Years")
    events_over_time = helper.data_over_time(df, "Event")

    fig, ax = plt.subplots()
    ax.plot(events_over_time["Edition"], events_over_time["Event"])
    st.pyplot(fig)

    # Athletes over time
    st.title("Athletes Over the Years")
    athletes_over_time = helper.data_over_time(df, "Name")

    fig, ax = plt.subplots()
    ax.plot(athletes_over_time["Edition"], athletes_over_time["Name"])
    st.pyplot(fig)

    # Most Successful Athletes
    st.title("Most Successful Athletes")
    sport_list = sorted(df['Sport'].unique().tolist())
    sport_list.insert(0, "Overall")

    sport = st.selectbox("Select a Sport", sport_list)
    successful_athletes = helper.most_successful(df, sport)

    st.table(successful_athletes)

#country wise analysis
if user_menu == "Country-wise Analysis":

    st.sidebar.header("Country Analysis")
    country_list = sorted(df['region'].dropna().unique())
    selected_country = st.sidebar.selectbox("Select Country", country_list)

    st.title(f"{selected_country} - Country Analysis")

    # Medal tally over years
    st.header("Medal Tally Over the Years")
    country_df = helper.yearwise_medal_tally(df, selected_country)

    fig, ax = plt.subplots()
    ax.plot(country_df['Year'], country_df['Medal'])
    st.pyplot(fig)

    # Heatmap of events
    st.header("Country Performance Heatmap")
    pt = helper.country_event_heatmap(df, selected_country)

    fig, ax = plt.subplots(figsize=(20, 10))
    sns.heatmap(pt, annot=True)
    st.pyplot(fig)

    # Top athletes
    st.header("Top Athletes from This Country")
    top_athletes = helper.most_successful_countrywise(df, selected_country)
    st.table(top_athletes)

#athlete wise analysis
if user_menu == "Athlete-wise Analysis":

    st.title("Athlete-wise Analysis")

    st.header("Height vs Weight Analysis")

    sport_list = sorted(df['Sport'].unique())
    sport_list.insert(0, "Overall")

    selected_sport = st.selectbox("Select a Sport", sport_list)

    temp_df = helper.weight_v_height(df, selected_sport)

    fig, ax = plt.subplots()
    sns.scatterplot(data=temp_df, x="Weight", y="Height", hue="Medal", style="Sex", ax=ax)
    st.pyplot(fig)

    # Men vs Women participation
    st.header("Men vs Women Participation Over the Years")

    final_df = helper.men_vs_women(df)

    fig, ax = plt.subplots()
    ax.plot(final_df["Year"], final_df["Male"], label="Male")
    ax.plot(final_df["Year"], final_df["Female"], label="Female")
    ax.legend()
    st.pyplot(fig)

    st.header("Distribution of Age w.r.t Sports (Gold Medalists)")

    age_df = helper.age_distribution_gold(df)

    sports = sorted(age_df['Sport'].unique())
    selected_sports = st.multiselect("Select Sports", sports, default=sports[:8])

    if selected_sports:
        fig, ax = plt.subplots(figsize=(12, 6))

        for sport in selected_sports:
            sns.kdeplot(
                age_df[age_df['Sport'] == sport]['Age'],
                label=sport,
                fill=False,
                linewidth=2,
                ax=ax
            )

        ax.set_xlabel("Age")
        ax.set_ylabel("Density")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        st.pyplot(fig)
