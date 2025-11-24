from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = "Панель управления заказами"
    site_title = "Админка заказов"
    index_title = "Управление данными"

admin_site = CustomAdminSite(name='custom_admin')