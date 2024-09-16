from django.contrib import admin
from bot.models import User, MandatoryUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'name', 'username')
    search_fields = ('id', 'telegram_id', 'name', 'username')
    list_filter = ('id', 'name', 'username')


@admin.register(MandatoryUser)
class MandatoryUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')
    search_fields = ('name', 'url')
    list_filter = ('name', 'url')
