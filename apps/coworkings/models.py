from django.db import models


class City(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"


class Coworking(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        db_table = 'coworking'

    def __str__(self):
        return f"{self.name}"


class Place(models.Model):
    TYPE_OF_PLACE = (
        ("desk", "Рабочее место"),
        ("meeting", "Переговорная"),
    )

    coworking = models.ForeignKey(Coworking, on_delete=models.CASCADE, related_name='places')
    type = models.CharField(max_length=50, choices=TYPE_OF_PLACE)
    place_number = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=1)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        db_table = 'place'
        unique_together = ("coworking", "type", "place_number")

    def __str__(self):
        return f"{self.type} - {self.place_number}"


class Slot(models.Model):
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, related_name='slots')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        db_table = 'slot'

    def __str__(self):
        return f"{self.place.coworking.name} | {self.place} | {self.start_datetime} - {self.end_datetime}"


