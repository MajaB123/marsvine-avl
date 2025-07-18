from supabase import create_client
import pandas as pd

url = "https://dhffpzifxweschuiwiqr.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRoZmZwemlmeHdlc2NodWl3aXFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU0OTQ5NDksImV4cCI6MjAyMTA3MDk0OX0.cGpOxk-cn8h0bgVa3iER0nm-T4yymGBt_l5ess08iec"

supabase = create_client(url, key)

pigs = supabase.table("guinea_pigs").select("*").execute().data
races = supabase.table("races").select("*").execute().data
print("Raw pigs:", pigs)
print("Raw races:", races)


pigs_df = pd.DataFrame(pigs)
races_df = pd.DataFrame(races)

print("PIGS:\n", pigs_df.head())
print("RACES:\n", races_df.head())


