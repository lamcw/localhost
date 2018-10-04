from django.contrib import admin
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicParentModelAdmin)

from localhost.report.models import PropertyItemReport, Report, UserReport


class ReportChildAdmin(PolymorphicChildModelAdmin):
    base_model = Report
    exclude = ('time', )


@admin.register(UserReport)
class UserReportAdmin(ReportChildAdmin):
    base_model = UserReport


@admin.register(PropertyItemReport)
class PropertyItemReportAdmin(ReportChildAdmin):
    base_model = PropertyItemReport


@admin.register(Report)
class ReportParentAdmin(PolymorphicParentModelAdmin):
    base_model = Report
    child_models = (UserReport, PropertyItemReport)
