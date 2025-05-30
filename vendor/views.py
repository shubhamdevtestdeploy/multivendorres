from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify


from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from vendor.forms import VendorForm

from accounts.forms import UserProfileForm
from vendor.models import Vendor
from django.contrib import messages

def get_vendor(request):
    vendor=Vendor.objects.get(user=request.user)
    return vendor
# Create your views here.

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile=get_object_or_404(UserProfile,user=request.user)
    vendor=get_object_or_404(Vendor,user=request.user)
    if request.method=='POST':
        profile_form= UserProfileForm(request.POST,request.FILES,instance=profile)
        vendor_form= VendorForm(request.POST,request.FILES,instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request,'Settings Updated!')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form=UserProfileForm(instance=profile)
        vendor_form=VendorForm(instance=vendor)
    context={
        'profile_form':profile_form,
        'vendor_form': vendor_form,
        'profile':profile,
        'vendor':vendor,
    }
    return render(request,'vendor/vprofile.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor=get_vendor(request)
    categories=Category.objects.filter(vendor=vendor).order_by('created_at')
    context={
        'categories':categories,
    }
    return render(request,'vendor/menu_builder.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request,pk=None):
    vendor=get_vendor(request)
    category=get_object_or_404(Category,pk=pk)
    fooditems=FoodItem.objects.filter(vendor=vendor,category=category)
    print(vendor,category,pk,fooditems)
    context={
        'fooditems':fooditems,
        'category':category,

    }
    return render(request,'vendor/fooditems_by_category.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            vendor = Vendor.objects.get(user=request.user)  # Get the current vendor

            # Check if a category with the same name exists for this vendor
            if Category.objects.filter(category_name=category_name, vendor=vendor).exists():
                messages.error(request, 'Category with this name already exists!')
                return redirect('menu_builder')  # Redirect to prevent duplicate submissions

            # Save category only if it doesn't exist
            category = form.save(commit=False)
            category.vendor = vendor
            category.slug = slugify(category_name)  # Generate slug
            category.save()

            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)

    else:
        form = CategoryForm()

    context = {'form': form}
    return render(request, 'vendor/add-category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category=get_object_or_404(Category,pk=pk)
    print("category is",category,pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST,instance=category)
        print(form)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            vendor = Vendor.objects.get(user=request.user)  # Get the current vendor
            category = form.save(commit=False)
            category.vendor = vendor
            category.slug = slugify(category_name)  # Generate slug
            category.save()

            messages.success(request, '✅ Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)

    context = {'form': form,'category':category,}
    return render(request, 'vendor/edit-category.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request,pk=None):
    category=get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request, '✅ Category has been deleted successfully!')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST,request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']

            # Save category only if it doesn't exist
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)  # Generate slug
            food.save()
            messages.success(request, '✅ food Item added successfully!')
            return redirect('fooditems_by_category',food.category.id)
        else:
            print(form.errors)
    else:
        form=FoodItemForm()
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))
    context={
        'form':form,
    }
    return render(request,'vendor/add_food.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food=get_object_or_404(FoodItem,pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST,request.FILES,instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)  # Generate slug
            food.save()

            messages.success(request, '✅ Food item updated successfully!')
            return redirect('fooditems_by_category',food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))

    context = {'form': form,'food':food,}
    return render(request, 'vendor/edit-food.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request,pk=None):
    food=get_object_or_404(FoodItem,pk=pk)
    food.delete()
    messages.success(request, '✅ Food item has been deleted successfully!')
    return redirect('fooditems_by_category',food.category.id)