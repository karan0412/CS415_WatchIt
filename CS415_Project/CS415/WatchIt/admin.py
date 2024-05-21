from django.contrib import admin
from . import models
from django.utils.html import format_html

admin.site.site_header = "WatchIt Administration"
admin.site.site_title = "WatchIt Admin"
admin.site.index_title = "Welcome to the WatchIt Admin Panel"

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'thumbnail', 'director')
    search_fields = ('title', 'director')
    list_filter = ('release_date', 'tags')
    fields = ('title', 'description', 'duration', 'starring', 'director', 'release_date', 'language', 'ageRating', 'image', 'trailer', 'tags')
    
    def thumbnail(self, obj):
        return format_html('<img src="{}" width="150" height="100" />', obj.image.url)
    thumbnail.short_description = 'Image'

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('booking_date', 'showtime')
    fields = ('user', 'movie', 'cinema_hall', 'showtime', 'booking_date', 'payment_amount', 'num_seats', 'seats', 'edited')
    readonly_fields = ('booking_date',)
    filter_horizontal = ('seats',)

class SeatInline(admin.TabularInline):
    model = models.Seat
    extra = 0
    readonly_fields = ('seat_label', 'availability')
    can_delete = False

class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie_thumbnail', 'movie', 'cinema_hall_type', 'local_showtime')
    search_fields = ('movie__title', 'cinema_hall__cinema_type')
    list_filter = ('showtime',)
    inlines = [SeatInline]

    def movie_thumbnail(self, obj):
        if obj.movie and obj.movie.image:
            return format_html('<img src="{}" width="100" height="75" />', obj.movie.image.url)
        return "No Image"
    movie_thumbnail.short_description = 'Movie Thumbnail'

    def cinema_hall_type(self, obj):
        return obj.cinema_hall.cinema_type
    cinema_hall_type.short_description = 'Cinema Type'

class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_label', 'showtime', 'availability')
    search_fields = ('seat_label', 'showtime__movie__title')
    list_filter = ('availability', 'showtime')
    readonly_fields = ('seat_label', 'showtime')
    list_select_related = ('showtime',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        showtime_id = request.GET.get('showtime__id__exact')
        if showtime_id:
            queryset = queryset.filter(showtime__id=showtime_id)
        return queryset

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(models.CinemaHall)
admin.site.register(models.Seat, SeatAdmin)
admin.site.register(models.Movie, MovieAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Booking, BookingAdmin)
admin.site.register(models.Showtime, ShowtimeAdmin)
admin.site.register(models.Deals)
admin.site.register(models.User)
