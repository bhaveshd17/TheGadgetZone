from store.figures import get_bar, get_plot
from store.models import Customer, OrderItem, Order
from store.utils import cartData


def dashboardContent(request):
    data = cartData(request)
    cartItems = data['cartItems']
    customers = Customer.objects.all()
    orderItem = OrderItem.objects.all().order_by("-date")

    if len(orderItem) >= 5:
        orderItems = [orderItem[i] for i in range(0, 5)]
    else:
        orderItems = [orderItem[i] for i in range(0, len(orderItem))]
    if len(customers) >= 6:
        customers = [customers[i] for i in range(1, 6)]
    else:
        customers = [customers[i] for i in range(1, len(customers))]


    delivered = orderItem.filter(status='Delivered').count()
    pending = orderItem.filter(status='Pending').count()
    shipping = orderItem.filter(status='Shipping').count()
    accepted = orderItem.filter(status='Accepted').count()

    # for order analysis
    x = list(set([x.date.date() for x in orderItem ]))
    y = []
    for i in x:
        a = [y.order for y in orderItem if y.date.date() == i]
        y.append(len(a))
    orderChart = get_bar(x, y)

    # for transaction
    transaction = []
    for i in x:
        a = [float(y.product.discountPrice) for y in orderItem if y.date.date() == i]
        transaction.append(sum(a))
    transactionChart = get_plot(x, transaction)
    return {
        'cartItems': cartItems,
        'customers': customers,
        'orderItems': orderItems,
        'total_order': orderItem.count(),
        'delivered': delivered,
        'pending': pending,
        'accepted': accepted,
        'shipping': shipping,
        'chart':orderChart,
        'tchart':transactionChart,

    }