from tortoise import fields, models
from tortoise.fields.base import CASCADE


class StoryReward(models.Model):

    id = fields.IntField(pk=True)
    tag = fields.TextField(null=True)
    author = fields.CharField(max_length=100, null=True)
    title = fields.CharField(max_length=100, null=True)
    word_count = fields.IntField(null=True, index=True)
    saved_pieces_count = fields.IntField(null=True, index=True)
    source_url = fields.TextField(null=True)

    pieces: fields.ReverseRelation["StoryPieceModel"]

    def __str__(self):
        return f"<id :: {self.id} , title :: {self.title}>"
    
    class Meta:
        app = "models"
        table = "stories"



class StoryPieceModel(models.Model):
   
    id = fields.IntField(pk=True)
    content = fields.TextField(null=False)
    word_count = fields.IntField(null=False)
    piece_num = fields.IntField(null=False, index=True)


    story: fields.ForeignKeyRelation[StoryReward] = fields.ForeignKeyField(
        "models.StoryReward", related_name="pieces", on_delete=CASCADE, null=True
    ) 

    def __str__(self):
        return f"<id :: {self.id} , piece_num :: {self.piece_num}>"
    
    class Meta:
        app = "models"
        # abstract = True
        table = "story_pieces"
        unique_together = ("id", "piece_num",)
        ordering = ["story_id", "piece_num"]
