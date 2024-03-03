from .models import Category
from adminapp.models import SiteInfo

def category_links(request):
    links = Category.objects.all()
    return dict(links = links)

def site_info(request):
    site_info = SiteInfo.objects.all()
    return dict(siteinfo = site_info)