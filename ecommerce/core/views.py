from decimal import Decimal
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from core.forms import *
from core.models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST


import razorpay
razorpay_client = razorpay.Client(
    auth=("rzp_test_nGiHgJ82KyUMwR", "5qPQLOj7AKBq7JKclx9oDVID")
)

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request,'core/index.html',{'products':products})

def add_product(request):
    if request.method == 'POST':
        form = productform(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Added successfully!!")
            return redirect('/')
        else:
            messages.info(request,"product is not added")
    else:
        form = productform()
    return render(request,'core/add_product.html',{'form':form})


def product_desc(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_desc.html', {'product': product})

def cart_item_count(user):
    return OrderItem.objects.filter(user=user, ordered=False).aggregate(
        total=models.Sum('quantity')
    )['total'] or 0

@require_POST
@login_required(login_url='user_login') 
def add_to_cart(request, pk):
    # Parse JSON body if AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
        except json.JSONDecodeError:
            quantity = 1
    else:
        # If not AJAX, maybe get quantity from POST form data or default 1
        quantity = int(request.POST.get('quantity', 1))
    
    product = Product.objects.get(pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item.quantity += quantity
            order_item.save()
        else:
            order_item.quantity = quantity
            order_item.save()
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order_item.quantity = quantity
        order_item.save()
        order.items.add(order_item)
    
    # Now return JsonResponse for AJAX or redirect for normal POST
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = cart_item_count(request.user)
        return JsonResponse({'success': True, 'cart_count': count})

    messages.info(request, "Item added to cart.")
    return redirect("index")
    
def orderlist(request):
    if Order.objects.filter(user=request.user, ordered=False).exists():
        order = Order.objects.get(user=request.user, ordered=False)
        order_items = order.items.all().order_by('id')
        return render(request, 'core/orderlist.html', {
            'order': order,
            'order_items': order_items,
        })
    return render(request, 'core/orderlist.html', {'message': "Your cart is empty"})


#copy all code from add_to_cart
def add_item(request, pk):
    product = Product.objects.get(pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            if order_item.quantity < product.product_avl_count:
                # increase quantity
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Added another item to your cart.")
                return redirect("orderlist")
            else:
                messages.info(request,"Sorry, product is out of stock")
                return redirect("orderlist")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to cart.")
            return redirect("product_desc",pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to cart.")
        return redirect('product_desc', pk=pk)

def remove_item(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists(): 
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item = OrderItem.objects.filter(product=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "Item quantity was updated.")
                return redirect("orderlist")
            else:
                order_item.delete()
                messages.info(request, "Item removed from cart.")
                return redirect("orderlist")
        else:
            messages.error(request, "This item is not in your cart.")
            return redirect("orderlist")
    else:
        messages.error(request, "You don’t have an active order.")
        return redirect('orderlist')
    
def checkout_page(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        return render(request, 'core/checkout_address.html', {'payment_allow':"allow"})
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            street_address = form.cleaned_data.get('street_address')
            apartment_address = form.cleaned_data.get('apartment_address')
            country = form.cleaned_data.get('country')
            zip_code = form.cleaned_data.get('zip')
            checkout_address = CheckoutAddress(
                user=request.user,
                street_address=street_address,
                apartment_address=apartment_address,
                country=country,
                zip_code=zip_code                
            )
            checkout_address.save()
            print("It should render the summary page")
            return render(request, 'core/checkout_address.html', {'payment_allow':"allow"})
    else:
        form = CheckoutForm()
        return render(request, 'core/checkout_address.html',{'form':form} )
    
def payment(request):
    
    try:
        order = Order.objects.get(user=request.user,ordered=False)
        address = CheckoutAddress.objects.get(user=request.user)
        order_amount = order.get_total_price()
        razorpay_amount = int(order_amount * Decimal(100))
        order_currency = "INR"
        order_receipt = order.order_id
        notes = {
            "street_address": address.street_address,
            "apartment_address": address.apartment_address,
            "country": address.country.name,
            "zip": address.zip_code,
        }
        razorpay_order = razorpay_client.order.create(
            dict(
                amount = int(order.get_total_price() * 100),
                currency = order_currency,
                receipt = order_receipt,
                notes = notes,
                payment_capture = "0",
            )
        )
        print(razorpay_order["id"])
        order.razorpay_order_id = razorpay_order["id"]
        order.save()
        print("It should render to summary page")
        
        return render(
            request,
            "core/paymentsummaryrazorpay.html",
            # "invoice/invoice.html",
            {
                "order": order,
                "order_id": razorpay_order["id"],
                "orderId": order.order_id,
                "final_price": order_amount,
                "razorpay_merchant_id": settings.RAZORPAY_ID,
                "razorpay_amount": razorpay_amount, 
            }
        )
    except Order.DoesNotExist:
        print("Order Not Found")
        return HttpResponse("404 Error")

# def handlerequest(request):
#     if request.method == "POST":
#         try:
#             payment_id = request.POST.get("razorpay_payment_id", "")
#             order_id = request.POST.get("razorpay_order_id", "")
#             signature = request.POST.get("razorpay_signature", "")
#             print(payment_id, order_id, signature)

#             params_dict = {
#                 "razorpay_order_id": order_id,
#                 "razorpay_payment_id": payment_id,
#                 "razorpay_signature": signature,
#             }

#             try:
#                 order_db = Order.objects.get(razorpay_order_id=order_id)
#                 print("Order Found")
#             except:
#                 print("Order Not Found")
#                 return HttpResponse("505 Not Found")

#             order_db.razorpay_payment_id = payment_id
#             order_db.razorpay_signature = signature
#             order_db.save()

#             print("Working............")
#             result = razorpay_client.utility.verify_payment_signature(params_dict)

#             if result is None:
#                 print("Working Final Fine............")
#                 amount = int(order_db.get_total_price() * 100)
#                 #amount = amount * 100 

#                 payment_status = razorpay_client.payment.capture(payment_id, amount)

#                 if payment_status is not None:
#                     print(payment_status)
#                     order_db.ordered = True
#                     order_db.save()
#                     print("Payment Success")
#                     checkout_address = CheckoutAddress.objects.get(user=request.user)

#                     request.session["order_complete"] = (
#                         "Your Order is Successfully Placed, You will receive your order within 5 days!"
#                     )
#                     return render(request, "invoice/invoice.html",{"order":order_db,"payment_status":payment_status,"CheckoutAddress":checkout_address})
#                 else:
#                     print("Payment Failed")
#                     order_db.ordered = False
#                     order_db.save()
#                     request.session["order_failed"] = (
#                         "Unfortunately your order could not be placed, try again!"
#                     )
#                     return redirect("/")
#             else:
#                 order_db.ordered = False
#                 order_db.save()
#                 print("Signature verification failed")
#                 return render(request, "core/paymentfailed.html")

#         except Exception as e:
#             print(f"Exception occurred: {e}")
#             return HttpResponse("Error Occurred")
@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            # Get payment info from Razorpay POST
            payment_id = request.POST.get("razorpay_payment_id", "")
            order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            print("POST Received:", payment_id, order_id, signature)

            # Match with DB order
            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
            except Order.DoesNotExist:
                return HttpResponseNotFound("Order Not Found")

            # Save payment details
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()

            # Verify signature
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                print("Signature mismatch.")
                order_db.ordered = False
                order_db.save()
                return render(request, "core/paymentfailed.html")

            # Capture payment
            amount = int(order_db.get_total_price() * 100)
            payment_status = razorpay_client.payment.capture(payment_id, amount)

            if payment_status:
                order_db.ordered = True
                order_db.save()

                for item in order_db.items.all():
                    item.ordered = True
                    item.save()

                checkout_address = CheckoutAddress.objects.filter(user=request.user).first()
                request.session["order_complete"] = "Your order has been placed successfully."

                return render(request, "core/invoice/invoice.html", {
                    "order": order_db,
                    "payment_status": payment_status,
                    "CheckoutAddress": checkout_address
                })
            else:
                order_db.ordered = False
                order_db.save()
                return render(request, "core/paymentfailed.html")

        except Exception as e:
            print("Exception occurred:", e)
            return HttpResponse("An error occurred during payment.")
    else:
        return HttpResponse("Invalid request method.")


def invoice(request):
    # return render(request,"core/invoice/invoice.html") 
    try:
        order = Order.objects.filter(user=request.user, ordered=True).last()
        checkout_address = CheckoutAddress.objects.filter(user=request.user).first()
    except Exception:
        order = None
        checkout_address = None

    return render(request, "core/invoice/invoice.html", {
        "order": order,
        "CheckoutAddress": checkout_address,
    })

def shop_view(request):
    products = Product.objects.all()  
    return render(request, 'core/shop.html', {'products': products})
                



