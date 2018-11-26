from django.db import models

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=30, primary_key=True, unique = True)
    occupied = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class Record(models.Model):
    date_start = models.DateTimeField('Room occupied at:')
    date_end = models.DateTimeField('Room freed at:')
    room_record = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    def __str__(self):
        return "Record " + str(self.id) + " for " + self.room_record.name