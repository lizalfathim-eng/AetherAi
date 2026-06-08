from django.db import models
from django.contrib.auth.models import User
# Create your models here.




class Staff(models.Model):
    name=models.CharField(max_length=150)
    gender=models.CharField(max_length=50)
    dob=models.DateField()
    email=models.CharField(max_length=50)
    phone=models.CharField(max_length=50)
    photo=models.CharField(max_length=250)
    qualification=models.CharField(max_length=250)
    place=models.CharField(max_length=50)
    district=models.CharField(max_length=50)
    pin=models.CharField(max_length=20)

    join_date = models.DateField(default="2026-01-14")
    experience = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    salary = models.FloatField()
    status = models.CharField(max_length=20, default="Active")

    USER=models.OneToOneField(User,on_delete=models.CASCADE)

class Upload(models.Model):
    STAFF = models.ForeignKey(Staff, on_delete=models.CASCADE)
    Date=models.DateField()
    document=models.CharField(max_length=400)
    title=models.CharField(max_length=500,default='')
    hashvalue=models.CharField(max_length=1000,default="")


class Complaint(models.Model):
    date=models.DateField()
    complaint=models.CharField(max_length=1000)
    reply=models.CharField(max_length=1000)
    status=models.CharField(max_length=100)
    STAFF=models.ForeignKey(Staff,on_delete=models.CASCADE)


