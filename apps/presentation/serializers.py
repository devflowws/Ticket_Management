from rest_framework import serializers


class HeroSerializer(serializers.Serializer):
    badge = serializers.CharField()
    title = serializers.CharField()
    subtitle = serializers.CharField()
    cta_primary = serializers.CharField()
    cta_secondary = serializers.CharField()
    stats = serializers.ListField(child=serializers.DictField(), allow_empty=True)


class FeatureSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class StepSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()


class RoleSerializer(serializers.Serializer):
    key = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class FaqItemSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()


class CtaSerializer(serializers.Serializer):
    title = serializers.CharField()
    subtitle = serializers.CharField()
    cta_primary = serializers.CharField()
    cta_secondary = serializers.CharField()


class LandingPageSerializer(serializers.Serializer):
    hero = HeroSerializer()
    features = FeatureSerializer(many=True)
    steps = StepSerializer(many=True)
    roles = RoleSerializer(many=True)
    faq = FaqItemSerializer(many=True)
    cta = CtaSerializer()
