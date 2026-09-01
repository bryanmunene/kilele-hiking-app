"""Compatibility entrypoint for Streamlit Cloud and older docs.

The main app lives in Home.py so Streamlit can discover the multipage sidebar.
Running `streamlit run app.py` still starts the same experience.
"""

from Home import main


if __name__ == "__main__":
    main()
