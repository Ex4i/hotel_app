from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^room/(?P<pk>[0-9]+)/$', views.RoomDetail.as_view()),
    url(r'^room/$', views.RoomList.as_view()),
    url(r'^room/category/(?P<pk>[0-9]+)/$', views.RoomCategoryDetail.as_view()),
    url(r'^room/category/$', views.RoomCategoryList.as_view()),
    url(r'^booking/(?P<pk>[0-9]+)/duration/$', views.BookingDuration.as_view()),
    url(r'^booking/(?P<pk>[0-9]+)/cost/$', views.BookingCost.as_view()),
    url(r'^booking/(?P<pk>[0-9]+)/$', views.BookingDetail.as_view()),
    url(r'^booking/$', views.BookingList.as_view())
]