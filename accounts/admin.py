from django.contrib import admin
from .models import Student
from django.contrib.auth.admin import UserAdmin


@admin_register(Student)
class studentAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
    ("Extra", {"fields": ("phone", "bio", "avatar", "public_id")}),
)
list_display = ('username', 'email', 'phone', 'bio', 'avatar', 'public_id', 'is_staff', 'is_active', 'date_joined')

list_filter = ('is_staff', 'is_active')
search_fields = ('username', 'email', 'phone')
ordering = ('username',)



# Register your models here.
