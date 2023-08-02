# admin.py
from django.contrib import admin
from .models import Tour, Booking, Image, Rating
from django.core.exceptions import ValidationError
class ImageInline(admin.TabularInline):
    model = Image

class TourAmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'start_date','end_date','location','created_at' )
    search_fields = ('name',)
    filter = ('start_date','end_date','location','created_at')
    inlines = [ImageInline]

admin.site.register(Tour, TourAmin)


class BookingAmin(admin.ModelAdmin):
    list_display = ('tour', 'user', 'status', 'created_at', 'departure_date')
    list_filter = ('status', 'created_at', 'departure_date')
    readonly_fields = ('tour', 'user', 'created_at', 'departure_date','price','end_date','number_of_people')
    actions = ['approve_booking']

    def approve_booking(self, request, queryset):
        # Phê duyệt các đơn đặt Tour đã chọn
        for booking in queryset:
            if booking.status == 'Pending':
                booking.status = 'Confirmed'
                booking.is_approved = True
                booking.save()

    approve_booking.short_description = 'Phê duyệt các đơn đặt Tour đã chọn'

    def save_model(self, request, obj, form, change):
        # Tự động lưu thông tin người dùng thực hiện phê duyệt đơn đặt Tour
        obj.approved_by = request.user
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        # Override the delete_model method to check the status of the tour's bookings before deleting the tour
        if obj.tour.has_pending_booking() or obj.tour.has_future_bookings():
            raise ValidationError(
                "Không thể xóa Tour khi có đơn đặt đang chờ xử lý hoặc được xác nhận."
            )
        obj.delete()

    def delete_queryset(self, request, queryset):
        # Override the delete_queryset method to check the status of bookings before deleting a batch of tours
        for booking in queryset:
            if booking.tour.has_pending_booking() or booking.tour.has_future_bookings():
                raise ValidationError(
                    f"Không thể xóa Tour '{booking.tour.name}' khi có đơn đặt đang chờ xử lý hoặc được xác nhận."
                )
        queryset.delete()

admin.site.register(Booking, BookingAmin)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = (
        "rating",
    )

    def has_add_permission(self, request):
        # Vô hiệu hóa khả năng thêm mới người dùng trong trang quản trị
        return False