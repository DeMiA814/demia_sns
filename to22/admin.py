from django.contrib import admin
from .models import Division, Postdata, Good, Item, User
from django.urls import path
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
import csv

class ExportCSV:
    def export_as_csv(self, request):
        meta = self.model._meta
        fields_name = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(meta)

        writer = csv.writer(response)
        writer.writerow(fields_name)
        for obj in self.model.objects.all():
            writer.writerow([getattr(obj, field) for field in fields_name])

        return response


@admin.register(User)
class AdminUserAdmin(UserAdmin, ExportCSV):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name','last_name', 'email', 'icon')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def get_urls(self):
        urls = super(AdminUserAdmin, self).get_urls()
        export_url = [
            path('export/', self.admin_site.admin_view(self.export_as_csv), name='%s_%s_export' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return export_url + urls


# Register your models here.
# admin.site.register(Division)
# admin.site.register(Postdata)
# admin.site.register(Good)
# admin.site.register(Item)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin, ExportCSV):
    def get_urls(self):
        urls = super(DivisionAdmin, self).get_urls()
        export_url = [
            path('export/', self.admin_site.admin_view(self.export_as_csv), name='%s_%s_export' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return export_url + urls


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin, ExportCSV):
    
    def get_urls(self):
        urls = super(ItemAdmin, self).get_urls()
        export_url = [
            path('export/', self.admin_site.admin_view(self.export_as_csv), name='%s_%s_export' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return export_url + urls


@admin.register(Postdata)
class PostdataAdmin(admin.ModelAdmin, ExportCSV):
    def get_urls(self):
        urls = super(PostdataAdmin, self).get_urls()
        export_url = [
            path('export/', self.admin_site.admin_view(self.export_as_csv), name='%s_%s_export' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return export_url + urls


@admin.register(Good)
class GoodAdmin(admin.ModelAdmin, ExportCSV):
    def get_urls(self):
        urls = super(GoodAdmin, self).get_urls()
        export_url = [
            path('export/', self.admin_site.admin_view(self.export_as_csv), name='%s_%s_export' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        return export_url + urls
