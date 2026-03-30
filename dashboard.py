import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Housing Affordability Dashboard", layout="wide")

st.title("Global Housing Affordability Dashboard")
st.markdown("Explore rent burden and housing purchase affordability across cities.")



# Load data
df = pd.read_csv("data/cost-of-living_cleaned.csv")


# Sidebar filters
st.sidebar.header("Filters")

country_options_1 = ["All"] + sorted(df["country"].dropna().unique().tolist())
selected_country_1 = st.sidebar.selectbox("Country 1", country_options_1)

country_options_2 = ["None"] + sorted(df["country"].dropna().unique().tolist())
selected_country_2 = st.sidebar.selectbox("Country 2", country_options_2)

# color map
if selected_country_2 == "None":
    color_map = {selected_country_1: "#4C9AFF"}
else:
    color_map = {
        selected_country_1: "#4C9AFF",
        selected_country_2: "#FF6B9A"
    }

filtered_df = df.copy()
if selected_country_1 != "All":
    if selected_country_2 == "None":
        filtered_df = filtered_df[filtered_df["country"] == selected_country_1]
    else:
        selected_countries = list({selected_country_1, selected_country_2})
        filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]

# Top metrics
col1, col2 = st.columns(2)
avg_rent_pct = filtered_df["Avg_Pct_Spent_Rent"].mean()
avg_months_m2 = filtered_df["Months_to_Afford_1sqm"].mean()
if selected_country_2 == "None":    
    if selected_country_1 == "All":
        col1.metric(f"Global Average Rent Burden:", f"{avg_rent_pct*100:.1f}%")
        col2.metric("Average Months of Salary per 1 m²", f"{avg_months_m2:.1f}")
    else:
        col1.metric(f"{selected_country_1} Average Rent Burden:", f"{avg_rent_pct*100:.1f}%")
        col2.metric(f"{selected_country_1} Average Months of Salary per 1 m²", f"{avg_months_m2:.1f}")

else:
    df_country_1 = df[df["country"] == selected_country_1]
    df_country_2 = df[df["country"] == selected_country_2]

    rent_1 = df_country_1["Avg_Pct_Spent_Rent"].mean() * 100
    rent_2 = df_country_2["Avg_Pct_Spent_Rent"].mean() * 100
    m2_1 = df_country_1["Months_to_Afford_1sqm"].mean()
    m2_2 = df_country_2["Months_to_Afford_1sqm"].mean()
    with col1:
        st.markdown("**Average Rent Burden**")
        c1, c2 = st.columns(2)
        c1.metric(selected_country_1, f"{rent_1:.1f}%")
        c2.metric(selected_country_2, f"{rent_2:.1f}%")

    with col2:
        st.markdown("**Average Months of Salary per m²**")
        c3, c4 = st.columns(2)
        c3.metric(selected_country_1, f"{m2_1:.1f}")
        c4.metric(selected_country_2, f"{m2_2:.1f}")

st.divider()
# Scatter plot
st.subheader("Rent Burden vs Purchase Affordability")

fig_scatter = px.scatter(
    filtered_df,
    x="Avg_Pct_Spent_Rent",
    y="Months_to_Afford_1sqm",
    hover_name="city",
    color="country",
    color_discrete_map=color_map,
    title="Cities with higher rent burden often also have weaker purchase affordability",
    labels={
        "Avg_Pct_Spent_Rent": "% of Monthly Salary Needed for 1BR Rent",
        "Months_to_Afford_1sqm": "Months of Salary Needed for 1 m²"
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Ranking chart
st.subheader("Highest Rent Burden Cities")

top_rent = filtered_df.sort_values("Avg_Pct_Spent_Rent", ascending=False).head(15)
top_rent["Avg_Pct_Spent_Rent"] = top_rent["Avg_Pct_Spent_Rent"].map(lambda x: round(x*100, 2))

fig_bar = px.bar(
    top_rent,
    x="Avg_Pct_Spent_Rent",
    y="city",
    orientation="h",
    color = "country",
    color_discrete_map=color_map,
    title="Top 15 Cities by Rent Burden",
    labels={
        "rent_pct_salary": "% of Monthly Salary Needed",
          "city": "City",
          "Avg_Pct_Spent_Rent" : "Rent Burden (%)"}
)
fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
fig_bar.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
st.plotly_chart(fig_bar, use_container_width=True)


st.divider()


# Simple insights table
st.subheader("Most Affordable and Least Affordable Cities")

insights_df = filtered_df.copy()
insights_df = insights_df[["city", "country", "Avg_Pct_Spent_Rent", "Months_to_Afford_1sqm"]]
insights_df["Avg_Pct_Spent_Rent"] = insights_df["Avg_Pct_Spent_Rent"].map(lambda x: round(x*100, 2))
insights_df["Months_to_Afford_1sqm"] = insights_df["Months_to_Afford_1sqm"].map(lambda x: round(x, 1))
rename_dict = {
    "city" : "City",
    "country" : "Country",
    "Avg_Pct_Spent_Rent" : "Rent Burden (%)",
    "Months_to_Afford_1sqm" : "Months Per Sq. Meter"
}

left, right = st.columns(2)

with left:
    st.markdown("**Lowest rent burden**")
    st.dataframe(
        insights_df.sort_values("Avg_Pct_Spent_Rent", ascending=True)[
            ["city", "country", "Avg_Pct_Spent_Rent", "Months_to_Afford_1sqm"]
        ].head(10).rename(columns = rename_dict),
        use_container_width=True
    )

with right:
    st.markdown("**Highest rent burden**")
    st.dataframe(
        insights_df.sort_values("Avg_Pct_Spent_Rent", ascending=False)[
            ["city", "country", "Avg_Pct_Spent_Rent", "Months_to_Afford_1sqm"]
        ].head(10).rename(columns = rename_dict),
        use_container_width=True
    )

st.markdown("Rent Burden (%) = Average percentage of monthly income spent on rent for 1BR apartment outside of city center.")
st.markdown("Months Per Sq. Meter = Approximate number of months of income needed to purchase one square meter of an apartment.")