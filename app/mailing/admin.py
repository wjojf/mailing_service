from django.contrib.contenttypes.admin import GenericStackedInline
from django.contrib import admin
import mailing.models as models
# Register your models here.

admin.site.register(models.Tag)
admin.site.register(models.ItemTag)
admin.site.register(models.Operator)

admin.site.register(models.Message)
admin.site.register(models.ClientFilter)


class ItemTagInline(GenericStackedInline):
    model = models.ItemTag
    classes = ["extrapretty", ]
    extra = 1


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    model = models.Client
    inlines = [ItemTagInline, ]


class MessageInline(admin.TabularInline):
    model = models.Message
    classes = ["wide", ]
    exclude = ("sent_time", )
    readonly_fields = ("status", )
    extra = 1


@admin.register(models.Mailing)
class MailingAdmin(admin.ModelAdmin):
    model = models.Mailing
    inlines = [ItemTagInline, MessageInline]
    fieldsets = (
        ("General Info", {
            'classes': ["wide", ],
            "fields": ["text", "client_filter", "start_time", "end_time"]
        }),

    )
