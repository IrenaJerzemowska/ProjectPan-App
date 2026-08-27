import pandas as pd
import streamlit as st

# Assuming 'df' is your beauty inventory dataframe containing a 'Brand' column
st.subheader("💖 Most Loved Brands")

if "Brand" in df.columns and not df.empty:
  # Count occurrences of each brand and grab the top 10
  brand_counts = df["Brand"].value_counts().reset_index()
  brand_counts.columns = ["Brand", "Count"]

  # Display interactive bar chart
  st.bar_chart(brand_counts.set_index("Brand"))

  # Quick text summary of your absolute top brand
  top_brand = brand_counts.iloc[0]["Brand"]
  top_count = brand_counts.iloc[0]["Count"]
  st.success(
      f"Your most collected brand is **{top_brand}** with **{top_count}**"
      " products!"
  )
else:
  st.info("Add some products with brand names to see your breakdown chart here.")
