import streamlit as st
import requests

st.title("📦 Kaggle Competition Activity Downloader")

username = st.text_input("Enter Kaggle Username (e.g., vedapr471):")

if st.button("Download Activity JSON"):
    if username.strip() == "":
        st.warning("Please enter a valid Kaggle username.")
    else:
        with st.spinner("Fetching data from API..."):
            try:
                # Call the FastAPI endpoint
                api_url = f"http://localhost:8000/download-activity/{username}"
                response = requests.get(api_url)

                if response.status_code == 200:
                    st.success("Data successfully retrieved!")

                    # Save the downloaded content to a file
                    filename = f"{username}_activity.json"
                    with open(filename, "wb") as f:
                        f.write(response.content)

                    # Display download button
                    st.download_button(
                        label="📥 Download JSON File",
                        data=response.content,
                        file_name=filename,
                        mime="application/json"
                    )
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"Failed to connect to the API: {e}")
