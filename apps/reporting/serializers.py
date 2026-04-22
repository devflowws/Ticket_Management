# apps/reporting/serializers.py
from rest_framework import serializers


class MonthlyReportSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    total_purchases_tickets = serializers.IntegerField()
    total_purchases_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_consumptions_tickets = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    active_providers = serializers.IntegerField()
    total_company_cost = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProviderReportSerializer(serializers.Serializer):
    provider_id = serializers.IntegerField()
    provider_name = serializers.CharField()
    total_tickets_used = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    company_part = serializers.DecimalField(max_digits=12, decimal_places=2)


class EmployeeReportSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    tickets_purchased = serializers.IntegerField()
    tickets_used = serializers.IntegerField()
    remaining_tickets = serializers.IntegerField()