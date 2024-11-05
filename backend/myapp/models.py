from djongo import models

class FileAnalysis(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    file_name = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    columns = models.JSONField()
    dtypes = models.JSONField()
    data = models.JSONField()

    class Meta:
        ordering = ['-upload_time']

    def __str__(self):
        return f"{self.file_name} - {self.upload_time}"