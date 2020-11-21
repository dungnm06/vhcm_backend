from rest_framework import serializers
import vhcm.models.knowledge_data_review as review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = review.Review
        fields = [review.ID, review.USER, review.REVIEW_DETAIL,
                  review.STATUS, review.MDATE]
