from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import UserProfile
from accounts.views import check_role_customer
from marketplace.context_processor import get_cart_counter, get_cart_amount
from marketplace.models import Cart
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from vendor.models import Vendor
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from functools import wraps

def user_passes_test_if_logged_in(test_func, login_url=None, redirect_field_name='next'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # If user is not authenticated, skip the test and just run the view
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            # If authenticated, run the test
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            # Otherwise, deny access (redirect or 403)
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return _wrapped_view
    return decorator

# Create your views here.
def marketplace(request):
    vendors=Vendor.objects.filter(is_approved=True,user__is_active=True).order_by('-vendor_name')
    vendor_count=vendors.count()
    for vendor in vendors:
        print("user profile is",vendor.vendor_name,vendor.user_profile.full_address())
    context={
        'vendors':vendors,
        'vendor_count':vendor_count,
    }
    return render(request,'marketplace/listings.html',context)

def vendor_details(request,vendor_slug):
    vendor=get_object_or_404(Vendor,vendor_slug=vendor_slug)
    categories=Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items=Cart.objects.filter(user=request.user)
    else:
        cart_items=None
    context={
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
    }
    return render(request,'marketplace/vendor_details.html',context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if the request is an AJAX request
            try:
                fooditem = get_object_or_404(FoodItem, id=food_id)
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity','card_counter': get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart','card_counter': get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
            except FoodItem.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if the request is an AJAX request
            try:
                fooditem = get_object_or_404(FoodItem, id=food_id)
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity=0
                    return JsonResponse({'status': 'Success', 'card_counter': get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!','card_counter': get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amount(request)})
            except FoodItem.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url='login')
def cart(request):
    cart_items= Cart.objects.filter(user=request.user).order_by('created_at')
    print(cart_items)
    print(get_cart_amount(request))
    context={
        'cart_items':cart_items,
        'cart_cost':get_cart_amount(request),
    }
    return render(request,'marketplace/cart.html',context)


def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                cart_item=Cart.objects.get(user=request.user,id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'cart item has been deleted','card_counter': get_cart_counter(request),'cart_amount':get_cart_amount(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})


@login_required(login_url='login')
def checkout(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    if cart_count <=0:
        return redirect('marketplace')
    user_profile=UserProfile.objects.get(user=request.user)
    default_values={
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.full_address(),
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pin_code
    }
    form=OrderForm(initial=default_values)
    context={
        'form':form,
        'cart_items':cart_items,
        'cart_count':cart_count
    }
    return render(request,'marketplace/checkout.html',context)