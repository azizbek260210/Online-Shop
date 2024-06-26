from django.shortcuts import render, redirect
from main import models
from django.contrib.auth.decorators import login_required


@login_required(login_url='auth:sign-in')
def product_list(request):
    categorys = models.Category.objects.all()
    cart = models.Cart.objects.get_or_create(user=request.user, status=1)
    wishlist = models.WishList.objects.filter(user=request.user)
    category_code = request.GET.get('category_id')
    if category_code:
        filters = {}
        for key, value in request.GET.items():
            print(key, value)
            if value and not value == '0':
                if key == 'min_price':
                    key = 'price__gte'
                elif key == 'max_price':
                    key = 'price__lte'
                elif key == 'name':
                    key = 'name__icontains'
                filters[key] = value
        products = models.Product.objects.filter(**filters)
    else:
        products = models.Product.objects.all()

    code = [item.product.code for item in wishlist]
    for product in products:
        value = product.code in code
        setattr(product, 'is_wishlisted', value)

    context = {
        'categorys': categorys,
        'products': products,
        'cart': cart,
        'wishlist': wishlist,

    }

    return render(request, 'front/products.html', context)


@login_required(login_url='auth:sign-in')
def category_list(request, id):
    categorys = models.Category.objects.all()
    catg = models.Category.objects.get(id=id)
    products = models.Product.objects.filter(category=catg)
    cart = models.Cart.objects.get_or_create(user=request.user, status=1)
    wishlist = models.WishList.objects.filter(user=request.user)

    code = [item.product.code for item in wishlist]
    for product in products:
        value = product.code in code
        setattr(product, 'is_wishlisted', value)
    context = {
        'categorys': categorys,
        'products': products,
        'categor': catg,
        'cart': cart,
        'wishlist': wishlist,

    }

    return render(request, 'front/shoplist.html', context)


@login_required(login_url='auth:sign-in')
def index(request):
    products = models.Product.objects.all()
    categorys = models.Category.objects.all()
    banners = models.Banner.objects.all()
    cart = models.Cart.objects.get_or_create(user=request.user, status=1)
    wishlist = models.WishList.objects.filter(user=request.user)
    reviews = models.Review.objects.filter().order_by('-id')[1:6]

    w_codes = [item.product.code for item in wishlist]
    for product in products:
        value = product.code in w_codes
        setattr(product, 'is_wishlisted', value)

    newproduct = products.order_by('-id')[:4]
    for new in newproduct:
        value = new.code in w_codes
        setattr(new, 'is_wishlisted', value)

    context = {
        'categorys': categorys,
        'banners': banners,
        'products': products,
        'wishlist': wishlist,
        'cart': cart,
        'reviews': reviews,
        'newproducts': newproduct

    }
    return render(request, 'front/index.html', context)


def product_detail(request, code):
    categorys = models.Category.objects.all()
    product = models.Product.objects.get(code=code)
    images = models.ProductImg.objects.filter(product=product.id)
    reviews = models.Review.objects.filter(product=product.id)
    cart = models.Cart.objects.get_or_create(user=request.user, status=1)
    wishlist = models.WishList.objects.filter(product=product, user=request.user)
    if wishlist:
        wishlist = wishlist[0]
    # videos = models.ProductVideo.objects.filter(product=product)
    print(images)
    context = {
        'categorys': categorys,
        'product': product,
        'images': images,
        'reviews': reviews,
        'wishlist': wishlist,
        'cart': cart,
        # 'videos': videos,
    }
    return render(request, 'front/shopdetail.html', context)


@login_required(login_url='auth:sign-in')
def cart_list(request):
    categorys = models.Category.objects.all()
    queryset = models.Cart.objects.filter(user=request.user, status=2)
    cart = models.Cart.objects.get_or_create(user=request.user, status=1)
    context = {
        'categorys': categorys,
        'queryset': queryset,
        'cart': cart,
    }
    return render(request, 'front/carts/list.html', context)


@login_required(login_url='auth:sign-in')
def active_cart(request):
    queryset, _ = models.Cart.objects.get_or_create(user=request.user, status=1)
    return redirect('front:cart', queryset.code)


@login_required(login_url='auth:sign-in')
def cart_detail(request, code):
    categorys = models.Category.objects.all()
    cart = models.Cart.objects.get(code=code)
    queryset = models.CartProduct.objects.filter(cart=cart)

    context = {
        'cart': cart,
        'queryset': queryset,
        'categorys': categorys,
    }

    return render(request, 'front/carts/detail.html', context)


def update_qtty(request, id):
    if request.method == 'POST':
        count = int(request.POST['count'])
        cart_product = models.CartProduct.objects.get(id=id)
        cart_product.count = count
        cart_product.save()
        return redirect('front:cart', cart_product.cart.code)


@login_required(login_url='auth:sign-in')
def cart_product_delete(request, id):
    cart_product = models.CartProduct.objects.get(id=id)
    cart_product.delete()
    return redirect('front:cart', cart_product.cart.code)


@login_required(login_url='auth:sign-in')
def add_cart_product(request, code):
    product = models.Product.objects.get(code=code)
    cart, _ = models.Cart.objects.get_or_create(user=request.user, status=1)
    count = 1
    if models.CartProduct.objects.filter(product=product, cart=cart).count():
        c = models.CartProduct.objects.get(product=product, cart=cart)
        c.count += 1
        c.save()
    else:
        p = models.CartProduct.objects.create(
            product=product,
            cart=cart,
            count=count,
        )

    return redirect('front:cart', cart.code)


@login_required(login_url='auth:sign-in')
def product_order(request):
    cart = models.Cart.objects.get(user=request.user, status=1)
    cart_product = models.CartProduct.objects.filter(cart=cart)
    for item in cart_product:
        item.product.quantity -= item.count
        item.product.save()

    cart.status = 2
    cart.save()

    return redirect('front:order_list')


@login_required(login_url='auth:sign-in')
def order_list(request):
    categorys = models.Category.objects.all()
    queryset = models.Cart.objects.filter(user=request.user, status__in=[2, 3, 4]).order_by('-date')
    context = {
        'queryset': queryset,
        'categorys': categorys,
    }

    return render(request, 'front/order/list.html', context)


@login_required(login_url='auth:sign-in')
def order_confirm(request, code):
    cart = models.Cart.objects.get(code=code, user=request.user)
    cart.status = 4
    cart.save()
    return redirect('front:order_list')


@login_required(login_url='auth:sign-in')
def order_rejection(request, code):
    cart = models.Cart.objects.get(code=code, user=request.user)
    cart.status = 3
    cart.save()
    return redirect('front:order_list')


@login_required(login_url='auth:sign-in')
def order_review(request, code):
    cart = models.Cart.objects.get(code=code, user=request.user)
    products = models.CartProduct.objects.filter(cart=cart)
    if request.method == 'POST':
        for product in products:
            review = models.Review.objects.create(
                product=product.product,
                user=request.user,
                mark=int(request.POST.get('mark')),
                text=request.POST.get('message')
            )

    return redirect('front:order_list')


# ---------WISHLIST---------
@login_required(login_url='auth:sign-in')
def wishlist(request):
    categorys = models.Category.objects.all()
    queryset = models.WishList.objects.filter(user=request.user)

    context = {
        'categorys': categorys,
        'queryset': queryset,
    }

    return render(request, 'front/wishlist.html', context)


@login_required(login_url='auth:sign-in')
def wishlist_delete(request, code):
    wishlist = models.WishList.objects.get(product__code=code, user=request.user)
    if wishlist:
        wishlist.delete()
    else:
        pass
    # return redirect('front:wishlist')
    return redirect(request.META.get('HTTP_REFERER', 'front:wishlis'))


@login_required(login_url='auth:sign-in')
def wishlist_add(request, code):
    product = models.Product.objects.get(code=code)
    models.WishList.objects.create(product=product, user=request.user)
    # return redirect('front:wishlist')
    return redirect(request.META.get('HTTP_REFERER', 'front:wishlis'))
