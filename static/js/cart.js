const updateButtonOfCart = document.getElementsByClassName('update-cart')
for(let i = 0; i < updateButtonOfCart.length; i++ ){
    updateButtonOfCart[i].addEventListener('click', function(){
        const productId = this.dataset.product
        const action = this.dataset.action
        console.log(productId, action)
        console.log(user)
        if(user === 'AnonymousUser'){
            addCookieItem(productId, action)
        }
        else{
            updateUserOrder(productId, action)
        }
    })
}



const addCookieItem = (productId, action)=>{
    if(action === 'add'){
        if(cart[productId] === undefined){
            cart[productId] = {'quantity':1}
        }
        else{
            cart[productId]['quantity'] += 1
        }
    }

    if(action === 'remove'){
        cart[productId]['quantity'] -= 1
        if(cart[productId]['quantity'] <= 0){
            delete cart[productId]
        }
    }
    console.log(cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + "; domain=;path=/"
    location.reload()
}




const updateUserOrder = (productId, action)=>{
    // console.log('sending data...')
    const url = '/update_item/'
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({
            productId,
            action
        })
    })
    .then((response)=>{
        return response.json()
    })
    .then((data)=>{
        console.log('data:',data)
        location.reload()
    })
}