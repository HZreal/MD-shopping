let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
    },
    methods: {
        oper_btn_click(order_id, order_status){
            //点击待支付的请求
            if(order_status == '1'){
                let url = '/payment/' + order_id + '/';
                axios.get(url, {
                    responseType: 'json',
                }).then((response) => {
                    if(response.data.code == '0'){
                        location.href = response.data.alipay_url;
                    }
                    else if (response.data.code == '4001'){
                        location.href = '/login/?next=/orders/info/1/';
                    }
                    else {
                        console.log(response.data)
                        alert(response.data.errmsg)
                    }
                }).catch((error) => {
                    console.log(error)
                })

            }

            //点击待评价的请求
            if(order_status == '4'){
                let url = '/orders/comment/?order_id=' + order_id;
                axios.get(url, {
                    responseType: 'json',
                }).then((response) => {
                    console.log(response.data)
                }).catch((error) => {
                    console.log(error)
                })
            }
        }
    }

})