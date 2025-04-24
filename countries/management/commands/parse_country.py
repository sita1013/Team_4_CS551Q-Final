import pandas as pd
from django.core.management.base import BaseCommand
from countries.models import Country, PM25Record, CountryMetadata

class Command(BaseCommand):
    """this is where I parse the file completely...the issue I found when deploying was that I couldn't load 
    metadata for income levels in Render. I included the code I found to load it at the bottom but commented 
    out since it wasn't necessary for the site to run just from here"""
    help = "Load PM2.5 data from Excel file into the database"

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        filepath = kwargs['filepath']
        self.stdout.write(f"Reading file: {filepath}")
        #had to go back and forth with ChatGPT for this one so I'm just writing notes for myself here
        df = pd.read_excel(filepath, sheet_name='Data', skiprows=3, engine='openpyxl') #reads excel into a "data frame" literally coding df
        df.dropna(axis=1, how='all', inplace=True) #gets rid of empty columns, this is to make it easier to add any missing data later
        df.dropna(subset=["Country Name"], inplace=True) #again drops empty rows where there isn't anything for Country Name, so can add data later if needed
        df_melted = df.melt( #data was in a wide format so this changes it to a long format
            id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
            var_name="Year",
            value_name="PM25_Level"
        )
        df_melted["Year"] = pd.to_numeric(df_melted["Year"], errors="coerce")
        df_melted.dropna(subset=["Year"], inplace=True)
        df_melted["Year"] = df_melted["Year"].astype(int)
        #this is where it gets loaded into the database
        for i, row in df_melted.iterrows():
            country, i = Country.objects.get_or_create(
                code=row["Country Code"],
                defaults={"name": row["Country Name"]}
            )
            PM25Record.objects.update_or_create(
                country=country,
                year=row["Year"],
                defaults={"value": row["PM25_Level"]}
            )
        self.stdout.write(self.style.SUCCESS("PM2.5 data loaded successfully."))
 
#when deploying this, had to add in a ton of stuff to get the metadata to be 
#picked up by Render... entire python code commented out below with # comments added...admittedly it was a lot
#of ChatGPT for help with this one as I had no idea what was going on but made notes for myself below
"""
import pandas as pd
from django.core.management.base import BaseCommand
from countries.models import Country, PM25Record, CountryMetadata

class Command(BaseCommand):
    help = "Load PM2.5 data and metadata from Excel file into the database"
    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Path to the Excel file')
    def handle(self, *args, **kwargs):
        filepath = kwargs['filepath']
        self.stdout.write(f"Reading file: {filepath}")

    #Loading the PM2.5 data
        df = pd.read_excel(filepath, sheet_name='Data', skiprows=3, engine='openpyxl')
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(subset=["Country Name"], inplace=True)

        self.stdout.write("Available Indicator Names:\n" + "\n".join(df["Indicator Name"].dropna().unique()))
        # Filtering via indicator
        df = df[df["Indicator Name"] == "PM2.5 air pollution, population exposed to levels exceeding WHO guideline value (% of total)"]

    # Reshaping the data
        df_melted = df.melt(
            id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
            var_name="Year",
            value_name="PM25_Level"
        )
        df_melted["Year"] = pd.to_numeric(df_melted["Year"], errors="coerce")
        df_melted.dropna(subset=["Year", "PM25_Level"], inplace=True)
        df_melted["Year"] = df_melted["Year"].astype(int)
        self.stdout.write(f"PM2.5 records to import: {len(df_melted)}")
        for _, row in df_melted.iterrows():
            country, _ = Country.objects.get_or_create(
                code=row["Country Code"],
                defaults={"name": row["Country Name"]}
            )
            PM25Record.objects.update_or_create(
                country=country,
                year=row["Year"],
                defaults={"value": row["PM25_Level"]}
            )
        self.stdout.write(self.style.SUCCESS("PM2.5 data loaded successfully."))

    # Load metadata -- finger's crossed
        self.stdout.write("Loading country metadata.")
        xls = pd.ExcelFile(filepath, engine='openpyxl')
        self.stdout.write(f"Available sheets: {xls.sheet_names}")
        meta_df = xls.parse(sheet_name='Metadata - Countries')
        meta_df.dropna(subset=["Country Code", "IncomeGroup"], inplace=True)

        for _, row in meta_df.iterrows():
            CountryMetadata.objects.update_or_create(
                code=row["Country Code"],
                defaults={"income_level": row["IncomeGroup"]}
            )
        self.stdout.write(self.style.SUCCESS("Country metadata loaded successfully."))
"""

