from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from my_app.models import Product, Review
from django.http import HttpResponse, JsonResponse
from my_app.form import ProductForm
from .form import ReviewForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from .form import CustomSignupForm 
from .tasks import send_review_notification_email
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db.models import Avg
from django.utils.timezone import now

# Home page
def home(request):
    return render(request, 'index.html')

@cache_page(60 * 10)  # Cache this view for 10 minutes
def pro(request):
    print("Fetching from database...")  # Will not show if from cache
    products = Product.objects.all()
    for product in products:
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = avg_rating if avg_rating else 0
    context = {
        'prdt': products,
        'timestamp': now()
    }
    return render(request, 'products.html', context)

# Add new product page
def add(request):
    f = ProductForm()
    if request.method == 'POST':
        pf = ProductForm(request.POST, request.FILES)
        if pf.is_valid():
            pf.save()
            messages.success(request, "Product added successfully!")
            return redirect('add')
    return render(request, 'add_product.html', {'form': f})

# Delete a product
def delete_product(request, pro_id):
    p = get_object_or_404(Product, id=pro_id)
    p.delete()
    return redirect('products')

# Edit product page
def edit(request, pro_id):
    p = get_object_or_404(Product, id=pro_id)
    f = ProductForm(request.POST or None, instance=p)
    if f.is_valid():
        f.save()
        return redirect('products')
    return render(request, 'add_product.html', {'form': f})

def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please sign in.")
            return redirect('signin')
    else:
        form = CustomSignupForm()
    return render(request, 'signup.html', {'form': form})

# User sign in
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'user_dashboard.html', {
                'fname': user.first_name,
                'lname': user.last_name
            })
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'signin.html')

# User sign out
def signout(request):
    logout(request)
    return render(request, 'index.html')

# Add to cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1
        }
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')

# View cart
def view_cart(request):
    cart = request.session.get('cart', {})
    return render(request, 'cart.html', {'cart': cart})

# Remove from cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('view_cart')

# Clear cart
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('view_cart')

# Submit a product review, redirect to thank you page, and send email
def submit_review(request, product_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        rating = request.POST.get('rating')

        product = get_object_or_404(Product, id=product_id)
        Review.objects.create(
            product=product,
            user=request.user,
            content=content,
            rating=rating
        )

        # Call Celery task
        send_review_notification_email.delay(
            username=request.user.username,
            product_name=product.name,
            review_content=content,
            rating=rating
        )

        return redirect('thank_you')

    return redirect('product_detail', product_id=product_id)

  
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews
    })

# Thank you page
def thank_you(request):
    return render(request, 'thank_you.html')

 
def clear_cache(request):
    if request.method == 'POST':
        cache.clear()
        messages.success(request, '✅ Cache has been cleared successfully!')
    return redirect('pro')