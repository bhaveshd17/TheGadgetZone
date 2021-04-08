import datetime

import matplotlib.pyplot as plt
import base64
from io import BytesIO

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_bar(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(12, 5))
    plt.title('Orders Analysis')
    plt.bar(x, y)
    plt.xlim(datetime.date(2021, 4, 1), datetime.date.today())
    plt.ylim(0, 50)
    plt.tight_layout()
    graph = get_graph()
    return graph

def get_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(12, 5))
    plt.title('Daily Transactions')
    plt.bar(x, y, 'r-',lw=1, label="transaction")
    plt.xlim(datetime.date(2021, 4, 1), datetime.date.today())
    plt.ylim(0, 500000)
    plt.tight_layout()
    graph = get_graph()
    return graph