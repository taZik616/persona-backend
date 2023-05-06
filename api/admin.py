from django.contrib import admin

from api.models import Brand, HelpfulInfo, AnotherImage, User, Category, MainContent

admin.site.register(User)
admin.site.register(Brand)
admin.site.register(HelpfulInfo)
admin.site.register(AnotherImage)
admin.site.register(Category)
admin.site.register(MainContent)
