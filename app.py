import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
from PIL import Image, ImageOps, ImageDraw
import helper
import preprocessor

st.set_page_config(layout="wide", page_title="Olympics Analysis")

def load_zip_csv(zip_path, csv_name):
    with zipfile.ZipFile(zip_path) as z:
        with z.open(csv_name) as f:
            return pd.read_csv(f)

def add_rounded_gradient_border(img_path):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    r = 40

    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w, h)], radius=r, fill=255)
    img.putalpha(mask)

    b = 12
    gradient = Image.new("RGBA", (w + 2*b, h + 2*b))
    draw = ImageDraw.Draw(gradient)

    for i in range(b):
        alpha = int(255 * (i / b))
        color = (255, 215, 0, alpha)
        draw.rounded_rectangle(
            [(i, i), (w + 2*b - i, h + 2*b - i)],
            radius=r + i,
            outline=color,
            width=1,
        )

    gradient.paste(img, (b, b), img)
    return gradient

st.sidebar.title("Olympics Analysis")

try:
    processed_img = add_rounded_gradient_border("olympics.png")
    st.sidebar.markdown('<a href="https://olympics.com" target="_blank">', unsafe_allow_html=True)
    st.sidebar.image(processed_img, use_column_width=True)
    st.sidebar.markdown('</a>', unsafe_allow_html=True)
    st.sidebar.markdown("<h4 style='text-align:center;'>Official Olympics</h4>", unsafe_allow_html=True)
except:
    st.sidebar.write("Image could not be loaded.")

df = load_zip_csv("athlete_events.csv.zip", "athlete_events.csv")
region_df = load_zip_csv("noc_regions.csv.zip", "noc_regions.csv")
df = preprocessor.preprocess(df, region_df)

user_menu = st.sidebar.radio(
    "Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete-wise Analysis")
)

if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years, countries = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)
    medal_df = helper.fetch_medal_tally(df, selected_year, selected_country)
    st.table(medal_df)

elif user_menu == "Overall Analysis":
    st.title("Overall Olympics Analysis")

    editions = df['Year'].nunique()
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.write(
        f"Editions: {editions} | Cities: {cities} | Sports: {sports} | "
        f"Events: {events} | Athletes: {athletes} | Nations: {nations}"
    )

    st.subheader("Participating Nations Over the Years")
    nations_over_time = helper.data_over_time(df, "region")
    fig, ax = plt.subplots()
    ax.plot(nations_over_time["Edition"], nations_over_time["region"])
    st.pyplot(fig)

    st.subheader("Events Over the Years")
    events_over_time = helper.data_over_time(df, "Event")
    fig, ax = plt.subplots()
    ax.plot(events_over_time["Edition"], events_over_time["Event"])
    st.pyplot(fig)

    st.subheader("Athletes Over the Years")
    athletes_over_time = helper.data_over_time(df, "Name")
    fig, ax = plt.subplots()
    ax.plot(athletes_over_time["Edition"], athletes_over_time["Name"])
    st.pyplot(fig)

    st.subheader("Most Successful Athletes")
    sport_list = sorted(df['Sport'].unique())
    sport_list.insert(0, "Overall")
    sport = st.selectbox("Select a Sport", sport_list)
    st.table(helper.most_successful(df, sport))

elif user_menu == "Country-wise Analysis":
    countries = sorted(df['region'].dropna().unique())
    selected_country = st.sidebar.selectbox("Select Country", countries)

    st.title(f"{selected_country} - Country Analysis")

    st.subheader("Medal Tally Over the Years")
    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig, ax = plt.subplots()
    ax.plot(country_df['Year'], country_df['Medal'])
    st.pyplot(fig)

    st.subheader("Country Performance Heatmap")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.heatmap(pt, annot=True)
    st.pyplot(fig)

    st.subheader("Top Athletes")
    st.table(helper.most_successful_countrywise(df, selected_country))

elif user_menu == "Athlete-wise Analysis":
    st.title("Athlete-wise Analysis")

    st.subheader("Height vs Weight")
    sport_list = sorted(df['Sport'].unique())
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(data=temp_df, x="Weight", y="Height", hue="Medal", style="Sex", ax=ax)
    st.pyplot(fig)

    st.subheader("Men vs Women Over the Years")
    final_df = helper.men_vs_women(df)
    fig, ax = plt.subplots()
    ax.plot(final_df["Year"], final_df["Male"], label="Male")
    ax.plot(final_df["Year"], final_df["Female"], label="Female")
    ax.legend()
    st.pyplot(fig)

    st.subheader("Distribution of Age w.r.t Sports (Gold Medalists)")
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
                ax=ax,
            )
        ax.set_xlabel("Age")
        ax.set_ylabel("Density")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        st.pyplot(fig)
