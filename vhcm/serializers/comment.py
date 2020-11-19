from rest_framework import serializers
import vhcm.models.knowledge_data_comment as comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = comment.Comment
        fields = [comment.ID, comment.USER, comment.REPLY_TO,
                  comment.COMMENT, comment.VIEWABLE_STATUS, comment.EDITED, comment.MDATE]


class DeletedCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = comment.Comment
        fields = [comment.ID, comment.USER, comment.REPLY_TO,
                  comment.VIEWABLE_STATUS, comment.EDITED, comment.MDATE]
