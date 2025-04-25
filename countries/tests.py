import os
import tempfile
import pandas as pd
from django.core.management import call_command
from django.test import TestCase
from countries.models import Country, PM25Record, CountryMetadata
from django.urls import reverse

class SimpleURLTests(TestCase):
    def test_homepage_url(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'countries/homepage.html')

    def test_pm25_lookup_url(self):
        response = self.client.get(reverse('pm25_lookup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'countries/pm25_lookup.html')

    def test_barchart_compare_url(self):
        response = self.client.get(reverse('barchart_compare'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'countries/barchart_compare.html')

class PM25LoadCommandTests(TestCase):
    def setUp(self):
        # Create a minimal Excel file in a temp file
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)

        df = pd.DataFrame({
            'Country Name': ['Testland'],
            'Country Code': ['TST'],
            'Indicator Name': ['PM2.5 air pollution'],
            'Indicator Code': ['EN.ATM.PM25.MC.M3'],
            '2000': [42.0],
            '2001': [43.0],
        })
        with pd.ExcelWriter(self.temp_file.name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data', startrow=3)

    def tearDown(self):
        os.remove(self.temp_file.name)

    def test_pm25_load_command_creates_records(self):
        call_command('parse_country', self.temp_file.name)
        
        self.assertTrue(Country.objects.filter(code='TST').exists())
        self.assertEqual(PM25Record.objects.filter(country__code='TST').count(), 2)
    
class CountriesAppTests(TestCase):
     def setUp(self):
         # Create test data
         self.country1 = Country.objects.create(name='China', code='CHN')
         self.country2 = Country.objects.create(name='United States', code='USA')
         
         # Create PM2.5 records
         self.pm25_2020_1 = PM25Record.objects.create(
             country=self.country1,
             year=2020,
             value=35.5
         )
         self.pm25_2020_2 = PM25Record.objects.create(
             country=self.country2,
             year=2020,
             value=25.0
         )
         
         # Create country metadata
         self.metadata1 = CountryMetadata.objects.create(
             code='CHN',
             income_level='Upper-Middle'
         )
         self.metadata2 = CountryMetadata.objects.create(
             code='USA',
             income_level='High'
         )
 
     def test_models(self):
         # Test Country model
         self.assertEqual(str(self.country1), 'China')
         self.assertEqual(str(self.country2), 'United States')
 
         # Test PM25Record model
         self.assertEqual(str(self.pm25_2020_1), 'China - 2020: 35.5')
         self.assertEqual(str(self.pm25_2020_2), 'United States - 2020: 25.0')
 
         # Test CountryMetadata model
         self.assertEqual(str(self.metadata1), 'CHN - Upper-Middle')
         self.assertEqual(str(self.metadata2), 'USA - High')
 
     def test_homepage_view(self):
         response = self.client.get(reverse('homepage'))
         self.assertEqual(response.status_code, 200)
         self.assertTemplateUsed(response, 'countries/homepage.html')
         # Check context data
         self.assertEqual(response.context['latest_year'], 2020)
 
     def test_pm25_lookup_view(self):
         # Test access without parameters
         response = self.client.get(reverse('pm25_lookup'))
         self.assertEqual(response.status_code, 200)
         self.assertTemplateUsed(response, 'countries/pm25_lookup.html')
 
         # Test access with parameters
         response = self.client.get(
             reverse('pm25_lookup'),
             {'country': 'CHN', 'year': '2020'}
         )
         self.assertEqual(response.status_code, 200)
         self.assertEqual(response.context['record'], self.pm25_2020_1)
         self.assertEqual(response.context['income_level'], 'Upper-Middle')
 
     def test_barchart_compare_view(self):
         # Test access without parameters
         response = self.client.get(reverse('barchart_compare'))
         self.assertEqual(response.status_code, 200)
         self.assertTemplateUsed(response, 'countries/barchart_compare.html')
 
         # Test access with parameters
         response = self.client.get(
             reverse('barchart_compare'),
             {
                 'country1': 'CHN',
                 'country2': 'USA',
                 'year': '2020',
                 'chart_type': 'bar'
             }
         )
         self.assertEqual(response.status_code, 200)
         self.assertEqual(response.context['record1'], self.pm25_2020_1)
         self.assertEqual(response.context['record2'], self.pm25_2020_2)
         self.assertEqual(response.context['income1'], 'Upper-Middle')
         self.assertEqual(response.context['income2'], 'High')
 
