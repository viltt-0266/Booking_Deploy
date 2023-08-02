from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext
from django.views import generic
from .models import Tour, Booking
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import TourSearchForm,BookingForm, RatingCommentForm
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib import messages

# Create your views here.
def index(request):
    context = {"title": gettext("Home Page")}
    return render(request, "index.html", context=context)

# TourListView 

class TourListView(generic.ListView):
    model = Tour

# Login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  
        else:
            return render(request, 'login.html', {'error_message': 'Đăng nhập không thành công. Vui lòng thử lại.'})
    else:
        return render(request, 'login.html')

#Log Out

def logout_view(request):
    logout(request)
    return redirect('index')

# Tour Detail & Book Tour


class TourDetailView(generic.DetailView):
    model = Tour
    template_name = 'tour_booking/tour_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookingForm()
        return context

    def post(self, request, *args, **kwargs):
        tour = self.get_object()
        form = BookingForm(request.POST)
        if form.is_valid():
            current_date = timezone.now().date()
            departure_date = form.cleaned_data['departure_date'].date()

            if departure_date > current_date:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.tour = tour
                booking.status = 'Pending'
                booking.price = tour.price * int(form.cleaned_data['number_of_people'])
                booking.save()
                return redirect(reverse('tour-detail', args=[str(tour.pk)]))
            else:
                error_message = 'Bạn chỉ được đặt tour cho tương lai.'
                return JsonResponse({'form_errors': form.errors, 'error_message': error_message})
        else:
            return JsonResponse({'form_errors': form.errors})


#List Booking

@login_required
def list_bookings(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')  # Lấy id của booking được gửi từ form

        if booking_id:
            booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

            if booking.status == 'Pending':  # Chỉ cho phép hủy tour khi booking đang ở trạng thái "Pending"
                booking.status = 'Cancelled'
                booking.save()
                
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'tour_booking/list_bookings.html', {'bookings': bookings})

#Search List

def search_view(request):
    form = TourSearchForm(request.GET)
    tour_list = Tour.objects.all()
    tour_list = tour_list.order_by('-average_rating', 'created_at')

    # Xử lý tìm kiếm theo từ khóa
    query = request.GET.get('query')
    if query:
        tour_list = tour_list.filter(name__icontains=query)

    # Xử lý lọc theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        tour_list = tour_list.filter(price__range=(min_price, max_price))
    # Xử lý lọc theo ngày
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        tour_list = tour_list.filter(start_date__gte=start_date)
    if end_date:
        tour_list = tour_list.filter(end_date__lte=end_date)

    # Sử dụng prefetch_related để tải hình ảnh liên quan cho tất cả các tour trong queryset
    tour_list = tour_list.prefetch_related('image_set')

    context = {
        'tour_list': tour_list,
        'form': form,
    }
    return render(request, 'tour_booking/tour_list.html', context)

    
#Comment

@login_required
def tour_rating_comment(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    try:
        booking = Booking.objects.filter(user=request.user, tour=tour).first()
    except Booking.DoesNotExist:
        booking = None

    if not booking or not booking.is_approved:
        return HttpResponse("Bạn chưa được admin xác nhận, không thể bình luận.")  # Hoặc hiển thị trang thông báo lỗi

    if request.method == 'POST':
        rating_comment_form = RatingCommentForm(request.POST)
        if rating_comment_form.is_valid():
            rating = rating_comment_form.save(commit=False)
            rating.user = request.user
            rating.tour = tour
            rating.save()

            # Đánh dấu đơn đặt tour đã được admin approve
            booking.is_approved = True
            booking.save()

            return redirect(reverse('tour-detail', args=[str(tour.pk)]))
    else:
        rating_comment_form = RatingCommentForm()

    return render(request, 'tour_booking/tour_detail.html', {'tour': tour, 'rating_comment_form': rating_comment_form})

# Admin Approve

def approve_tours(request):
    if request.method == 'POST':
        selected_bookings = request.POST.getlist('selected_bookings')
        action = request.POST.get('action')

        if action == 'approve':
            Booking.objects.filter(pk__in=selected_bookings).update(is_approved=True, status='Confirmed')
        elif action == 'cancel':
            bookings_to_cancel = Booking.objects.filter(pk__in=selected_bookings, status__in=['Pending', 'Confirmed'])
            for booking in bookings_to_cancel:
                if booking.status == 'Confirmed':
                    # Nếu đơn đã được xác nhận thì không cho phép hủy
                    continue
                booking.is_cancelled = True
                booking.status = 'Cancelled'
                booking.save()
        elif action == 'delete':
            bookings_to_delete = Booking.objects.filter(pk__in=selected_bookings)
            confirmed_or_pending_bookings = bookings_to_delete.filter(status__in=['Pending', 'Confirmed'])
            if confirmed_or_pending_bookings.exists():
                messages.error(request, "Không thể xóa các đơn đặt đang chờ xử lý hoặc được xác nhận.")
            else:
                bookings_to_delete.filter(status='Cancelled').delete()

    bookings = Booking.objects.all()  # Lấy tất cả các đơn đặt tour
    return render(request, 'admin/approve_tours.html', {'bookings': bookings})





