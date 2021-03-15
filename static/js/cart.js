const updateButtonOfCart = document.getElementsByClassName('update-cart')
for(let i = 0; i < updateButtonOfCart.length; i++ ){
    updateButtonOfCart[i].addEventListener('click', function(){
        const productId = this.dataset.product
        const action = this.dataset.action
        console.log(productId, action)
        if(user === 'AnonymousUser'){
            console.log('not logged in')
        }
        else{
            updateUserOrder(productId, action)
        }
    })
}

const updateUserOrder = (productId, action)=>{
    console.log('sending data...')
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