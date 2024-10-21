# imperial-college-hackathon

This is the repo of the work done on the Imperial College Hackathon.

The key technologies used are:

* NextJs & React (mostly via V0 prompting) - an AI website builder 

* Streamlit - a Python library for creating web apps, used for the interactive orderbook

* Supabase - a Postgres-like database service, used to store the orderbook data

* Fly.io - a cloud hosting service, used to host the website & streamlit app


# zktrade
The code for the website.

You can run it locally by running `npm run dev` in the `zktrade` folder.

You can create a new deployment via

`fly launch`

or update it by running

`fly deploy`

# zero-viz-brokers
The streamlit app for the interactive orderbook.

> Start it by running `streamlit run app.py` in the `zero-viz-brokers` folder after installing the dependencies in requirements.txt (using pip or uv).

You can create a new deployment via

`fly launch`

or update it by running

`fly deploy`

---

I've removed the data in the zero-viz-brokers/.streamlit/secrets.toml as it contains the credentials for the Supabase database. You can find the credentials in the supabase dashboard.

