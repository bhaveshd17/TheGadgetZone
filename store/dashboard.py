from store.figures import get_bar, get_plot, get_pie
from store.models import Customer, OrderItem, Order, Category
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
    x = []
    for item in orderItem:
        if item.date.date() not in x:
            x.append(item.date.date())

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

    total_payment = sum(transaction)
    profit = (len(orderItem)*60)//100

    categories = Category.objects.all()
    cat_list = []
    for category in categories:
        cat_list.append(category.category)


    category_wise_quantity =[]

    for keyL in cat_list:
        cat_sort = []
        for ordr in orderItem:
            if ordr.product.category.category == keyL:
                cat_sort.append(ordr.product.category.category)

        category_wise_quantity .append(len(cat_sort))


    pie_chart = get_pie(category_wise_quantity, cat_list)

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
        'total_payment':total_payment,
        'profit':profit,
        'pie_chart':pie_chart,

    }