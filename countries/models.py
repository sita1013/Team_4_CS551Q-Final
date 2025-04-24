from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    def __str__(self):
        return self.name

class PM25Record(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='pm25_records')
    year = models.IntegerField()
    value = models.FloatField(null=True, blank=True)
    class Meta:
        unique_together = ('country', 'year')
        ordering = ['country', 'year']
    def __str__(self):
        return f"{self.country.name} - {self.year}: {self.value}"

#inputted new class to render metatdata for income levels
#this was also added into the views to make sure the metadata is running correctly
class CountryMetadata(models.Model):
    code = models.CharField(max_length=3, unique=True)
    income_level = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.code} - {self.income_level}"

