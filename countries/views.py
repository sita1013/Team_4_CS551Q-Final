import json
from django.shortcuts import render
"""from .models import PM25Record, Country""" #commented out since it's redundant 
from django.db.models import Max
"""from .models import CountryMetadata""" #commented out because it's also redundant
from countries.models import Country, PM25Record, CountryMetadata

#used json to avoid JS on html and render top countries in most recent year
#this means we can add in data if we want from 2017 - 2015 and it won't break (hopefully)
def homepage(request):
    latest_year = PM25Record.objects.aggregate(Max('year'))['year__max']
    top_records = PM25Record.objects.filter(year=latest_year).order_by('-value')[:5]
    countries = [record.country.name for record in top_records]
    values = [record.value for record in top_records]
    return render(request, 'countries/homepage.html', {
        'countries_json': json.dumps(countries),
        'values_json': json.dumps(values),
        'latest_year': latest_year,
    })

#looking at a single country with metadat displayed for income levels
def pm25_lookup_view(request):
    selected_country = request.GET.get('country')
    selected_year = request.GET.get('year')
    countries = Country.objects.order_by('name')
    years = PM25Record.objects.values_list('year', flat=True).distinct().order_by('year')
    record = None
    country = None
    income_level = None
    year_list = []
    value_list = []
    if selected_country:
        country = Country.objects.filter(code=selected_country).first()
        metadata = CountryMetadata.objects.filter(code=selected_country).first()
        income_level = metadata.income_level if metadata else "Unknown"
        yearly_records = PM25Record.objects.filter(
            country__code=selected_country
        ).order_by('year')
        year_list = [r.year for r in yearly_records]
        value_list = [r.value for r in yearly_records]
    if selected_country and selected_year:
        record = PM25Record.objects.filter(
            country__code=selected_country,
            year=selected_year
        ).first()
    context = {
        'countries': countries,
        'years': years,
        'selected_country': selected_country,
        'selected_year': selected_year,
        'record': record,
        'year_list': year_list,
        'value_list': value_list,
        'country': country,
        'income_level': income_level,
    }
    return render(request, 'countries/pm25_lookup.html', context)

#comparing two countries with barcharts and displayed data included metadata for income level
def barchart_compare(request):
    countries = Country.objects.order_by('name')
    years = PM25Record.objects.values_list('year', flat=True).distinct().order_by('year')
    selected_year = request.GET.get('year')
    country1_code = request.GET.get('country1')
    country2_code = request.GET.get('country2')
    chart_type = request.GET.get('chart_type', 'bar')  # Default to 'bar'
    record1 = record2 = None
    income1 = income2 = None
    if selected_year and country1_code and country2_code:
        record1 = PM25Record.objects.filter(country__code=country1_code, year=selected_year).first()
        record2 = PM25Record.objects.filter(country__code=country2_code, year=selected_year).first()
        try:
            income1 = CountryMetadata.objects.get(code=country1_code).income_level
        except CountryMetadata.DoesNotExist:
            income1 = "Unknown"
        try:
            income2 = CountryMetadata.objects.get(code=country2_code).income_level
        except CountryMetadata.DoesNotExist:
            income2 = "Unknown"
    return render(request, 'countries/barchart_compare.html', {
        'countries': countries,
        'years': years,
        'selected_year': selected_year,
        'country1_code': country1_code,
        'country2_code': country2_code,
        'record1': record1,
        'record2': record2,
        'income1': income1, 
        'income2': income2,
        'chart_type': chart_type,
    })


#for deployment I added in code below to help get Render to pick up on metadata
#admittedly got a lot of help from ChatGPT on this one because I didn't know what
#was happening...but below is the code I used for the metadata in Render with 
#notes added in so hopefully I can do this on my own in the future
"""
from django.http import JsonResponse
from .models import CountryMetadata #in hindsight this was redundant and didn't need to add this as already at the top

def check_metadata(request): #should fetch all the metadata records in the subfile CountryMetada
    data = list(CountryMetadata.objects.values())
    return JsonResponse(data, safe=False) #Json makes it easier for the frontend call

def load_metadata(request):
    data = [
        {"code": "KEN", "income_level": "Low"}, #sample of code to push the metadata
        {"code": "CAN", "income_level": "High"},
        {"code": "IND", "income_level": "Lower-Middle"},
    ]
    for item in data: #to loop through each country code matching the country name and metadata
        CountryMetadata.objects.update_or_create(
            code=item["code"], #specific as main data was connected to metadata only by the country code
            defaults={"income_level": item["income_level"]}
        )
# added so I know if the data had loaded in the deployment log
    return JsonResponse({"status": "Metadata loaded"})
"""