from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Pdf, ChatMessage, Subscription, Session


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'credits', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('credits',)}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Pdf)
admin.site.register(ChatMessage)
admin.site.register(Subscription)
admin.site.register(Session)
