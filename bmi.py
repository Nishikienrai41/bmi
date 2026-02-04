import streamlit as st


# titel
st.title("mijn eerste streamlit app")
# tekst
st.write("Welkom. Bereken hier het kwadraat van een getal.")
#slider
x = st.slider("kies een getal", 0, 100)
#output
st.write(f"Het kwaadraat van {x} is {x**2}")