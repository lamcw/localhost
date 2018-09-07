from django.contrib import admin
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicParentModelAdmin)

from localhost.report.models import PropertyReport, Report, UserReport


class ReportChildAdmin(PolymorphicChildModelAdmin):
    base_model = Report
    exclude = ('time', )


@admin.register(UserReport)
class UserReportAdmin(ReportChildAdmin):
    base_model = UserReport


@admin.register(PropertyReport)
class PropertyReportAdmin(ReportChildAdmin):
    base_model = PropertyReport


@admin.register(Report)
class ReportParentAdmin(PolymorphicParentModelAdmin):
    base_model = Report
    child_models = (UserReport, PropertyReport)
