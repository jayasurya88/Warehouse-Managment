from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,Product,Cart,Order
from .models import CustomUser
from django.contrib import auth, messages
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model
def index(request):
     categories = Category.objects.all()
     products = Product.objects.all()

     context = {
        'categories': categories,
        'products': products,
    }
     return render(request, 'index.html',context )

def delivery_dashboard(request):
    orders = Order.objects.all()
    return render(request, 'delivery_dashboard.html', {'orders': orders})
    

def client_register(request):
    return render(request,'client_register.html')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import CustomUser
import re

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        photo = request.FILES.get('photo', None)
        pan_card = request.POST['pan_card']
        address = request.POST['address']
        user_type = request.POST.get('user_type', '1')

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email format')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        elif CustomUser.objects.filter(pan_card=pan_card).exists():
            messages.error(request, 'PAN card already exists')
        else:
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    photo=photo,
                    pan_card=pan_card,
                    address=address,
                    user_type=user_type
                )
                user.is_approved = False
                user.save()
                return redirect('registration_pending')  
            except IntegrityError:
                messages.error(request, 'There was an error creating your account. Please try again.')

    return render(request, 'client_register.html')





def registration_pending(request):
    return render(request,'registration_pending.html')



def adminpage(request):
    return render(request,'adminpage.html')

def approve_disapprove(request):
    users = CustomUser.objects.filter(user_type='2') 
    userss = CustomUser.objects.filter(user_type='3')  
    pending_delivery_count = userss.filter(is_approved=False).count()
    pending_user_count = users.filter(is_approved=False).count()  
    orders = Order.objects.all()
    order_notification_count = Order.objects.filter(status='Pending').count() 
    return render(request, 'approve_disapprove.html', {'users': users, 'pending_user_count': pending_user_count ,'userss': userss,
        'pending_delivery_count': pending_delivery_count,'orders': orders, 'order_notification_count': order_notification_count})


def delivery_approve(request):
    users = CustomUser.objects.filter(user_type='3')
  
    pending_delivery_count = users.filter(is_approved=False).count()  
    return render(request, 'delivery_approve.html', {'users': users,
        'pending_delivery_count': pending_delivery_count})

def disapprove_delivery(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.delete()
    return redirect('delivery_approve')

def approve_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_approved = True
    user.save()
  
    send_email_with_password(user)
    return redirect('approve_disapprove')


def send_email_with_password(user):
    import random
    import string
    from django.core.mail import send_mail

    password = ''.join(random.choices(string.digits, k=6))
    user.set_password(password)
    user.save()
    
    send_mail(
        'Your account has been approved',
        f'Your new password is: {password}',
        'admin@example.com',
        [user.email],
        fail_silently=False,
    )


def disapprove_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = False
    user.delete()

    return redirect('approve_disapprove')

def delivery_approve(request):
    users = CustomUser.objects.filter(user_type='3')  # Assuming user_type '3' is for delivery users
    pending_delivery_count = users.filter(is_approved=False).count()
    return render(request, 'delivery_approve.html', {
        'users': users,
        'pending_delivery_count': pending_delivery_count
    })
def delivery_register(request):
    return render(request,'delivery_register.html')


def login1(request):
    return render(request,'login1.html')



def login2(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                auth.login(request, user)
                if user.user_type == '1':
                    return redirect('approve_disapprove')
                elif user.user_type == '2':
                    return redirect('clientpage')
                else:
                    return redirect('delivery_dashboard')
            else:
                messages.error(request, "Your account is disabled.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login1.html')


def custom_password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
            return redirect('password_reset')  # Redirect back to the password reset page
        
        if not user.check_password(current_password):
            messages.error(request, 'Incorrect current password.')
            return redirect('password_reset')  # Redirect back to the password reset page
        
        if len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters long.')
            return redirect('password_reset')  # Redirect back to the password reset page
        
        # Add more password strength checks here if needed
        
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password reset successfully.')
        return redirect('login1')  # Redirect to home or any other desired page
    
    else:
        return render(request, 'password_reset.html')
def password_reset(request):
    return render(request,'password_reset.html')




def clientpage(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request,'clientpage.html', context)



def addcategory(request):
    # Retrieve existing messages
    all_messages = messages.get_messages(request)
    context = {'messages': all_messages}
    return render(request, 'addcategory.html', context)

def addcategory1(request):
    if request.method == 'POST':
        category_name = request.POST.get('category')
        if category_name:
            category = Category.objects.create(category_name=category_name)
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('addcategory1')  # Redirect to another page
        else:
            messages.error(request, 'Category name is required!')
    
    # Retrieve existing messages
    all_messages = messages.get_messages(request)
    context = {'messages': all_messages}
    return render(request, 'addcategory.html', context)
    # Retrieve existing error messages
    all_messages = messages.get_messages(request)
    context = {'messages': all_messages}
    return render(request, 'addcategory.html', context)

def addproduct(request):
    categories = Category.objects.all()  # Retrieve all categories
    return render(request, 'addproduct.html', {'categories': categories})


def addproduct1(request):
    if request.method == 'POST':
        try:
            # Retrieve form data from POST request
            pname = request.POST.get('name')
            pdesc = request.POST.get('description')
            pspec = request.POST.get('specifications')
            pprice = request.POST.get('price')
            pstock = request.POST.get('stock_quantity')
            pimg = request.FILES.get('pimg')
            category_id = request.POST.get('category')
            
            # Retrieve category instance
            category = Category.objects.get(id=category_id)
            
            # Create new product instance and save to database
            product = Product(
                name=pname, 
                description=pdesc, 
                specifications=pspec, 
                price=pprice, 
                stock_quantity=pstock, 
                pimg=pimg, 
                category=category
            )
            product.save()
            
            # Redirect to admin home page
            messages.success(request, 'Product added successfully!')
            return redirect('addproduct')  # Replace 'admin_page' with your actual URL name for the admin home
        except Exception as e:
            print(e)  # Print any exceptions that occur
            messages.error(request, 'Failed to add product. Please try again.')  # Display error message
            return redirect('addproduct')  # Redirect to addproduct page
    else:
        # Retrieve all categories to populate category dropdown
        categories = Category.objects.all()
        return render(request, 'add_product.html', {'categories': categories})
    

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        description = request.POST.get('description')
        specifications = request.POST.get('specifications')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        pimg = request.FILES.get('pimg')
        
        category = Category.objects.get(id=category_id)
        
        product.category = category
        product.name = name
        product.description = description
        product.specifications = specifications
        product.price = price
        product.stock_quantity = stock_quantity
        if pimg:
            product.pimg = pimg
        
        product.save()
        
        messages.success(request, 'Product updated successfully!')
        return redirect('product_list')
    
    categories = Category.objects.all()
    return render(request, 'add_edit_product.html', {'product': product, 'categories': categories})




def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'confirm_delete.html', {'product': product})


def category_page(request, category_id):
    category = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all() 
    return render(request, 'category_page.html', {'category': category, 'products': products,'categories': categories})


def logout(request):
    auth.logout(request)
    return render(request,'index.html')


def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)  # Assuming user is logged in
    total_price = sum(item.total_price() for item in cart_items)  # Ensure to call the method
    cart_items_count = cart_items.count()
    categories = Category.objects.all() 
    return render(request, 'cart_page.html', {
        'cart_items': cart_items, 
        'total_price': total_price, 
        'categories': categories,
        'cart_items_count': cart_items_count
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        cart_item, created = Cart.objects.get_or_create(user=request.user, prod=product)
        if created:
            cart_item.quantity = 1  # Initialize quantity to 1
        else:
            if cart_item.quantity < product.stock_quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, 'Not enough stock available.')
                return redirect('cart_page')
        
        cart_item.save()
        messages.success(request, 'Product added to cart successfully!')
        return redirect('cart_page')

    return redirect('index')

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, pk=cart_item_id)
    
    if request.method == 'POST':
        cart_item.delete()
        messages.success(request, 'Product removed from cart.')
        return redirect('cart_page')

    return redirect('index')


def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, pk=cart_item_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'subtract':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
        elif action == 'add':
            if cart_item.quantity < cart_item.prod.stock_quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, 'Not enough stock available.')
        cart_item.save()
        return redirect('cart_page')







def checkoutpage(request):
    return render (request,'checkoutpage.html')



from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem, Product
from django.contrib.auth.decorators import login_required
import uuid

import random
import string
def generate_tracking_id(length=12):
    """Generate a unique random tracking ID."""
    characters = string.ascii_letters + string.digits
    while True:
        tracking_id = ''.join(random.choices(characters, k=length))
        if not Order.objects.filter(tracking_id=tracking_id).exists():
            break
    return tracking_id

from django.shortcuts import render, redirect
from .models import Order, OrderItem, Product

def generate_tracking_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

SHIPPING_METHODS = {
    'road': 'By Road',
    'ship': 'By Ship',
    'airline': 'By Airline'
}
from datetime import timedelta
from django.utils import timezone
@login_required
def checkout_view(request):
    if request.method == 'POST':
        address = request.POST['address']
        landmark = request.POST['landmark']
        shipping_method = request.POST['shipping_method']

        if shipping_method not in SHIPPING_METHODS:
            messages.error(request, 'Invalid shipping method selected.')
            return render(request, 'checkoutpage.html', {
                'delivery_methods': SHIPPING_METHODS
            })

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')

        for item in cart_items:
            if item.quantity > item.prod.stock_quantity:
                messages.error(request, f'Insufficient stock for {item.prod.name}. Only {item.prod.stock_quantity} items left.')
                return redirect('cart')

        # Calculate estimated delivery date (current date + 7 days)
        estimated_delivery_date = timezone.now() + timedelta(days=7)

        order = Order.objects.create(
            user=request.user,
            address=address,
            landmark=landmark,
            delivery_method=SHIPPING_METHODS[shipping_method],
            estimated_delivery_date=estimated_delivery_date  # Assign estimated delivery date
        )

        for item in cart_items:
            product = item.prod
            product.stock_quantity -= item.quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity
            )
            item.delete()  # Clear the cart

        # Send email with tracking ID and estimated delivery date
        send_mail(
            'Your Order Confirmation',
            f'Thank you for your purchase. Your tracking ID is {order.tracking_id}. Estimated delivery date is {estimated_delivery_date.strftime("%Y-%m-%d")}.',
            'from@example.com',
            [request.user.email],
            fail_silently=False,
        )

        return redirect('order_success')

    return render(request, 'checkoutpage.html', {'delivery_methods': SHIPPING_METHODS})
def order_success(request):
    return render (request,'order_success.html')



from .models import Order


def admin_orders(request):
    orders = Order.objects.prefetch_related('items__product').all()
    return render(request, 'admin_orders.html', {'orders': orders})


def assign_delivery_person(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    delivery_boys = CustomUser.objects.filter(user_type='3')  # Filter to get delivery boys

    if request.method == 'POST':
        delivery_person_id = request.POST.get('delivery_person')
        delivery_person = get_object_or_404(CustomUser, id=delivery_person_id)
        order.delivery_person = delivery_person
        order.save()
        messages.success(request, 'Delivery person assigned successfully!')
        return redirect('admin_orders')  # Redirect back to the all orders page

    return render(request, 'assign_delivery_person.html', {'order': order, 'delivery_boys': delivery_boys})


def search_view(request):
    tracking_id = request.GET.get('tracking_id', None)
    order = None
    error = None

    if tracking_id:
        try:
            order = Order.objects.get(tracking_id=tracking_id)
        except Order.DoesNotExist:
            error = "No order found with this tracking ID."

    return render(request, 'search.html', {'order': order, 'error': error})




def delivery_person_orders(request):
    orders = Order.objects.filter(delivery_person=request.user)
    return render(request, 'delivery_person_orders.html', {'orders': orders, 'msg': messages.get_messages(request)})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order

def update_order_status_form(request, order_id):
    order = get_object_or_404(Order, id=order_id, delivery_person=request.user)
    
    if request.method == 'POST':
        status = request.POST['status']
        dispatch_location = request.POST.get('dispatch_location', '').strip()
        transmit_location = request.POST.get('transmit_location', '').strip()

        # Validate required fields based on status
        if status == 'dispatched' and not dispatch_location:
            messages.error(request, 'Dispatch location is required for dispatched status.')
        elif status == 'intransit' and not transmit_location:
            messages.error(request, 'Transmit location is required for in transit status.')
        else:
            # Update order fields based on status
            order.status = status
            order.dispatch_location = dispatch_location if status == 'dispatched' else ''
            order.transmit_location = transmit_location if status == 'intransit' else ''

            # Special handling for status 'delivered'
            if status == 'delivered':
                order.status = 'Delivered by Delivery'

            order.save()
            
            return redirect('delivery_person_orders')
    
    return render(request, 'update_order_status_form.html', {'order': order})
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']
        status = request.POST['status']
        order = get_object_or_404(Order, id=order_id, delivery_person=request.user)
        order.status = status
        order.save()
        return redirect('delivery_person_orders')
    return redirect('delivery_dashboard')



# def mark_order_as_completed_client(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     if request.user.user_type == '2':  # Check if the user is a client
#         order.client_marked_completed = True
#         order.save()
#     return redirect('/') 
def mark_order_as_completed_client(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user.user_type == '2':  # Check if the user is a client
        order.client_marked_completed = True
        order.save()

        # Send email notification
        send_order_completion_email(order)

    return redirect('client_order_list')
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
def send_order_completion_email(order):
    subject = 'Your Order Completion Notification'
    html_message = render_to_string('order_completion_email.html', {'order': order})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = [order.user.email]
    msg = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
    msg.attach_alternative(html_message, "text/html")
    msg.send()
def mark_order_as_completed_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user.user_type == '3':  # Check if the user is a delivery person
        order.delivery_person_marked_completed = True
        order.save()
      
    return redirect('delivery_person_orders')


def client_order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'client_order_list.html', {'orders': orders})






from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser


from django.contrib.auth.decorators import login_required
from .models import CustomUser

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser
import re

def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        pan_card = request.POST.get('pan_card')
        
        # Email validation regex
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        if not re.match(email_pattern, email):
            messages.error(request, 'Invalid email format')
        elif CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'Email already exists')
        elif CustomUser.objects.filter(pan_card=pan_card).exclude(pk=user.pk).exists():
            messages.error(request, 'PAN card already exists')
        else:
            # Update user information
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone
            user.pan_card = pan_card
            
            # Handle photo upload
            if 'photo' in request.FILES:
                user.photo = request.FILES['photo']
            user.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile_view')
    
    return render(request, 'edit_profile.html', {'user': request.user})

def profile_view(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'profile.html', context)
