from django.db import models
import architect

# Create your models here.
class Board(models.Model):
    pass

    def __str__(self):
        return str(self.pk)

@architect.install('partition', type='range', subtype='integer', constraint='2', column='board_id')
class Article(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
